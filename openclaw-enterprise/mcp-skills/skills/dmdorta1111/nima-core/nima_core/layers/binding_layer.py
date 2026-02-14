#!/usr/bin/env python3
"""
VSA Binding Layer — NIMA Layer 2
=================================
Compositional binding using Vector Symbolic Architecture.

Key insight from research: "Phase ≈ Convolution" — neural synchrony and
VSA binding are mathematically equivalent operations.

Based on research:
- Plate's Holographic Reduced Representations (1995)
- Kanerva's Hyperdimensional Computing

Author: NIMA Project
Date: 2026
"""

import threading
import numpy as np
from collections import OrderedDict
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from ..config import ZERO_NORM_THRESHOLD


class BindingOperation(Enum):
    """Available binding operations."""
    CIRCULAR_CONVOLUTION = "conv"    # Plate's HRR (default)
    HADAMARD = "hadamard"            # Element-wise multiply
    PERMUTATION = "perm"             # Shift-based binding
    XOR = "xor"                      # For binary VSA


@dataclass
class BoundEpisode:
    """A bound episode representation."""
    vector: np.ndarray              # The bound VSA vector
    bindings: Dict[str, str]        # role → filler pairs
    affect: Optional[Dict] = None   # Affective annotation
    timestamp: str = ""
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            'bindings': self.bindings,
            'affect': self.affect,
            'timestamp': self.timestamp,
            'confidence': self.confidence,
            'vector_norm': float(np.linalg.norm(self.vector)),
        }


class VSABindingLayer:
    """
    Layer 2: Compositional binding operations.
    
    Implements:
    - Role-filler binding (WHO did WHAT WHERE WHEN)
    - Episode superposition (bundling multiple bindings)
    - Similarity-based retrieval
    - Unbinding (querying with partial info)
    """
    
    # Standard semantic roles
    ROLES = ['WHO', 'WHAT', 'WHERE', 'WHEN', 'WHY', 'HOW', 'AFFECT']
    
    def __init__(self, dimension: int = 10000, 
                 operation: BindingOperation = BindingOperation.CIRCULAR_CONVOLUTION,
                 seed: int = 42):
        """
        Initialize binding layer.
        
        Args:
            dimension: VSA vector dimension
            operation: Which binding operation to use
            seed: Random seed for reproducibility
        """
        self.dimension = dimension
        self.operation = operation
        self.rng = np.random.default_rng(seed)
        
        # Threading lock for mutable state
        self._lock = threading.RLock()
        
        # Role vectors (fixed, orthogonal-ish)
        self._init_role_vectors()
        
        # Filler cache (text → vector, true LRU via OrderedDict)
        self.filler_cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self.max_cache = 10000
    
    def _init_role_vectors(self):
        """Create role vectors that are approximately orthogonal."""
        with self._lock:
            self.role_vectors = {}
            
            for role in self.ROLES:
                # Use hash-based seeding for deterministic vectors
                seed = int(hashlib.md5(role.encode()).hexdigest()[:8], 16)
                rng = np.random.default_rng(seed)
                vec = rng.standard_normal(self.dimension)
                vec = vec / np.linalg.norm(vec)
                self.role_vectors[role] = vec
            
            # Also create inverse roles for unbinding
            self.role_inverses = {}
            for role, vec in self.role_vectors.items():
                self.role_inverses[role] = self._inverse(vec)
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """Convert text to a VSA vector."""
        with self._lock:
            if text in self.filler_cache:
                self.filler_cache.move_to_end(text)  # True LRU: mark as recently used
                return self.filler_cache[text]
            
            # Hash-based deterministic encoding
            seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
            rng = np.random.default_rng(seed)
            vec = rng.standard_normal(self.dimension)
            vec = vec / np.linalg.norm(vec)
            
            # Cache management with LRU eviction
            if len(self.filler_cache) >= self.max_cache:
                self.filler_cache.popitem(last=False)  # Evict least recently used
            
            self.filler_cache[text] = vec
            
            return vec
    
    def bind(self, role: str, filler: Union[str, np.ndarray]) -> np.ndarray:
        """
        Bind a role to a filler.
        
        Args:
            role: Semantic role (WHO, WHAT, etc.)
            filler: Text or vector to bind
        
        Returns:
            Bound vector
        """
        with self._lock:
            role_vec = self.role_vectors.get(role.upper())
            if role_vec is None:
                # Create ad-hoc role vector
                role_vec = self._text_to_vector(f"ROLE_{role.upper()}")
                self.role_vectors[role.upper()] = role_vec
                self.role_inverses[role.upper()] = self._inverse(role_vec)
            
            if isinstance(filler, str):
                filler_vec = self._text_to_vector(filler)
            else:
                filler_vec = filler
            
            return self._bind_op(role_vec, filler_vec)
    
    def unbind(self, bound: np.ndarray, role: str) -> np.ndarray:
        """
        Unbind to retrieve filler from role.
        
        Args:
            bound: Bound or bundled vector
            role: Role to query
        
        Returns:
            Approximate filler vector (use similarity to identify)
        """
        role_inverse = self.role_inverses.get(role.upper())
        if role_inverse is None:
            raise ValueError(f"Unknown role: {role}")
        
        return self._bind_op(role_inverse, bound)
    
    def bundle(self, vectors: List[np.ndarray], 
               weights: Optional[List[float]] = None) -> np.ndarray:
        """
        Bundle multiple vectors into a superposition.
        
        Args:
            vectors: List of vectors to bundle
            weights: Optional importance weights
        
        Returns:
            Bundled vector (normalized)
        """
        if not vectors:
            return np.zeros(self.dimension)
        
        if weights is None:
            weights = [1.0] * len(vectors)
        
        # Weighted sum
        result = np.zeros(self.dimension)
        for vec, w in zip(vectors, weights):
            result += w * vec
        
        # Normalize
        norm = np.linalg.norm(result)
        if norm > 0:
            result = result / norm
        
        return result
    
    def create_episode(self, bindings: Dict[str, str],
                       affect: Optional[Dict] = None) -> BoundEpisode:
        """
        Create a bound episode from role-filler pairs.
        
        Args:
            bindings: Dict mapping roles to fillers (text)
            affect: Optional affective annotation
        
        Returns:
            BoundEpisode with composed vector
        """
        bound_pairs = []
        
        for role, filler in bindings.items():
            bound = self.bind(role, filler)
            bound_pairs.append(bound)
        
        # Add affect if provided
        if affect and 'vector' in affect:
            affect_bound = self.bind('AFFECT', affect['vector'])
            bound_pairs.append(affect_bound)
        
        # Bundle all bindings
        episode_vector = self.bundle(bound_pairs)
        
        return BoundEpisode(
            vector=episode_vector,
            bindings=bindings,
            affect=affect,
            timestamp=str(np.datetime64('now')),
            confidence=1.0,
        )
    
    def query_role(self, episode: BoundEpisode, role: str) -> Tuple[np.ndarray, float]:
        """
        Query an episode for a specific role.
        
        Returns:
            (recovered_vector, confidence)
        """
        recovered = self.unbind(episode.vector, role)
        
        # If we know the original filler, compute confidence
        if role.upper() in episode.bindings:
            original = self._text_to_vector(episode.bindings[role.upper()])
            confidence = float(np.dot(recovered, original))
        else:
            confidence = 0.5  # Unknown
        
        return recovered, confidence
    
    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        # Guard against zero vectors
        if norm_a < ZERO_NORM_THRESHOLD or norm_b < ZERO_NORM_THRESHOLD:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b + ZERO_NORM_THRESHOLD))
    
    def find_nearest(self, query: np.ndarray, 
                     candidates: List[str],
                     top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find nearest candidates to a query vector.
        
        Args:
            query: Query vector
            candidates: List of text candidates
            top_k: Number of results
        
        Returns:
            List of (text, similarity) pairs
        """
        results = []
        
        for text in candidates:
            vec = self._text_to_vector(text)
            sim = self.similarity(query, vec)
            results.append((text, sim))
        
        results.sort(key=lambda x: -x[1])
        return results[:top_k]
    
    def _bind_op(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Apply binding operation."""
        if self.operation == BindingOperation.CIRCULAR_CONVOLUTION:
            return self._circular_convolution(a, b)
        elif self.operation == BindingOperation.HADAMARD:
            return a * b
        elif self.operation == BindingOperation.PERMUTATION:
            return self._permutation_bind(a, b)
        else:
            raise ValueError(f"Unknown operation: {self.operation}")
    
    def _circular_convolution(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Circular convolution (Plate's HRR binding).
        
        Uses FFT for O(n log n) complexity.
        Normalizes result to prevent unbounded growth.
        """
        result = np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))
        # Normalize to prevent explosion over multiple operations
        norm = np.linalg.norm(result)
        if norm > 1e-10:
            result = result / norm
        return result
    
    def _inverse(self, vec: np.ndarray) -> np.ndarray:
        """
        Compute approximate inverse for unbinding.
        
        For circular convolution: inv(x)[k] = x[-k]
        """
        if self.operation == BindingOperation.CIRCULAR_CONVOLUTION:
            return np.flip(vec)
        elif self.operation == BindingOperation.HADAMARD:
            # For Hadamard, inverse is same as original (x * x = 1 for normalized)
            return vec
        elif self.operation == BindingOperation.PERMUTATION:
            # Inverse permutation
            return np.roll(vec, -1)
        else:
            return vec
    
    def _permutation_bind(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Permutation-based binding (shift + multiply)."""
        shifted = np.roll(a, 1)
        return shifted * b
    
    def encode_sequence(self, items: List[str]) -> np.ndarray:
        """
        Encode a sequence using positional binding.
        
        Uses position vectors to preserve order.
        """
        if not items:
            return np.zeros(self.dimension)
        
        bound_items = []
        
        for i, item in enumerate(items):
            # Create position vector
            pos_vec = self._text_to_vector(f"POS_{i}")
            item_vec = self._text_to_vector(item)
            
            # Bind item to position
            bound = self._bind_op(pos_vec, item_vec)
            bound_items.append(bound)
        
        return self.bundle(bound_items)
    
    def cleanup(self, noisy: np.ndarray, 
                codebook: List[np.ndarray],
                threshold: float = 0.3) -> Optional[np.ndarray]:
        """
        Clean up a noisy vector by finding best match in codebook.
        
        Args:
            noisy: Noisy/superposed vector
            codebook: Clean prototype vectors
            threshold: Minimum similarity threshold
        
        Returns:
            Best matching clean vector, or None if below threshold
        """
        if not codebook:
            return None
        
        best_sim = -1
        best_vec = None
        
        for clean in codebook:
            sim = self.similarity(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_vec = clean
        
        if best_sim >= threshold:
            return best_vec
        return None
    
    def get_stats(self) -> Dict:
        """Get binding layer statistics."""
        return {
            'dimension': self.dimension,
            'operation': self.operation.value,
            'roles': list(self.role_vectors.keys()),
            'filler_cache_size': len(self.filler_cache),
        }


# Quick test
if __name__ == "__main__":
    print("Testing VSABindingLayer...")
    
    layer = VSABindingLayer(dimension=1000)
    
    # Create an episode
    bindings = {
        'WHO': 'Alice',
        'WHAT': 'asked about NIMA v2',
        'WHERE': 'chat',
        'WHEN': 'morning',
    }
    
    episode = layer.create_episode(bindings)
    print(f"\n✅ Created episode: {episode.bindings}")
    print(f"   Vector norm: {np.linalg.norm(episode.vector):.4f}")
    
    # Query role
    recovered, conf = layer.query_role(episode, 'WHO')
    print(f"\n   Query WHO:")
    
    # Find nearest match
    candidates = ['Alice', 'Bob', 'Agent', 'System']
    matches = layer.find_nearest(recovered, candidates)
    print(f"   Best match: {matches[0][0]} ({matches[0][1]:.3f})")
    
    # Test sequence encoding
    sequence = ['first', 'second', 'third']
    seq_vec = layer.encode_sequence(sequence)
    print(f"\n   Sequence encoded: norm = {np.linalg.norm(seq_vec):.4f}")
    
    print("\n✅ Binding layer working!")
