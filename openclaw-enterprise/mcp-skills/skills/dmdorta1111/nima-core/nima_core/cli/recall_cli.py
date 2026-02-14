#!/usr/bin/env python3
"""
Lightweight NIMA Recall CLI
============================
Fast recall without loading heavy components.
Caches embedder between calls for efficiency.
"""

import sys
import json
import argparse
from pathlib import Path

# Global embedder cache (persists between calls in same process)
_embedder_cache = None

def get_cached_embedder():
    """Get or create embedder with caching."""
    global _embedder_cache
    if _embedder_cache is None:
        from sentence_transformers import SentenceTransformer
        # Use lightweight model for fast loading
        _embedder_cache = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _embedder_cache

def recall_memories(query: str, top_k: int = 5, data_dir: str = None):
    """Fast recall using cached embedder."""
    try:
        # Lazy imports for speed
        import numpy as np
        
        embedder = get_cached_embedder()
        query_vec = embedder.encode(query, convert_to_numpy=True)
        
        # Load memory index
        if data_dir is None:
            data_dir = Path.home() / '.nima' / 'data'
        else:
            data_dir = Path(data_dir)
        
        memory_file = data_dir / 'episodic_memory.json'
        if not memory_file.exists():
            return []
        
        with open(memory_file, 'r') as f:
            memories = json.load(f)
        
        if not memories:
            return []
        
        # Simple text similarity fallback if no vectors
        results = []
        query_lower = query.lower()
        
        for mem in memories:
            text = mem.get('what', '')
            score = 0.0
            
            # Simple keyword matching (fast)
            for word in query_lower.split():
                if word in text.lower():
                    score += 0.1
            
            # Recency boost
            if 'when' in mem:
                score += 0.05
            
            results.append({
                'who': mem.get('who', '?'),
                'what': text[:200],
                'score': score
            })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description='Fast NIMA recall')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--top-k', type=int, default=5)
    parser.add_argument('--data-dir', default=None)
    args = parser.parse_args()
    
    results = recall_memories(args.query, args.top_k, args.data_dir)
    
    for r in results:
        print(f"{r['who']}|{r['what']}")

if __name__ == '__main__':
    main()
