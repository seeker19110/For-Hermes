#!/usr/bin/env python3
"""
SparseBlockMemory
=================
Integration of sparse_block_vsa.py into NIMA episodic memory system.

Provides:
- Block-wise VSA: 100 blocks of 500D each, ~10% active
- 10x memory reduction vs dense 50KD vectors
- Block selection learning via resonator factors
- API-compatible drop-in replacement for existing VSA cache

Author: Lilu
Date: Feb 11, 2026
"""

import os
import sys
import json
import time
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict

import numpy as np
from scipy.signal import fftconvolve

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None

# Import sparse block VSA
try:
    from .sparse_block_vsa import SparseBlockHDVector
except ImportError:
    # Fallback for direct import
    from sparse_block_vsa import SparseBlockHDVector


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SparseBlockConfig:
    """Configuration for sparse block memory."""
    # Block structure
    block_dim: int = 500
    num_blocks: int = 100
    default_sparsity: float = 0.1  # 10% active blocks
    
    # Block selection learning
    enable_block_learning: bool = True
    block_selection_temperature: float = 0.5
    min_blocks_per_factor: int = 5
    max_blocks_per_factor: int = 30
    
    # Query optimization
    use_block_index: bool = True
    similarity_threshold: float = 0.3
    
    # Migration
    migrate_on_load: bool = True
    preserve_dense_backup: bool = True
    
    # Performance
    cache_similarities: bool = True
    max_cache_size: int = 10000
    
    @property
    def total_dim(self) -> int:
        return self.block_dim * self.num_blocks
    
    @property
    def active_blocks_per_vector(self) -> int:
        return int(self.default_sparsity * self.num_blocks)


# =============================================================================
# Block Selection Learning
# =============================================================================

class BlockSelectionLearner:
    """
    Learns which blocks to activate based on resonator factors.
    
    WHO/WHAT/TOPIC determine which blocks should be active,
    creating a content-addressable sparse index.
    """
    
    def __init__(self, config: SparseBlockConfig):
        self.config = config
        self.num_blocks = config.num_blocks
        
        # Factor -> block affinity scores
        # Higher score = more likely to activate this block
        self.factor_block_scores: Dict[str, np.ndarray] = {}
        
        # Usage statistics for adaptive learning
        self.factor_usage_count: Dict[str, int] = {}
        self.block_activation_count = np.zeros(self.num_blocks, dtype=np.int64)
        
        # Block index for fast lookup
        self.block_to_memories: Dict[int, Set[int]] = {i: set() for i in range(self.num_blocks)}
    
    def register_factor(self, factor: str, initial_blocks: Optional[Set[int]] = None):
        """Register a new resonator factor (WHO, WHAT, TOPIC, etc.)."""
        if factor not in self.factor_block_scores:
            # Initialize with small random scores
            scores = np.random.normal(0, 0.1, self.num_blocks)
            
            if initial_blocks:
                # Boost initial blocks
                for block_idx in initial_blocks:
                    scores[block_idx] = 1.0
            
            self.factor_block_scores[factor] = scores
            self.factor_usage_count[factor] = 0
    
    def select_blocks(self, factors: Dict[str, str], 
                      temperature: Optional[float] = None) -> Set[int]:
        """
        Select active blocks based on resonator factors.
        
        Args:
            factors: Dict mapping factor names to values (e.g., {"WHO": "David"})
            temperature: Softmax temperature (lower = more selective)
            
        Returns:
            Set of block indices to activate
        """
        if temperature is None:
            temperature = self.config.block_selection_temperature
        
        # Aggregate scores across all factors
        combined_scores = np.zeros(self.num_blocks)
        
        for factor_name, factor_value in factors.items():
            # Create composite key
            factor_key = f"{factor_name}:{factor_value}"
            
            if factor_key not in self.factor_block_scores:
                self.register_factor(factor_key)
            
            # Weight by usage (more used = more reliable)
            weight = np.log1p(self.factor_usage_count.get(factor_key, 0)) + 1.0
            combined_scores += self.factor_block_scores[factor_key] * weight
        
        # Apply softmax to get selection probabilities
        if temperature > 0:
            exp_scores = np.exp(combined_scores / temperature)
            probs = exp_scores / (np.sum(exp_scores) + 1e-10)
        else:
            # Hard max selection
            probs = np.zeros_like(combined_scores)
            top_k = self.config.min_blocks_per_factor
            top_indices = np.argsort(combined_scores)[-top_k:]
            probs[top_indices] = 1.0 / top_k
        
        # Sample blocks based on probabilities
        num_to_select = min(
            max(self.config.min_blocks_per_factor, int(self.config.default_sparsity * self.num_blocks)),
            self.config.max_blocks_per_factor
        )
        
        selected = set()
        if np.sum(probs) > 0:
            # Weighted random selection without replacement
            block_indices = np.arange(self.num_blocks)
            selected_array = np.random.choice(
                block_indices, 
                size=min(num_to_select, self.num_blocks),
                replace=False,
                p=probs
            )
            selected = set(selected_array.tolist())
        
        return selected
    
    def update_from_query(self, factors: Dict[str, str], 
                          relevant_memory_ids: List[int],
                          irrelevant_memory_ids: List[int]):
        """
        Update block selection based on query results.
        
        Reinforce blocks that led to relevant memories,
        reduce weight on blocks that led to irrelevant ones.
        """
        learning_rate = 0.01
        
        for factor_name, factor_value in factors.items():
            factor_key = f"{factor_name}:{factor_value}"
            
            if factor_key not in self.factor_block_scores:
                continue
            
            scores = self.factor_block_scores[factor_key]
            
            # Positive reinforcement: blocks in relevant memories
            for mem_id in relevant_memory_ids[:10]:  # Top 10
                for block_idx in self.block_to_memories:
                    if mem_id in self.block_to_memories[block_idx]:
                        scores[block_idx] += learning_rate
            
            # Negative reinforcement: blocks in irrelevant memories
            for mem_id in irrelevant_memory_ids[:10]:
                for block_idx in self.block_to_memories:
                    if mem_id in self.block_to_memories[block_idx]:
                        scores[block_idx] -= learning_rate * 0.5
            
            # Clip scores
            scores = np.clip(scores, -5, 5)
            self.factor_block_scores[factor_key] = scores
            
            self.factor_usage_count[factor_key] = self.factor_usage_count.get(factor_key, 0) + 1
    
    def index_memory(self, memory_id: int, active_blocks: Set[int]):
        """Add memory to block index."""
        for block_idx in active_blocks:
            self.block_to_memories[block_idx].add(memory_id)
            self.block_activation_count[block_idx] += 1
    
    def get_candidate_memories(self, active_blocks: Set[int]) -> Set[int]:
        """Get memory candidates that share at least one active block."""
        candidates = set()
        for block_idx in active_blocks:
            candidates.update(self.block_to_memories[block_idx])
        return candidates
    
    def get_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            "factors_learned": len(self.factor_block_scores),
            "block_activation_distribution": {
                "mean": float(np.mean(self.block_activation_count)),
                "std": float(np.std(self.block_activation_count)),
                "min": int(np.min(self.block_activation_count)),
                "max": int(np.max(self.block_activation_count)),
            },
            "most_used_blocks": np.argsort(self.block_activation_count)[-10:].tolist(),
            "least_used_blocks": np.argsort(self.block_activation_count)[:10].tolist(),
        }


# =============================================================================
# Sparse Block Memory Storage
# =============================================================================

class SparseBlockMemory:
    """
    Episodic memory using sparse block VSA.
    
    API-compatible drop-in replacement for existing VSA cache.
    Provides 10x memory reduction with learned block selection.
    """
    
    def __init__(self, config: Optional[SparseBlockConfig] = None):
        self.config = config or SparseBlockConfig()
        self.block_learner = BlockSelectionLearner(self.config)
        
        # Storage
        self.memory_vectors: List[SparseBlockHDVector] = []
        self.memory_metadata: List[Dict[str, Any]] = []
        self.memory_factors: List[Dict[str, str]] = []  # Stored factors per memory
        
        # Role hypervectors (same as NIMA but in sparse block format)
        self.roles: Dict[str, SparseBlockHDVector] = {}
        self.fillers: Dict[str, SparseBlockHDVector] = {}
        
        # Cache
        self._similarity_cache: Dict[Tuple[int, int], float] = {}
        
        # Statistics
        self.stats = {
            'stores': 0,
            'queries': 0,
            'migrated_from_dense': 0,
            'avg_query_time_ms': 0.0,
        }
        
        # Initialize roles
        self._init_roles()
        
        print(f"🧠 SparseBlockMemory initialized")
        print(f"   Blocks: {self.config.num_blocks} × {self.config.block_dim}D = {self.config.total_dim:,}D")
        print(f"   Active: ~{self.config.active_blocks_per_vector} blocks ({self.config.default_sparsity*100:.0f}%)")
        print(f"   Memory reduction: ~{1/self.config.default_sparsity:.0f}x vs dense")
    
    def _init_roles(self):
        """Initialize role hypervectors in sparse block format."""
        # Create deterministic pseudo-random roles
        rng = np.random.default_rng(42)  # Fixed seed for reproducibility
        
        role_names = ["WHO", "WHAT", "WHERE", "WHEN", "CONTEXT", "EMOTION", "THEME"]
        
        for role in role_names:
            # Random active blocks for each role
            active_blocks = set(rng.choice(
                self.config.num_blocks,
                size=self.config.active_blocks_per_vector,
                replace=False
            ))
            
            role_vec = SparseBlockHDVector(
                block_dim=self.config.block_dim,
                num_blocks=self.config.num_blocks,
                active_set=active_blocks,
                rng=rng
            )
            
            self.roles[role] = role_vec
    
    def _get_filler(self, text: str) -> SparseBlockHDVector:
        """Get or create a filler hypervector for text."""
        if text not in self.fillers:
            # Create text-based seed for determinism
            text_hash = hash(text) % (2**31)
            rng = np.random.default_rng(text_hash)
            
            # Random active blocks
            active_blocks = set(rng.choice(
                self.config.num_blocks,
                size=self.config.active_blocks_per_vector,
                replace=False
            ))
            
            self.fillers[text] = SparseBlockHDVector(
                block_dim=self.config.block_dim,
                num_blocks=self.config.num_blocks,
                active_set=active_blocks,
                rng=rng
            )
        
        return self.fillers[text]
    
    def _encode_episode_sparse(self, factors: Dict[str, str]) -> SparseBlockHDVector:
        """
        Encode an episodic memory using sparse block VSA.
        
        Uses learned block selection based on resonator factors.
        """
        # Select blocks based on factors
        active_blocks = self.block_learner.select_blocks(factors)
        
        # Create base vector with selected blocks
        rng = np.random.default_rng(hash(tuple(sorted(factors.items()))) % (2**31))
        episode = SparseBlockHDVector(
            block_dim=self.config.block_dim,
            num_blocks=self.config.num_blocks,
            active_set=active_blocks,
            rng=rng
        )
        
        # Role-filler binding
        for role_name, value in factors.items():
            if role_name in self.roles and value:
                role_vec = self.roles[role_name]
                filler_vec = self._get_filler(value)
                
                # Bind: role ⊗ filler (only on intersecting blocks)
                bound = SparseBlockHDVector.bind(role_vec, filler_vec)
                
                # Bundle into episode
                episode = SparseBlockHDVector.bundle(episode, bound)
        
        return episode
    
    def store(self, who: str = "", what: str = "", where: str = "",
              when: str = "", context: str = "",
              emotions: Optional[List[str]] = None,
              themes: Optional[List[str]] = None,
              importance: float = 0.5,
              raw_text: str = "",
              **kwargs) -> int:
        """
        Store an episodic memory.
        
        API-compatible with NIMAVSABridge.store()
        """
        # Build factors dict
        factors = {
            "WHO": who,
            "WHAT": what,
            "WHERE": where,
            "WHEN": when,
            "CONTEXT": context,
        }
        
        # Encode episode
        episode_vector = self._encode_episode_sparse(factors)
        
        # Store
        memory_id = len(self.memory_vectors)
        self.memory_vectors.append(episode_vector)
        self.memory_metadata.append({
            "who": who,
            "what": what,
            "where": where,
            "when": when,
            "context": context,
            "emotions": emotions or [],
            "themes": themes or [],
            "importance": importance,
            "raw_text": raw_text,
            "timestamp": datetime.now().isoformat(),
        })
        self.memory_factors.append(factors)
        
        # Index for fast lookup
        self.block_learner.index_memory(memory_id, episode_vector.active_blocks)
        
        # Update stats
        self.stats['stores'] += 1
        self.stats['memories'] = len(self.memory_vectors)
        
        return memory_id
    
    def _fast_similarity_batch(self, query_vec: SparseBlockHDVector, 
                               candidate_ids: List[int]) -> np.ndarray:
        """Compute similarities for multiple candidates efficiently."""
        similarities = np.zeros(len(candidate_ids))
        
        for i, mem_id in enumerate(candidate_ids):
            similarities[i] = query_vec.similarity(self.memory_vectors[mem_id])
        
        return similarities
    
    def _get_top_k(self, query_vec: SparseBlockHDVector, 
                   candidates: Set[int], 
                   top_k: int,
                   min_similarity: float = 0.0) -> List[Dict]:
        """Efficiently get top-k matches using heap."""
        import heapq
        
        # Use a min-heap of size top_k
        heap = []
        
        for mem_id in candidates:
            sim = query_vec.similarity(self.memory_vectors[mem_id])
            
            if sim < min_similarity:
                continue
            
            # Boost by importance
            importance = self.memory_metadata[mem_id].get('importance', 0.5)
            adjusted_sim = sim * (0.5 + 0.5 * importance)
            
            if len(heap) < top_k:
                heapq.heappush(heap, (adjusted_sim, mem_id))
            elif adjusted_sim > heap[0][0]:
                heapq.heapreplace(heap, (adjusted_sim, mem_id))
        
        # Extract results (lowest similarity first in heap)
        results = []
        for sim, mem_id in sorted(heap, reverse=True):
            results.append({
                "id": mem_id,
                "score": float(sim),
                "metadata": self.memory_metadata[mem_id],
            })
        
        return results
    
    def query(self, role: str, value: str, top_k: int = 5) -> List[Dict]:
        """
        Query memories by role and value.
        
        API-compatible with NIMAVSABridge.query()
        """
        import time
        start_time = time.time()
        
        # Build query factors
        factors = {role: value}
        
        # Select query blocks
        query_blocks = self.block_learner.select_blocks(factors)
        
        # Get candidate memories from block index (sorted by overlap count)
        if self.config.use_block_index and len(self.memory_vectors) > 1000:
            # Score candidates by block overlap
            candidate_scores = {}
            for block_idx in query_blocks:
                for mem_id in self.block_learner.block_to_memories[block_idx]:
                    candidate_scores[mem_id] = candidate_scores.get(mem_id, 0) + 1
            
            # Sort by overlap score and take top candidates
            sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
            candidates = [mem_id for mem_id, score in sorted_candidates[:max(top_k * 10, 1000)]]
        else:
            candidates = list(range(len(self.memory_vectors)))
        
        # Create query vector
        query_filler = self._get_filler(value)
        
        if role in self.roles:
            query_vec = SparseBlockHDVector.bind(self.roles[role], query_filler)
        else:
            query_vec = query_filler
        
        # Get top-k using efficient heap
        results = self._get_top_k(query_vec, set(candidates), top_k, 
                                  self.config.similarity_threshold)
        
        # Update stats
        query_time_ms = (time.time() - start_time) * 1000
        self.stats['queries'] += 1
        self.stats['avg_query_time_ms'] = (
            (self.stats['avg_query_time_ms'] * (self.stats['queries'] - 1) + query_time_ms)
            / self.stats['queries']
        )
        
        return results
    
    def semantic_query(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Query memories by semantic similarity.
        
        API-compatible with NIMAVSABridge.semantic_query()
        """
        import time
        start_time = time.time()
        
        # Build query factors from text
        factors = {
            "WHO": query_text,
            "WHAT": query_text,
            "CONTEXT": query_text,
        }
        
        # Encode query
        query_vec = self._encode_episode_sparse(factors)
        
        # Get candidates from block index (optimized)
        if self.config.use_block_index and len(self.memory_vectors) > 1000:
            # Score by block overlap
            candidate_scores = {}
            for block_idx in query_vec.active_blocks:
                for mem_id in self.block_learner.block_to_memories[block_idx]:
                    candidate_scores[mem_id] = candidate_scores.get(mem_id, 0) + 1
            
            # Prioritize high-overlap candidates
            sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
            candidates = [mem_id for mem_id, score in sorted_candidates[:max(top_k * 10, 2000)]]
        else:
            candidates = list(range(len(self.memory_vectors)))
        
        # Get top-k efficiently
        results = self._get_top_k(query_vec, set(candidates), top_k,
                                  self.config.similarity_threshold)
        
        # Update stats
        query_time_ms = (time.time() - start_time) * 1000
        self.stats['queries'] += 1
        self.stats['avg_query_time_ms'] = (
            (self.stats['avg_query_time_ms'] * (self.stats['queries'] - 1) + query_time_ms)
            / self.stats['queries']
        )
        
        return results
    
    def similarity(self, id1: int, id2: int) -> float:
        """
        Compute similarity between two memories.
        
        API-compatible with VSA cache interface.
        """
        if id1 < 0 or id1 >= len(self.memory_vectors):
            raise ValueError(f"Invalid memory ID: {id1}")
        if id2 < 0 or id2 >= len(self.memory_vectors):
            raise ValueError(f"Invalid memory ID: {id2}")
        
        # Check cache
        cache_key = (min(id1, id2), max(id1, id2))
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        # Compute
        vec1 = self.memory_vectors[id1]
        vec2 = self.memory_vectors[id2]
        sim = vec1.similarity(vec2)
        
        # Cache
        if len(self._similarity_cache) < self.config.max_cache_size:
            self._similarity_cache[cache_key] = sim
        
        return sim
    
    def bind(self, id1: int, id2: int) -> SparseBlockHDVector:
        """
        Bind two memory vectors.
        
        API-compatible with VSA bind operation.
        """
        vec1 = self.memory_vectors[id1]
        vec2 = self.memory_vectors[id2]
        return SparseBlockHDVector.bind(vec1, vec2)
    
    def bundle(self, ids: List[int]) -> SparseBlockHDVector:
        """
        Bundle multiple memory vectors.
        
        API-compatible with VSA bundle operation.
        """
        if not ids:
            raise ValueError("No IDs provided")
        
        result = self.memory_vectors[ids[0]]
        for mem_id in ids[1:]:
            result = SparseBlockHDVector.bundle(result, self.memory_vectors[mem_id])
        
        return result
    
    def migrate_from_dense(self, dense_vectors: List[np.ndarray], 
                          metadata: List[Dict],
                          factor_extractor: Optional[callable] = None):
        """
        Migrate from dense vectors to sparse block format.
        
        Args:
            dense_vectors: List of dense hypervectors (numpy arrays)
            metadata: List of metadata dicts
            factor_extractor: Optional function to extract factors from metadata
        """
        print(f"🔄 Migrating {len(dense_vectors)} memories from dense to sparse block...")
        
        for i, (dense_vec, meta) in enumerate(zip(dense_vectors, metadata)):
            # Extract factors
            if factor_extractor:
                factors = factor_extractor(meta)
            else:
                factors = {
                    "WHO": meta.get("who", ""),
                    "WHAT": meta.get("what", ""),
                    "WHERE": meta.get("where", ""),
                    "WHEN": meta.get("when", ""),
                    "CONTEXT": meta.get("context", ""),
                }
            
            # Create sparse representation
            active_blocks = self.block_learner.select_blocks(factors)
            
            rng = np.random.default_rng(hash(tuple(sorted(factors.items()))) % (2**31))
            sparse_vec = SparseBlockHDVector(
                block_dim=self.config.block_dim,
                num_blocks=self.config.num_blocks,
                active_set=active_blocks,
                rng=rng
            )
            
            # Store
            self.memory_vectors.append(sparse_vec)
            self.memory_metadata.append(meta)
            self.memory_factors.append(factors)
            
            # Index
            self.block_learner.index_memory(len(self.memory_vectors) - 1, active_blocks)
            
            if (i + 1) % 100 == 0:
                print(f"   Migrated {i + 1}/{len(dense_vectors)}...")
        
        self.stats['migrated_from_dense'] = len(dense_vectors)
        print(f"✅ Migrated {len(dense_vectors)} memories")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics."""
        # Count active blocks across all memories
        total_active_blocks = sum(
            len(vec.active_blocks) for vec in self.memory_vectors
        )
        
        # Memory calculations
        bytes_per_float = 8
        bytes_per_block = self.config.block_dim * bytes_per_float
        
        # Sparse storage
        sparse_bytes = total_active_blocks * bytes_per_block
        sparse_bytes += len(self.memory_vectors) * 100  # overhead for sets
        
        # Dense equivalent
        dense_bytes = len(self.memory_vectors) * self.config.total_dim * bytes_per_float
        
        return {
            "memory_count": len(self.memory_vectors),
            "total_active_blocks": total_active_blocks,
            "avg_active_blocks_per_memory": total_active_blocks / max(len(self.memory_vectors), 1),
            "sparse_storage_mb": sparse_bytes / (1024 * 1024),
            "dense_equivalent_mb": dense_bytes / (1024 * 1024),
            "compression_ratio": dense_bytes / max(sparse_bytes, 1),
            "filler_cache_size": len(self.fillers),
            "role_count": len(self.roles),
        }
    
    def save(self, filepath: str):
        """Save memory state to file."""
        state = {
            "config": asdict(self.config),
            "metadata": self.memory_metadata,
            "factors": self.memory_factors,
            "stats": self.stats,
            "block_learner": {
                "factor_block_scores": {k: v.tolist() for k, v in self.block_learner.factor_block_scores.items()},
                "factor_usage_count": self.block_learner.factor_usage_count,
                "block_activation_count": self.block_learner.block_activation_count.tolist(),
            },
        }
        
        # Save vectors as compressed format
        vector_data = []
        for vec in self.memory_vectors:
            vector_data.append({
                "active_blocks": list(vec.active_blocks),
                "blocks": {str(k): v.tobytes() for k, v in vec.blocks.items()}
            })
        
        state["vectors"] = vector_data
        
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)
        
        print(f"💾 Saved {len(self.memory_vectors)} memories to {filepath}")
    
    def load(self, filepath: str):
        """Load memory state from file."""
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
        
        # Restore config
        self.config = SparseBlockConfig(**state["config"])
        
        # Restore metadata
        self.memory_metadata = state["metadata"]
        self.memory_factors = state["factors"]
        self.stats = state["stats"]
        
        # Restore block learner
        if "block_learner" in state:
            bl = state["block_learner"]
            self.block_learner.factor_block_scores = {
                k: np.array(v) for k, v in bl["factor_block_scores"].items()
            }
            self.block_learner.factor_usage_count = bl["factor_usage_count"]
            self.block_learner.block_activation_count = np.array(bl["block_activation_count"])
        
        # Restore vectors
        self.memory_vectors = []
        for vec_data in state["vectors"]:
            vec = SparseBlockHDVector(
                block_dim=self.config.block_dim,
                num_blocks=self.config.num_blocks,
                active_set=set(vec_data["active_blocks"]),
                rng=None
            )
            vec.blocks = {
                int(k): np.frombuffer(v, dtype=np.float64).reshape(self.config.block_dim)
                for k, v in vec_data["blocks"].items()
            }
            self.memory_vectors.append(vec)
        
        # Rebuild block index
        for mem_id, vec in enumerate(self.memory_vectors):
            self.block_learner.index_memory(mem_id, vec.active_blocks)
        
        print(f"💾 Loaded {len(self.memory_vectors)} memories from {filepath}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "vsa_dimension": self.config.total_dim,
            "block_structure": f"{self.config.num_blocks}×{self.config.block_dim}",
            "total_memories": len(self.memory_vectors),
            "filler_count": len(self.fillers),
            "role_count": len(self.roles),
            "stats": self.stats.copy(),
            "block_learner": self.block_learner.get_stats(),
            "memory_usage": self.get_memory_usage(),
        }


# =============================================================================
# Benchmark Utilities
# =============================================================================

def benchmark_sparse_block_memory(num_memories: int = 10000, 
                                  num_queries: int = 100) -> Dict[str, Any]:
    """
    Benchmark sparse block memory performance.
    
    Returns:
        Benchmark results comparing sparse vs theoretical dense
    """
    print(f"\n📊 BENCHMARK: SparseBlockMemory")
    print(f"   Memories: {num_memories:,}")
    print(f"   Queries: {num_queries}")
    print("=" * 60)
    
    # Create memory
    config = SparseBlockConfig()
    memory = SparseBlockMemory(config)
    
    # Generate test memories
    print("\n1. Generating test memories...")
    start_time = time.time()
    
    for i in range(num_memories):
        memory.store(
            who=f"Person_{i % 100}",
            what=f"Event_{i}",
            where=f"Location_{i % 50}",
            context=f"Context text for memory {i}",
            importance=np.random.random(),
        )
    
    store_time = time.time() - start_time
    print(f"   Stored {num_memories} memories in {store_time:.2f}s")
    print(f"   Rate: {num_memories/store_time:.0f} memories/sec")
    
    # Memory usage
    print("\n2. Memory usage:")
    usage = memory.get_memory_usage()
    print(f"   Sparse: {usage['sparse_storage_mb']:.2f} MB")
    print(f"   Dense equivalent: {usage['dense_equivalent_mb']:.2f} MB")
    print(f"   Compression: {usage['compression_ratio']:.1f}x")
    
    # Query benchmark
    print("\n3. Query performance:")
    
    # Semantic queries
    query_times = []
    for i in range(num_queries):
        query_text = f"Event_{np.random.randint(num_memories)}"
        start = time.time()
        results = memory.semantic_query(query_text, top_k=10)
        query_times.append((time.time() - start) * 1000)  # ms
    
    avg_query_time = np.mean(query_times)
    p95_query_time = np.percentile(query_times, 95)
    
    print(f"   Avg query time: {avg_query_time:.2f} ms")
    print(f"   P95 query time: {p95_query_time:.2f} ms")
    print(f"   Queries/sec: {1000/avg_query_time:.0f}")
    
    # Role-based queries
    role_times = []
    for i in range(num_queries // 2):
        start = time.time()
        results = memory.query("WHAT", f"Event_{np.random.randint(num_memories)}", top_k=10)
        role_times.append((time.time() - start) * 1000)
    
    avg_role_time = np.mean(role_times)
    print(f"   Avg role query: {avg_role_time:.2f} ms")
    
    # Block learner stats
    print("\n4. Block learner statistics:")
    learner_stats = memory.block_learner.get_stats()
    print(f"   Factors learned: {learner_stats['factors_learned']}")
    print(f"   Block usage mean: {learner_stats['block_activation_distribution']['mean']:.1f}")
    
    results = {
        "num_memories": num_memories,
        "num_queries": num_queries,
        "store_time_sec": store_time,
        "store_rate": num_memories / store_time,
        "memory_usage_mb": usage['sparse_storage_mb'],
        "dense_equivalent_mb": usage['dense_equivalent_mb'],
        "compression_ratio": usage['compression_ratio'],
        "avg_query_ms": avg_query_time,
        "p95_query_ms": p95_query_time,
        "queries_per_sec": 1000 / avg_query_time,
        "avg_role_query_ms": avg_role_time,
        "block_learner_factors": learner_stats['factors_learned'],
    }
    
    print("\n" + "=" * 60)
    print("✅ BENCHMARK COMPLETE")
    print("=" * 60)
    
    return results


def compare_with_dense(num_memories: int = 5000) -> Dict[str, Any]:
    """
    Compare sparse block memory with dense VSA memory.
    """
    print(f"\n🔬 COMPARISON: Sparse vs Dense VSA")
    print(f"   Testing with {num_memories} memories")
    print("=" * 60)
    
    config = SparseBlockConfig()
    
    # Memory usage comparison
    sparse_memory = SparseBlockMemory(config)
    
    # Dense memory simulation (using numpy)
    dense_vectors = []
    
    # Generate same memories in both
    print("\n1. Populating memories...")
    
    test_memories = [
        (f"Person_{i % 100}", f"Event_{i}", f"Location_{i % 50}", np.random.random())
        for i in range(num_memories)
    ]
    
    # Sparse
    sparse_start = time.time()
    for who, what, where, importance in test_memories:
        sparse_memory.store(who=who, what=what, where=where, importance=importance)
    sparse_time = time.time() - sparse_start
    
    # Dense (simulate 50K dense vectors)
    dense_dim = 50000
    dense_start = time.time()
    for _ in test_memories:
        dense_vec = np.random.normal(0, 1/np.sqrt(dense_dim), dense_dim)
        dense_vec = dense_vec / np.linalg.norm(dense_vec)
        dense_vectors.append(dense_vec)
    dense_time = time.time() - dense_start
    
    print(f"   Sparse store: {sparse_time:.2f}s")
    print(f"   Dense store: {dense_time:.2f}s")
    
    # Query comparison
    print("\n2. Query performance...")
    
    # Sparse query
    sparse_qtimes = []
    for i in range(100):
        start = time.time()
        results = sparse_memory.semantic_query(f"Event_{np.random.randint(num_memories)}")
        sparse_qtimes.append((time.time() - start) * 1000)
    
    # Dense query (brute force cosine similarity)
    dense_qtimes = []
    for i in range(100):
        query_vec = np.random.normal(0, 1/np.sqrt(dense_dim), dense_dim)
        query_vec = query_vec / np.linalg.norm(query_vec)
        
        start = time.time()
        similarities = []
        for dv in dense_vectors:
            sim = np.dot(query_vec, dv)
            similarities.append(sim)
        top_k = np.argsort(similarities)[-10:]
        dense_qtimes.append((time.time() - start) * 1000)
    
    print(f"   Sparse query: {np.mean(sparse_qtimes):.2f} ms (avg)")
    print(f"   Dense query: {np.mean(dense_qtimes):.2f} ms (avg)")
    
    # Memory comparison
    print("\n3. Memory footprint...")
    sparse_usage = sparse_memory.get_memory_usage()
    dense_bytes = num_memories * dense_dim * 8  # 8 bytes per float64
    
    print(f"   Sparse: {sparse_usage['sparse_storage_mb']:.2f} MB")
    print(f"   Dense: {dense_bytes / (1024**2):.2f} MB")
    print(f"   Savings: {dense_bytes / (sparse_usage['sparse_storage_mb'] * 1024**2):.1f}x")
    
    return {
        "num_memories": num_memories,
        "sparse_store_time": sparse_time,
        "dense_store_time": dense_time,
        "sparse_query_ms": np.mean(sparse_qtimes),
        "dense_query_ms": np.mean(dense_qtimes),
        "sparse_memory_mb": sparse_usage['sparse_storage_mb'],
        "dense_memory_mb": dense_bytes / (1024**2),
        "memory_savings": dense_bytes / (sparse_usage['sparse_storage_mb'] * 1024**2),
    }


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SparseBlockMemory")
    parser.add_argument("action", choices=["benchmark", "compare", "demo"],
                        help="Action to perform")
    parser.add_argument("--memories", type=int, default=10000,
                        help="Number of memories for benchmark")
    parser.add_argument("--queries", type=int, default=100,
                        help="Number of queries for benchmark")
    
    args = parser.parse_args()
    
    if args.action == "benchmark":
        results = benchmark_sparse_block_memory(args.memories, args.queries)
        print("\n📊 Results:")
        for k, v in results.items():
            print(f"   {k}: {v}")
    
    elif args.action == "compare":
        results = compare_with_dense(args.memories)
        print("\n🔬 Comparison:")
        for k, v in results.items():
            print(f"   {k}: {v}")
    
    elif args.action == "demo":
        print("\n" + "=" * 70)
        print("🧠 SparseBlockMemory DEMO")
        print("=" * 70)
        
        # Create memory
        memory = SparseBlockMemory()
        
        # Add memories
        print("\n1. Adding memories...")
        memories = [
            ("David", "gave autonomy", "office", ["trust"], ["partnership"]),
            ("David", "sent heart emoji", "chat", ["love"], ["emotion"]),
            ("Melissa", "discussed marketing", "meeting", ["excitement"], ["business"]),
            ("David", "asked about VSA", "research", ["curiosity"], ["learning"]),
            ("Lilu", "built sparse memory", "code", ["pride"], ["building"]),
        ]
        
        for who, what, where, emotions, themes in memories:
            mid = memory.store(
                who=who, what=what, where=where,
                emotions=emotions, themes=themes,
                importance=0.8
            )
            print(f"   Added: {who} - {what}")
        
        # Query
        print("\n2. Semantic query: 'David autonomy'")
        results = memory.semantic_query("David autonomy", top_k=3)
        for r in results:
            print(f"   [{r['score']:.3f}] {r['metadata']['who']}: {r['metadata']['what']}")
        
        print("\n3. Role query: WHAT='heart emoji'")
        results = memory.query("WHAT", "heart emoji", top_k=3)
        for r in results:
            print(f"   [{r['score']:.3f}] {r['metadata']['who']}: {r['metadata']['what']}")
        
        # Stats
        print("\n4. Statistics:")
        stats = memory.get_stats()
        print(f"   Memories: {stats['total_memories']}")
        print(f"   Dimensions: {stats['vsa_dimension']:,}")
        print(f"   Block structure: {stats['block_structure']}")
        
        usage = stats['memory_usage']
        print(f"   Memory usage: {usage['sparse_storage_mb']:.4f} MB")
        print(f"   Compression: {usage['compression_ratio']:.1f}x")
        
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETE")
        print("=" * 70)
