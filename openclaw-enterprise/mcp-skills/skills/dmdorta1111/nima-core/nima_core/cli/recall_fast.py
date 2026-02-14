#!/usr/bin/env python3
"""
Ultra-Lightweight NIMA Recall for Hooks
=========================================
No embeddings, no heavy imports. Just fast keyword search.

Falls back to Graphiti (SQLite) if available for instant results.
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def fast_recall_graphiti(data_dir: Path, query: str, top_k: int = 5):
    """
    Fast recall using Graphiti SQLite database.
    No model loading, just SQL queries.
    """
    try:
        # Look for Graphiti database
        graphiti_db = data_dir / 'knowledge_graph.db'
        if not graphiti_db.exists():
            # Try alternate locations
            alt_paths = [
                Path.home() / '.openclaw' / 'workspace' / 'lilu_core' / 'storage' / 'data' / 'knowledge_graph.db',
                Path.home() / '.nima' / 'knowledge_graph.db',
            ]
            for alt in alt_paths:
                if alt.exists():
                    graphiti_db = alt
                    break
        
        if not graphiti_db.exists():
            return None  # No Graphiti available
        
        # Query Graphiti for relevant memories
        conn = sqlite3.connect(f'file:{graphiti_db}?mode=ro', uri=True)
        cursor = conn.cursor()
        
        # Extract keywords from query
        keywords = [k.lower() for k in query.split() if len(k) > 3]
        
        results = []
        
        # Search in episodes (memories)
        try:
            cursor.execute("""
                SELECT e.content, e.timestamp, e.source
                FROM episodes e
                WHERE e.content LIKE ?
                ORDER BY e.timestamp DESC
                LIMIT ?
            """, (f'%{keywords[0] if keywords else query}%', top_k * 2))
            
            for row in cursor.fetchall():
                content, timestamp, source = row
                results.append({
                    'who': source or '?',
                    'what': content[:200] if content else '',
                    'when': timestamp
                })
        except sqlite3.OperationalError as e:
            # Table might not exist or schema different
            pass
        
        # Search in facts
        if len(results) < top_k:
            try:
                cursor.execute("""
                    SELECT name, fact, created_at 
                    FROM facts 
                    WHERE fact LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (f'%{keywords[0] if keywords else query}%', top_k - len(results)))
                
                for row in cursor.fetchall():
                    name, fact, created_at = row
                    results.append({
                        'who': name or '?',
                        'what': fact[:200] if fact else '',
                        'when': created_at
                    })
            except sqlite3.OperationalError:
                pass
        
        conn.close()
        return results[:top_k]
        
    except Exception as e:
        return None

def fast_recall_json(data_dir: Path, query: str, top_k: int = 5):
    """
    Fast recall from JSON memory files.
    """
    try:
        # Try multiple memory file locations
        memory_files = [
            data_dir / 'episodic_memory.json',
            data_dir / 'memories.json',
            Path.home() / '.nima' / 'data' / 'episodic_memory.json',
        ]
        
        memories = []
        for mf in memory_files:
            if mf.exists():
                try:
                    with open(mf, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            memories.extend(data)
                        elif isinstance(data, dict) and 'memories' in data:
                            memories.extend(data['memories'])
                except:
                    continue
        
        if not memories:
            return None
        
        # Parse query keywords
        query_words = set(query.lower().split())
        
        # Score memories
        scored = []
        for mem in memories:
            text = mem.get('what', mem.get('content', ''))
            text_lower = text.lower()
            
            # Keyword matching score
            score = 0.0
            for word in query_words:
                if word in text_lower:
                    score += 1.0
                    if f' {word} ' in f' {text_lower} ':
                        score += 0.5
            
            if query_words:
                score /= len(query_words)
            
            scored.append((score, mem))
        
        # Sort by score and return top_k
        scored.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, mem in scored[:top_k]:
            results.append({
                'who': mem.get('who', mem.get('name', '?')),
                'what': str(mem.get('what', mem.get('content', '')))[:200],
            })
        
        return results
        
    except Exception as e:
        return None

def fast_recall(query: str, top_k: int = 5, data_dir: str = None):
    """
    Ultra-fast recall - tries multiple backends in order of speed.
    """
    # Resolve data directory
    if data_dir is None:
        # Try to find the lilu_core data dir
        data_dir = Path.home() / '.openclaw' / 'workspace' / 'lilu_core' / 'storage' / 'data'
        if not data_dir.exists():
            data_dir = Path.home() / '.nima' / 'data'
    else:
        data_dir = Path(data_dir)
    
    # Try Graphiti first (fastest - just SQLite)
    results = fast_recall_graphiti(data_dir, query, top_k)
    if results:
        return results
    
    # Fall back to JSON files
    results = fast_recall_json(data_dir, query, top_k)
    if results:
        return results
    
    # No memories found - return empty list gracefully
    return []

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Ultra-fast NIMA recall')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--top-k', type=int, default=5)
    parser.add_argument('--data-dir', default=None)
    args = parser.parse_args()
    
    results = fast_recall(args.query, args.top_k, args.data_dir)
    
    for r in results:
        print(f"{r['who']}|{r['what']}")

if __name__ == '__main__':
    main()
