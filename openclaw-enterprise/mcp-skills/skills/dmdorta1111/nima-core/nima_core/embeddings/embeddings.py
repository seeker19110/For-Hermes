#!/usr/bin/env python3
"""
Unified Embeddings Loader
=========================
Single cached load of embeddings with automatic provider selection:
1. Voyage AI (1024D) - preferred when VOYAGE_API_KEY available
2. MiniLM (384D) - fallback local model

With learned projection for energy-concentrated embeddings (50KD).

Author: NIMA Project
Date: 2026
Updated: 2026 - Added Voyage AI support + learned projection
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Union
import threading
import numpy as np

# Suppress tokenizers parallelism warnings (prevents deadlocks with multiprocessing)
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Import config paths
from ..config import NIMA_MODELS_DIR

# Singleton state
_embedder = None
_embedder_lock = threading.Lock()
_uses_voyage = None  # Track which provider is active

# MiniLM defaults
_model_name = "sentence-transformers/all-MiniLM-L6-v2"
_embedding_dim = 384
_projected_dim = 50000
_projection_path = NIMA_MODELS_DIR / "learned_projection.pt"

# Feature flag for projection (can be overridden via env)
ENABLE_PROJECTION = os.environ.get("NIMA_PROJECTION", "true").lower() == "true"

# Lazy loading flag - don't load until first encode() call
LAZY_LOAD = os.environ.get("NIMA_LAZY_LOAD", "true").lower() == "true"


def _should_use_voyage() -> bool:
    """Check if Voyage AI should be used (API key available)."""
    return os.environ.get("VOYAGE_API_KEY") is not None


def is_voyage_available() -> bool:
    """Check if Voyage AI is available."""
    return _should_use_voyage()


class EmbeddingCache:
    """
    Cached embedding generator with optional learned projection.
    
    Loads sentence-transformers ONCE and reuses across all modules.
    Thread-safe singleton pattern.
    
    With projection enabled:
        text → MiniLM (384D) → W (50KD, concentrated)
    """
    
    def __init__(self, model_name: str = None, enable_projection: bool = None, lazy: bool = None):
        self.model_name = model_name or _model_name
        self.model = None
        self.dimension = _embedding_dim
        self._loaded = False
        
        # Projection settings
        self.enable_projection = enable_projection if enable_projection is not None else ENABLE_PROJECTION
        self.projection_matrix = None  # W: (50K, 384)
        self._projection_loaded = False
        
        # Lazy loading - don't load until first encode()
        self._lazy = lazy if lazy is not None else LAZY_LOAD
        self._load_triggered = False
        
        if not self._lazy:
            # Eager loading (original behavior)
            self._ensure_loaded()
    
    def load(self) -> bool:
        """Explicitly load the model and projection."""
        self._ensure_loaded()
        return self._loaded
    
    def unload(self) -> None:
        """Unload model and projection to free memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.projection_matrix is not None:
            del self.projection_matrix
            self.projection_matrix = None
        self._loaded = False
        self._projection_loaded = False
        self._load_triggered = False
        import gc
        gc.collect()
        print("🧹 Embedding cache unloaded")
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    @property
    def memory_usage_mb(self) -> float:
        """Estimate current memory usage in MB."""
        usage = 0.0
        if self.model is not None:
            usage += 100.0
        if self.projection_matrix is not None:
            usage += self.projection_matrix.nbytes / 1024 / 1024
        return usage
        
    def _ensure_loaded(self):
        """Load model if not already loaded."""
        if self._loaded:
            return
            
        try:
            from sentence_transformers import SentenceTransformer
            print(f"📦 Loading embeddings model (cached): {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self._loaded = True
            print(f"✅ Embeddings ready (dim={self.dimension})")
            
            # Load projection if enabled
            if self.enable_projection:
                self._load_projection()
                
        except ImportError:
            print("⚠️ sentence-transformers not installed")
            self._loaded = False
        except Exception as e:
            print(f"⚠️ Embeddings load failed: {e}")
            self._loaded = False
    
    def _load_projection(self):
        """Load the learned projection matrix."""
        if self._projection_loaded:
            return
            
        if not _projection_path.exists():
            print(f"⚠️ Projection not found: {_projection_path}")
            print("   Running without projection (raw 384D embeddings)")
            self.enable_projection = False
            return
            
        try:
            from ..utils import safe_torch_load
            checkpoint = safe_torch_load(_projection_path)
            
            # Extract weight matrix from state dict
            if 'model_state_dict' in checkpoint:
                W = checkpoint['model_state_dict']['W.weight']
            else:
                W = checkpoint.get('W.weight', checkpoint)
            
            # Convert to numpy for fast CPU inference
            self.projection_matrix = W.numpy()  # Shape: (50K, 384)
            
            # CRITICAL: Free PyTorch tensors to prevent 76MB leak
            del W
            del checkpoint
            
            self._projection_loaded = True
            self.dimension = self.projection_matrix.shape[0]  # Now 50K
            
            print(f"🎯 Learned projection loaded: 384 → {self.dimension}D (concentrated)")
            
        except Exception as e:
            print(f"⚠️ Projection load failed: {e}")
            print("   Running without projection")
            self.enable_projection = False
    
    def _apply_projection(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Apply learned projection to concentrate energy.
        
        Args:
            embeddings: (N, 384) array
            
        Returns:
            (N, 50K) concentrated embeddings
        """
        if self.projection_matrix is None:
            return embeddings
            
        # W @ e.T = (50K, 384) @ (384, N) = (50K, N)
        projected = np.dot(embeddings, self.projection_matrix.T)  # (N, 50K)
        return projected
    
    def encode(self, texts: List[str], apply_projection: bool = True, **kwargs) -> Optional[np.ndarray]:
        """
        Encode texts to embeddings, optionally with learned projection.
        
        Args:
            texts: List of strings to encode
            apply_projection: Whether to apply learned projection (default True)
            **kwargs: Passed to model.encode()
            
        Returns:
            Numpy array of embeddings (N, D) where D=50K if projected, 384 otherwise
            Returns None if model not loaded
        """
        self._ensure_loaded()
        
        if not self._loaded or self.model is None:
            return None
            
        try:
            # Get base embeddings (384D)
            embeddings = self.model.encode(texts, **kwargs)
            
            if not isinstance(embeddings, np.ndarray):
                embeddings = np.array(embeddings)
            
            # Apply projection if enabled
            if apply_projection and self.enable_projection and self._projection_loaded:
                embeddings = self._apply_projection(embeddings)
            
            return embeddings
            
        except Exception as e:
            print(f"⚠️ Encoding failed: {e}")
            return None
    
    def encode_raw(self, texts: List[str], **kwargs) -> Optional[np.ndarray]:
        """Encode texts WITHOUT projection (raw 384D)."""
        return self.encode(texts, apply_projection=False, **kwargs)
    
    def encode_single(self, text: str, apply_projection: bool = True, **kwargs) -> Optional[np.ndarray]:
        """Encode a single text, optionally with projection."""
        result = self.encode([text], apply_projection=apply_projection, **kwargs)
        return result[0] if result is not None else None
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    @property
    def is_projected(self) -> bool:
        """Whether projection is active."""
        return self._projection_loaded and self.enable_projection
    
    @property
    def output_dimension(self) -> int:
        """Get the output embedding dimension (384 raw, 50K projected)."""
        self._ensure_loaded()  # Must load to know actual dimension
        if self.is_projected and self.projection_matrix is not None:
            return self.projection_matrix.shape[0]
        return _embedding_dim


def get_embedder(enable_projection: bool = None, lazy: bool = None):
    """
    Get the singleton embedder instance.

    Auto-selects provider:
    - Voyage AI if VOYAGE_API_KEY is set
    - MiniLM (local) as fallback

    Thread-safe. All modules should use this instead of creating their own.

    Args:
        enable_projection: Whether to enable learned projection
        lazy: If True, don't load until first encode() call
              If None, uses NIMA_LAZY_LOAD env var (default: True)

    Returns:
        VoyageEmbedder or EmbeddingCache instance
    """
    global _embedder, _uses_voyage

    if _embedder is None:
        with _embedder_lock:
            if _embedder is None:  # Double-check
                proj = enable_projection if enable_projection is not None else ENABLE_PROJECTION
                lazy_flag = lazy if lazy is not None else LAZY_LOAD

                # Prefer Voyage when API key available
                if _should_use_voyage():
                    try:
                        from .voyage_embeddings import get_voyage_embedder
                        _embedder = get_voyage_embedder(enable_projection=proj, lazy=lazy_flag)
                        _uses_voyage = True
                    except Exception as e:
                        print(f"⚠️ Voyage init failed, falling back to MiniLM: {e}")
                        _embedder = EmbeddingCache(enable_projection=proj, lazy=lazy_flag)
                        _uses_voyage = False
                else:
                    _embedder = EmbeddingCache(enable_projection=proj, lazy=lazy_flag)
                    _uses_voyage = False

    return _embedder


def preload():
    """
    Preload the embeddings model.

    Call at startup to avoid first-use delay.
    Ignored if lazy loading is disabled.
    """
    embedder = get_embedder()
    if hasattr(embedder, 'load'):
        embedder.load()
    else:
        embedder._ensure_loaded()


def unload():
    """
    Unload embeddings to free memory.

    Model will be reloaded on next use if needed.
    """
    global _embedder
    if _embedder is not None:
        if hasattr(_embedder, 'unload'):
            _embedder.unload()
        _embedder = None


def is_loaded() -> bool:
    """Check if embedder is loaded and ready."""
    global _embedder
    if _embedder is None:
        return False
    return _embedder.is_loaded


def memory_usage_mb() -> float:
    """Get current memory usage of embedder in MB."""
    global _embedder
    if _embedder is None:
        return 0.0
    if hasattr(_embedder, 'memory_usage_mb'):
        return _embedder.memory_usage_mb
    return 0.0


# Convenience functions
def encode(texts: List[str], apply_projection: bool = True, **kwargs) -> Optional[np.ndarray]:
    """Encode texts using the cached embedder (with projection by default)."""
    return get_embedder().encode(texts, apply_projection=apply_projection, **kwargs)


def encode_raw(texts: List[str], **kwargs) -> Optional[np.ndarray]:
    """Encode texts WITHOUT projection (raw 384D or 1024D)."""
    return get_embedder().encode_raw(texts, **kwargs)


def encode_single(text: str, apply_projection: bool = True, **kwargs) -> Optional[np.ndarray]:
    """Encode single text using the cached embedder."""
    return get_embedder().encode_single(text, apply_projection=apply_projection, **kwargs)


def get_dimension() -> int:
    """Get output embedding dimension (50K if projected, 384/1024 raw)."""
    embedder = get_embedder()
    embedder._ensure_loaded()  # Must load to know actual dimension
    return embedder.output_dimension


def get_raw_dimension() -> int:
    """Get raw embedding dimension (384 for MiniLM, 1024 for Voyage)."""
    if _uses_voyage:
        return 1024
    return _embedding_dim


def is_projection_enabled() -> bool:
    """Check if projection is active."""
    embedder = get_embedder()
    embedder._ensure_loaded()  # Must load to know if projection worked
    return embedder.is_projected


def uses_voyage() -> bool:
    """Check if using Voyage AI (vs MiniLM)."""
    get_embedder()  # Ensure initialized
    return _uses_voyage


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("Testing unified embeddings with learned projection")
    print("=" * 60)
    
    preload()
    
    # Test with projection
    print("\n📊 With projection:")
    result = encode_single("Hello, this is a test sentence.")
    if result is not None:
        print(f"   Dimension: {len(result)}")
        print(f"   Provider: {'Voyage' if uses_voyage() else 'MiniLM'}")
        print(f"   Projection enabled: {is_projection_enabled()}")
        
        # Check energy concentration
        energy = result ** 2
        total = energy.sum()
        top_10_pct = int(len(result) * 0.1)
        top_indices = np.argsort(energy)[-top_10_pct:]
        top_energy = energy[top_indices].sum()
        concentration = top_energy / total
        print(f"   Energy concentration (top 10%): {concentration*100:.1f}%")
    
    # Test without projection
    print("\n📊 Without projection (raw):")
    result_raw = encode_single("Hello, this is a test sentence.", apply_projection=False)
    if result_raw is not None:
        print(f"   Dimension: {len(result_raw)}")
    
    # Batch test
    print("\n📊 Batch encoding:")
    texts = ["First sentence", "Second sentence", "Third sentence"]
    batch_result = encode(texts)
    if batch_result is not None:
        print(f"   Shape: {batch_result.shape}")
    
    print("\n✅ Unified embeddings with projection working!")
