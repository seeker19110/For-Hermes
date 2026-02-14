#!/usr/bin/env python3
"""
Sequence Predictor — Frontier 5 Step 3
=======================================

Build corpus of encoded sequences, then predict next turns
by finding similar sequences and unbinding.

Author: NIMA Project
Date: 2026
"""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime
import threading
import logging

logger = logging.getLogger(__name__)

from ..config import NIMA_DATA_DIR, ZERO_NORM_THRESHOLD

SEQUENCE_DIR = NIMA_DATA_DIR / "sequences"


@dataclass
class StoredSequence:
    """A stored sequence for prediction matching."""
    vector: torch.Tensor
    length: int
    metadata: Dict
    timestamp: str


class SequenceCorpus:
    """
    Corpus of encoded sequences for prediction.
    
    Stores sequence vectors and enables similarity-based retrieval
    for next-turn prediction.
    """
    
    def __init__(self, dimension: int = 50000, data_dir: Path = None):
        self.dimension = dimension
        self._lock = threading.RLock()
        self.sequences: List[StoredSequence] = []
        
        if data_dir is None:
            data_dir = NIMA_DATA_DIR
        self.corpus_path = data_dir / "sequences" / "corpus.pt"
    
    def add(self, sequence_vector: torch.Tensor, length: int, metadata: Optional[Dict] = None):
        """Add a sequence to the corpus."""
        with self._lock:
            self.sequences.append(StoredSequence(
                vector=sequence_vector,
                length=length,
                metadata=metadata or {},
                timestamp=datetime.now().isoformat(),
            ))
    
    def find_similar(
        self,
        query_vector: torch.Tensor,
        min_length: int = 2,
        top_k: int = 5,
    ) -> List[Tuple[StoredSequence, float]]:
        """Find sequences similar to the query."""
        results = []
        
        for seq in self.sequences:
            if seq.length < min_length:
                continue
            
            sim = self._cosine_sim(query_vector, seq.vector)
            results.append((seq, sim))
        
        results.sort(key=lambda x: -x[1])
        return results[:top_k]
    
    def save(self):
        """Save corpus to disk."""
        with self._lock:
            self.corpus_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'sequences': [
                    {
                        'vector': seq.vector,
                        'length': seq.length,
                        'metadata': seq.metadata,
                        'timestamp': seq.timestamp,
                    }
                    for seq in self.sequences
                ],
                'count': len(self.sequences),
                'saved_at': datetime.now().isoformat(),
            }
            
            from ..utils import atomic_torch_save
            atomic_torch_save(data, self.corpus_path)
            logger.info(f"Saved {len(self.sequences)} sequences to corpus")
    
    def load(self) -> bool:
        """Load corpus from disk."""
        with self._lock:
            if not self.corpus_path.exists():
                return False
            
            try:
                from ..utils import safe_torch_load
                data = safe_torch_load(self.corpus_path)
                
                self.sequences = []
                for entry in data.get('sequences', []):
                    self.sequences.append(StoredSequence(
                        vector=entry['vector'],
                        length=entry['length'],
                        metadata=entry.get('metadata', {}),
                        timestamp=entry.get('timestamp', ''),
                    ))
                
                logger.info(f"Loaded {len(self.sequences)} sequences from corpus")
                return True
            except Exception as e:
                logger.warning(f"Failed to load corpus: {e}")
                return False
    
    @staticmethod
    def _cosine_sim(a: torch.Tensor, b: torch.Tensor) -> float:
        norm_a = torch.norm(a)
        norm_b = torch.norm(b)
        # Guard against zero vectors
        if norm_a.item() < ZERO_NORM_THRESHOLD or norm_b.item() < ZERO_NORM_THRESHOLD:
            return 0.0
        return float((a @ b) / (norm_a * norm_b + ZERO_NORM_THRESHOLD))
    
    def __len__(self):
        return len(self.sequences)


class NextTurnPredictor:
    """
    Predict the next turn in a conversation.
    
    Uses the sequence corpus to find similar conversations
    and predict what comes next.
    """
    
    def __init__(self, encoder=None, corpus: Optional[SequenceCorpus] = None):
        """
        Initialize predictor.
        
        Args:
            encoder: TemporalEncoder instance
            corpus: SequenceCorpus (creates new if None)
        """
        self.encoder = encoder
        self.corpus = corpus or SequenceCorpus()
        
        self.last_prediction: Optional[torch.Tensor] = None
        self.prediction_confidence: float = 0.0
        
        self.stats = {
            'predictions_made': 0,
            'cache_hits': 0,
            'avg_confidence': 0.0,
            'surprises': [],
        }
    
    def predict_next_turn(
        self,
        current_turns: List[torch.Tensor],
        return_top_k: int = 3,
    ) -> Optional[Tuple[torch.Tensor, float, List[Dict]]]:
        """
        Predict the next turn given current conversation.
        
        Args:
            current_turns: List of turn vectors so far
            return_top_k: Number of candidate predictions
        
        Returns:
            (predicted_vector, confidence, candidates) or None
        """
        if not current_turns or len(current_turns) < 1:
            return None
        
        if self.encoder is None:
            logger.warning("No encoder available")
            return None
        
        partial_seq = self.encoder.encode_sequence(current_turns)
        
        similar = self.corpus.find_similar(
            partial_seq.vector,
            min_length=len(current_turns) + 1,
            top_k=return_top_k * 2,
        )
        
        if not similar:
            return None
        
        candidates = []
        next_pos = len(current_turns)
        
        for seq, sim in similar:
            if seq.length <= next_pos:
                continue
            
            predicted = self.encoder.unbind(
                seq.vector,
                self.encoder.position_vectors[next_pos]
            )
            
            candidates.append({
                'vector': predicted,
                'similarity': sim,
                'source_length': seq.length,
                'metadata': seq.metadata,
            })
        
        if not candidates:
            return None
        
        best = candidates[0]
        self.last_prediction = best['vector']
        self.prediction_confidence = best['similarity']
        
        self.stats['predictions_made'] += 1
        n = self.stats['predictions_made']
        self.stats['avg_confidence'] = (
            (self.stats['avg_confidence'] * (n-1) + best['similarity']) / n
        )
        
        return (best['vector'], best['similarity'], candidates[:return_top_k])
    
    def compute_surprise(
        self,
        actual_turn: torch.Tensor,
    ) -> float:
        """Compute surprise for the actual turn vs prediction."""
        if self.last_prediction is None:
            return 1.0
        
        surprise = self.encoder.compute_surprise(self.last_prediction, actual_turn)
        self.stats['surprises'].append(surprise)
        
        self.last_prediction = None
        
        return surprise
    
    def add_to_corpus(
        self,
        turns: List[torch.Tensor],
        metadata: Optional[Dict] = None,
    ):
        """Add a completed conversation to the corpus."""
        if len(turns) < 2:
            return
        
        sequence = self.encoder.encode_sequence(turns, metadata)
        self.corpus.add(sequence.vector, sequence.length, metadata)
