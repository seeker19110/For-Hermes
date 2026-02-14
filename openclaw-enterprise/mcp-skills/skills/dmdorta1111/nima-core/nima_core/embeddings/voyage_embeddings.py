"""
Voyage AI Embeddings
====================
High-quality embeddings (1024D) with learned projection to 50KD.
Preferred over MiniLM when VOYAGE_API_KEY is available.

Author: NIMA Project
"""

import os
import numpy as np
from typing import List, Optional
import threading

_voyage_embedder = None
_voyage_lock = threading.Lock()


class VoyageEmbedder:
    """
    Voyage AI embedder with learned projection.
    
    1024D → 50KD projection for sparse retrieval.
    """
    
    def __init__(self, api_key: str = None, enable_projection: bool = True, lazy: bool = False):
        self.api_key = api_key or os.environ.get("VOYAGE_API_KEY")
        self.model = "voyage-4-lite"
        self.dimension = 1024
        self._loaded = False
        self._client = None
        self._lazy = lazy
        
        # Projection
        self.enable_projection = enable_projection
        self.projection_matrix = None
        self._projection_loaded = False
        self._projected_dim = 50000
        
        # Paths
        from ..config import NIMA_MODELS_DIR
        self._projection_path = NIMA_MODELS_DIR / "learned_projection.pt"
        
        # Load immediately unless lazy
        if not lazy:
            self._ensure_loaded()
    
    def _ensure_loaded(self):
        """Load Voyage client."""
        if self._loaded:
            return
            
        if not self.api_key:
            raise ValueError("VOYAGE_API_KEY not set")
            
        try:
            import voyageai
            self._client = voyageai.Client(api_key=self.api_key)
            self._loaded = True
            print(f"🚀 Voyage AI embeddings ready (model={self.model}, dim={self.dimension})")
            
            if self.enable_projection:
                self._load_projection()
                
        except ImportError:
            raise ImportError("voyageai not installed. Run: pip install voyageai")
        except Exception as e:
            raise RuntimeError(f"Voyage init failed: {e}")
    
    def _load_projection(self):
        """Load the learned projection matrix."""
        if self._projection_loaded:
            return
            
        if not self._projection_path.exists():
            print(f"⚠️ Projection not found: {self._projection_path}")
            print("   Running without projection (raw 1024D embeddings)")
            self.enable_projection = False
            return
            
        try:
            from ..utils import safe_torch_load
            import torch
            
            checkpoint = safe_torch_load(self._projection_path)
            
            # Check projection source dimension matches
            state_dict = checkpoint.get("model_state_dict", checkpoint)
            W = state_dict.get("W.weight", state_dict.get("weight"))
            
            if W is None:
                print("⚠️ Invalid projection format")
                self.enable_projection = False
                return
            
            # Verify dimension
            if W.shape[1] != self.dimension:
                print(f"⚠️ Projection dimension mismatch: {W.shape[1]} vs {self.dimension}")
                print("   Running without projection")
                self.enable_projection = False
                return
            
            self.projection_matrix = W.numpy() if hasattr(W, 'numpy') else W
            self._projected_dim = self.projection_matrix.shape[0]
            self._projection_loaded = True
            
            print(f"🎯 Voyage projection loaded: {self.dimension} → {self._projected_dim}D")
            
        except Exception as e:
            print(f"⚠️ Failed to load projection: {e}")
            self.enable_projection = False
    
    def encode(self, texts: List[str], apply_projection: bool = True) -> Optional[np.ndarray]:
        """Encode texts using Voyage AI."""
        self._ensure_loaded()
        
        if not texts:
            return None
            
        try:
            # Voyage API call
            result = self._client.embed(texts, model=self.model)
            embeddings = np.array(result.embeddings, dtype=np.float32)
            
            # Apply projection if enabled
            if apply_projection and self.enable_projection and self.projection_matrix is not None:
                embeddings = self._apply_projection(embeddings)
            
            return embeddings
            
        except Exception as e:
            print(f"⚠️ Voyage encoding failed: {e}")
            return None
    
    def encode_single(self, text: str, apply_projection: bool = True) -> Optional[np.ndarray]:
        """Encode single text."""
        result = self.encode([text], apply_projection=apply_projection)
        return result[0] if result is not None else None
    
    def _apply_projection(self, embeddings: np.ndarray) -> np.ndarray:
        """Apply learned projection W: (N, 1024) @ (1024, 50K).T → (N, 50K)."""
        if self.projection_matrix is None:
            return embeddings
            
        # Matrix multiplication: (N, 1024) @ (1024, 50K) → (N, 50K)
        projected = embeddings @ self.projection_matrix.T
        
        # Sparsify: keep only top-k% values
        k = 0.1  # Keep top 10%
        threshold = np.percentile(np.abs(projected), (1 - k) * 100, axis=1, keepdims=True)
        projected = np.where(np.abs(projected) >= threshold, projected, 0)
        
        # Normalize
        norms = np.linalg.norm(projected, axis=1, keepdims=True)
        projected = np.where(norms > 0, projected / norms, 0)
        
        return projected.astype(np.float32)
    
    def load(self) -> bool:
        """Explicitly load the Voyage client."""
        self._ensure_loaded()
        return self._loaded
    
    def unload(self) -> None:
        """Unload client and projection to free memory."""
        if self._client is not None:
            del self._client
            self._client = None
        if self.projection_matrix is not None:
            del self.projection_matrix
            self.projection_matrix = None
        self._loaded = False
        self._projection_loaded = False
        import gc
        gc.collect()
        print("🧹 Voyage embedder unloaded")
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    @property
    def memory_usage_mb(self) -> float:
        """Estimate current memory usage in MB."""
        usage = 0.0
        if self.projection_matrix is not None:
            usage += self.projection_matrix.nbytes / 1024 / 1024
        return usage
    
    @property
    def is_projected(self) -> bool:
        """Check if projection is active."""
        return self._projection_loaded and self.enable_projection
    
    @property
    def output_dimension(self) -> int:
        """Get output dimension (50K if projected, 1024 raw)."""
        if self.is_projected and self.projection_matrix is not None:
            return self._projected_dim
        return self.dimension
    
    def encode_raw(self, texts: List[str]) -> Optional[np.ndarray]:
        """Encode WITHOUT projection (raw 1024D)."""
        return self.encode(texts, apply_projection=False)


def get_voyage_embedder(api_key: str = None, enable_projection: bool = True, lazy: bool = False) -> VoyageEmbedder:
    """Get Voyage embedder singleton."""
    global _voyage_embedder
    
    if _voyage_embedder is None:
        with _voyage_lock:
            if _voyage_embedder is None:
                _voyage_embedder = VoyageEmbedder(api_key, enable_projection, lazy=lazy)
    
    return _voyage_embedder
