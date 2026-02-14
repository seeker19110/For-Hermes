#!/usr/bin/env python3
"""
Sparse Retrieval for NIMA
=========================
Two-stage retrieval using concentrated embeddings for 10x speedup.

Architecture:
    Query → Project → Sparsify (1%) → Index Scan → Top-K candidates
                                                   ↓
                                Re-rank (10% sparse) → Final results

Based on: MATHEMATICAL_FRAMEWORKS_SPARSE_VSA.md

Author: NIMA Project
Date: 2026
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict
import threading


def sparsify(vector: np.ndarray, sparsity: float = 0.01) -> Tuple[np.ndarray, np.ndarray]:
    """
    Sparsify a vector by keeping top-k dimensions by magnitude.
    
    Args:
        vector: Dense vector (D,)
        sparsity: Fraction of dimensions to keep (default 1%)
        
    Returns:
        (indices, values) of non-zero elements
    """
    k = max(1, int(len(vector) * sparsity))
    
    # Get top-k by absolute value
    abs_vals = np.abs(vector)
    top_indices = np.argpartition(abs_vals, -k)[-k:]
    
    # Sort by magnitude for consistent ordering
    sorted_idx = top_indices[np.argsort(abs_vals[top_indices])[::-1]]
    
    return sorted_idx, vector[sorted_idx]


class SparseRetriever:
    """
    Two-stage sparse retrieval for concentrated embeddings.
    
    Stage 1 (Index): 1% sparsity, inverted index scan
    Stage 2 (Re-rank): 10% sparsity, weighted collision score
    
    Memory efficiency: Only stores sparse representations.
    Speed: O(k * avg_posting_length) vs O(N * D) for dense.
    """
    
    def __init__(
        self,
        index_sparsity: float = 0.01,  # 1% for index
        rerank_sparsity: float = 0.10,  # 10% for re-ranking
        dimension: int = 50000
    ):
        self.index_sparsity = index_sparsity
        self.rerank_sparsity = rerank_sparsity
        self.dimension = dimension
        
        # Inverted index: dim_id → [(memory_id, value), ...]
        self.inverted_index: Dict[int, List[Tuple[int, float]]] = defaultdict(list)
        
        # Memory storage: id → (sparse_indices, sparse_values, metadata)
        self.memories: Dict[int, Tuple[np.ndarray, np.ndarray, Dict]] = {}
        
        # Dense vectors for re-ranking (10% sparse)
        self.rerank_vectors: Dict[int, Tuple[np.ndarray, np.ndarray]] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Stats
        self.stats = {
            'total_memories': 0,
            'index_lookups': 0,
            'rerank_operations': 0,
        }
    
    def add(
        self,
        memory_id: int,
        embedding: np.ndarray,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a memory to the sparse index.
        
        Args:
            memory_id: Unique identifier
            embedding: Concentrated embedding (D,)
            metadata: Optional metadata dict
        """
        with self._lock:
            # Sparsify for index (1%)
            idx_indices, idx_values = sparsify(embedding, self.index_sparsity)
            
            # Sparsify for re-ranking (10%)
            rerank_indices, rerank_values = sparsify(embedding, self.rerank_sparsity)
            
            # Store
            self.memories[memory_id] = (idx_indices, idx_values, metadata or {})
            self.rerank_vectors[memory_id] = (rerank_indices, rerank_values)
            
            # Add to inverted index
            for dim, val in zip(idx_indices, idx_values):
                self.inverted_index[int(dim)].append((memory_id, float(val)))
            
            self.stats['total_memories'] += 1
    
    def add_batch(
        self,
        embeddings: np.ndarray,
        metadatas: Optional[List[Dict]] = None,
        start_id: int = 0
    ) -> List[int]:
        """
        Add multiple memories at once.
        
        Args:
            embeddings: (N, D) array
            metadatas: List of metadata dicts
            start_id: Starting memory ID
            
        Returns:
            List of assigned memory IDs
        """
        ids = []
        metadatas = metadatas or [{}] * len(embeddings)
        
        for i, (emb, meta) in enumerate(zip(embeddings, metadatas)):
            mem_id = start_id + i
            self.add(mem_id, emb, meta)
            ids.append(mem_id)
        
        return ids
    
    def query(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        candidates_multiplier: int = 10
    ) -> List[Tuple[int, float, Dict]]:
        """
        Two-stage retrieval.
        
        Stage 1: Sparse index scan for candidates
        Stage 2: Re-rank candidates with denser representation
        
        Args:
            query_embedding: Query vector (D,)
            top_k: Number of results to return
            candidates_multiplier: How many candidates to fetch before re-ranking
            
        Returns:
            List of (memory_id, score, metadata) sorted by score descending
        """
        with self._lock:
            self.stats['index_lookups'] += 1
            
            # Stage 1: Sparse index scan
            q_indices, q_values = sparsify(query_embedding, self.index_sparsity)
            
            # Accumulate collision scores
            candidate_scores: Dict[int, float] = defaultdict(float)
            
            for q_dim, q_val in zip(q_indices, q_values):
                q_dim = int(q_dim)
                if q_dim in self.inverted_index:
                    for mem_id, mem_val in self.inverted_index[q_dim]:
                        # Weighted collision score: |q_i| * |m_i|
                        candidate_scores[mem_id] += abs(q_val) * abs(mem_val)
            
            if not candidate_scores:
                return []
            
            # Get top candidates for re-ranking
            n_candidates = min(len(candidate_scores), top_k * candidates_multiplier)
            top_candidates = sorted(
                candidate_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:n_candidates]
            
            # Stage 2: Re-rank with 10% sparse vectors
            self.stats['rerank_operations'] += 1
            
            q_rerank_idx, q_rerank_val = sparsify(query_embedding, self.rerank_sparsity)
            
            # Build query dict for O(1) lookup (fixes O(n²) bug)
            q_dict = dict(zip(q_rerank_idx, q_rerank_val))
            
            reranked = []
            for mem_id, _ in top_candidates:
                m_idx, m_val = self.rerank_vectors[mem_id]
                
                # Build memory dict for O(1) intersection
                m_dict = dict(zip(m_idx, m_val))
                
                # Efficient sparse dot product via dict intersection
                score = sum(q_dict[qi] * m_dict[qi] 
                           for qi in q_dict if qi in m_dict)
                
                metadata = self.memories[mem_id][2]
                reranked.append((mem_id, score, metadata))
            
            # Sort by re-ranked score
            reranked.sort(key=lambda x: x[1], reverse=True)
            
            return reranked[:top_k]
    
    def query_batch(
        self,
        query_embeddings: np.ndarray,
        top_k: int = 10
    ) -> List[List[Tuple[int, float, Dict]]]:
        """Query multiple embeddings."""
        return [self.query(q, top_k) for q in query_embeddings]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics."""
        with self._lock:
            avg_posting_len = 0
            if self.inverted_index:
                total_postings = sum(len(v) for v in self.inverted_index.values())
                avg_posting_len = total_postings / len(self.inverted_index)
            
            return {
                **self.stats,
                'index_size': len(self.inverted_index),
                'avg_posting_length': avg_posting_len,
                'index_sparsity': self.index_sparsity,
                'rerank_sparsity': self.rerank_sparsity,
            }
    
    def clear(self) -> None:
        """Clear all data."""
        with self._lock:
            self.inverted_index.clear()
            self.memories.clear()
            self.rerank_vectors.clear()
            self.stats = {
                'total_memories': 0,
                'index_lookups': 0,
                'rerank_operations': 0,
            }
    
    def save(self, path: str) -> None:
        """
        Persist the sparse index to disk.
        
        Saves:
            - inverted_index
            - memories
            - rerank_vectors
            - config (dimension, sparsities)
        
        Args:
            path: Path to save the index (will use torch.save for efficiency)
        """
        import torch
        from pathlib import Path
        
        with self._lock:
            # Convert inverted index to serializable format
            # Dict[int, List[Tuple[int, float]]] → same but JSON-friendly
            index_data = {
                int(k): [(int(mid), float(val)) for mid, val in v]
                for k, v in self.inverted_index.items()
            }
            
            # Convert memories: id → (indices, values, metadata)
            memories_data = {}
            for mem_id, (indices, values, meta) in self.memories.items():
                memories_data[int(mem_id)] = {
                    'indices': indices.tolist(),
                    'values': values.tolist(),
                    'metadata': meta
                }
            
            # Convert rerank vectors
            rerank_data = {}
            for mem_id, (indices, values) in self.rerank_vectors.items():
                rerank_data[int(mem_id)] = {
                    'indices': indices.tolist(),
                    'values': values.tolist()
                }
            
            data = {
                'version': 1,
                'config': {
                    'dimension': self.dimension,
                    'index_sparsity': self.index_sparsity,
                    'rerank_sparsity': self.rerank_sparsity,
                },
                'inverted_index': index_data,
                'memories': memories_data,
                'rerank_vectors': rerank_data,
                'stats': self.stats,
            }
            
            from ..utils import atomic_torch_save
            atomic_torch_save(data, Path(path))
    
    @classmethod
    def load(cls, path: str) -> 'SparseRetriever':
        """
        Load a sparse index from disk.
        
        Args:
            path: Path to saved index
            
        Returns:
            Loaded SparseRetriever instance
        """
        import torch
        from pathlib import Path
        
        if not Path(path).exists():
            raise FileNotFoundError(f"No index found at {path}")
        
        from ..utils import safe_torch_load
        data = safe_torch_load(path)
        
        # Create instance with saved config
        config = data['config']
        instance = cls(
            dimension=config['dimension'],
            index_sparsity=config['index_sparsity'],
            rerank_sparsity=config['rerank_sparsity']
        )
        
        # Restore inverted index
        for dim, postings in data['inverted_index'].items():
            instance.inverted_index[int(dim)] = [(int(mid), float(val)) for mid, val in postings]
        
        # Restore memories
        for mem_id, mem_data in data['memories'].items():
            instance.memories[int(mem_id)] = (
                np.array(mem_data['indices']),
                np.array(mem_data['values']),
                mem_data['metadata']
            )
        
        # Restore rerank vectors
        for mem_id, rv_data in data['rerank_vectors'].items():
            instance.rerank_vectors[int(mem_id)] = (
                np.array(rv_data['indices']),
                np.array(rv_data['values'])
            )
        
        # Restore stats
        instance.stats = data['stats']
        
        return instance
    
    def get_memory_hash(self) -> str:
        """Get a hash representing current index state (for cache invalidation)."""
        import hashlib
        with self._lock:
            # Hash based on memory count and IDs
            content = f"{len(self.memories)}:{sorted(self.memories.keys())}"
            return hashlib.md5(content.encode()).hexdigest()[:16]


# ============================================================================
# BENCHMARKING
# ============================================================================

def benchmark_sparse_vs_dense(n_memories: int = 1000, dimension: int = 50000):
    """
    Benchmark sparse retrieval vs dense cosine similarity.
    """
    import time
    from sklearn.metrics.pairwise import cosine_similarity
    
    print(f"\n{'='*60}")
    print(f"Benchmark: Sparse vs Dense Retrieval")
    print(f"Memories: {n_memories:,} | Dimension: {dimension:,}")
    print(f"{'='*60}\n")
    
    # Generate random concentrated embeddings
    np.random.seed(42)
    embeddings = np.random.randn(n_memories, dimension).astype(np.float32)
    
    # Simulate concentration (energy in top 10%)
    for i in range(n_memories):
        mask = np.random.random(dimension) > 0.9  # 10% active
        embeddings[i] *= mask
    
    query = embeddings[0].copy()  # Use first as query
    
    # Build sparse index
    print("Building sparse index...")
    t0 = time.time()
    retriever = SparseRetriever(dimension=dimension)
    retriever.add_batch(embeddings)
    build_time = time.time() - t0
    print(f"  Build time: {build_time:.3f}s")
    print(f"  Index size: {len(retriever.inverted_index):,} dimensions")
    
    # Sparse query
    print("\nSparse retrieval (10 queries)...")
    t0 = time.time()
    for _ in range(10):
        results = retriever.query(query, top_k=10)
    sparse_time = (time.time() - t0) / 10
    print(f"  Avg query time: {sparse_time*1000:.2f}ms")
    
    # Dense query (for comparison)
    print("\nDense retrieval (10 queries)...")
    t0 = time.time()
    for _ in range(10):
        sims = cosine_similarity(query.reshape(1, -1), embeddings)[0]
        top_k = np.argsort(sims)[-10:][::-1]
    dense_time = (time.time() - t0) / 10
    print(f"  Avg query time: {dense_time*1000:.2f}ms")
    
    # Speedup
    speedup = dense_time / sparse_time
    print(f"\n{'='*60}")
    print(f"SPEEDUP: {speedup:.1f}x faster with sparse retrieval")
    print(f"{'='*60}\n")
    
    return speedup


if __name__ == "__main__":
    print("Testing Sparse Retrieval Module\n")
    
    # Basic test
    print("1. Basic functionality test...")
    retriever = SparseRetriever(dimension=50000)
    
    # Add some test embeddings
    np.random.seed(42)
    test_embeddings = np.random.randn(100, 50000).astype(np.float32)
    
    # Simulate concentration
    for i in range(100):
        mask = np.random.random(50000) > 0.9
        test_embeddings[i] *= mask
    
    metadatas = [{'text': f'Memory {i}', 'theme': 'test'} for i in range(100)]
    retriever.add_batch(test_embeddings, metadatas)
    
    print(f"   Added {retriever.stats['total_memories']} memories")
    print(f"   Index dimensions: {len(retriever.inverted_index)}")
    
    # Query
    query = test_embeddings[0]
    results = retriever.query(query, top_k=5)
    
    print(f"\n   Query results (top 5):")
    for mem_id, score, meta in results:
        print(f"     ID={mem_id}, score={score:.4f}, text={meta.get('text', 'N/A')}")
    
    # Verify self-retrieval works
    assert results[0][0] == 0, "Self-retrieval should return query as top result"
    print("\n   ✅ Self-retrieval verified")
    
    print(f"\n   Stats: {retriever.get_stats()}")
    
    # Benchmark
    print("\n2. Running benchmark...")
    benchmark_sparse_vs_dense(n_memories=1000, dimension=50000)
    
    print("✅ Sparse retrieval module working!")
