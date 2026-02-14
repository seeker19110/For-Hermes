#!/usr/bin/env python3
"""
Temporal Sequence Encoder — Frontier 5
=======================================

Encode conversation sequences as single VSA vectors that preserve order.
Enables prediction: given turns 1-3, predict turn 4.

Mechanism: Chained VSA bindings with temporal position vectors.

Author: NIMA Project
Date: 2026
"""

import threading
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)

from ..config import ZERO_NORM_THRESHOLD


@dataclass
class TemporalConfig:
    """Configuration for temporal encoding."""
    dimension: int = 50000
    max_positions: int = 20  # Max sequence length
    sparsity: float = 0.01   # 1% sparsity for position vectors
    seed: int = 42


@dataclass
class SequenceEncoding:
    """A temporally-encoded sequence."""
    vector: torch.Tensor          # The combined sequence vector
    length: int                   # Number of turns encoded
    turn_vectors: List[torch.Tensor]  # Individual turn vectors (for reference)
    metadata: Optional[Dict] = None


class TemporalEncoder:
    """
    Encode sequences with temporal position binding.
    
    Each turn in a conversation is bound to its position vector,
    then all are superposed into a single sequence vector.
    """
    
    def __init__(self, config: Optional[TemporalConfig] = None):
        """Initialize temporal encoder."""
        self.config = config or TemporalConfig()
        self.position_vectors: List[torch.Tensor] = []
        self._initialize_positions()
    
    def _initialize_positions(self):
        """Generate fixed position vectors T₁...T_K."""
        torch.manual_seed(self.config.seed)
        
        D = self.config.dimension
        K = int(D * self.config.sparsity)
        
        for i in range(self.config.max_positions):
            vec = torch.zeros(D)
            indices = torch.randperm(D)[:K]
            vec[indices] = torch.randn(K)
            vec = vec / torch.norm(vec)
            self.position_vectors.append(vec)
        
        logger.info(f"Initialized {len(self.position_vectors)} temporal position vectors")
    
    def bind(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        """Circular convolution binding (FFT-based)."""
        fa = torch.fft.fft(a.to(torch.complex64))
        fb = torch.fft.fft(b.to(torch.complex64))
        result = torch.fft.ifft(fa * fb).real
        norm = torch.norm(result)
        if norm > 1e-10:
            result = result / norm
        return result
    
    def unbind(self, bound: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
        """Unbind via correlation (inverse of bind)."""
        fb = torch.fft.fft(bound.to(torch.complex64))
        fk = torch.fft.fft(key.to(torch.complex64))
        result = torch.fft.ifft(fb * torch.conj(fk)).real
        norm = torch.norm(result)
        if norm > 1e-10:
            result = result / norm
        return result
    
    def encode_sequence(
        self,
        turn_vectors: List[torch.Tensor],
        metadata: Optional[Dict] = None,
    ) -> SequenceEncoding:
        """
        Encode a sequence of turns into a single temporal vector.
        
        Args:
            turn_vectors: List of memory vectors in order
            metadata: Optional metadata about the sequence
        
        Returns:
            SequenceEncoding with combined vector
        """
        if len(turn_vectors) > self.config.max_positions:
            raise ValueError(
                f"Sequence length {len(turn_vectors)} exceeds max {self.config.max_positions}"
            )
        
        if not turn_vectors:
            raise ValueError("Cannot encode empty sequence")
        
        sequence_vector = torch.zeros(self.config.dimension)
        
        for i, turn_vec in enumerate(turn_vectors):
            if isinstance(turn_vec, np.ndarray):
                turn_vec = torch.from_numpy(turn_vec)
            
            bound = self.bind(self.position_vectors[i], turn_vec)
            sequence_vector += bound
        
        sequence_vector = sequence_vector / torch.norm(sequence_vector)
        
        return SequenceEncoding(
            vector=sequence_vector,
            length=len(turn_vectors),
            turn_vectors=turn_vectors,
            metadata=metadata,
        )
    
    def predict_next(
        self,
        sequence: SequenceEncoding,
        position: Optional[int] = None,
    ) -> torch.Tensor:
        """
        Predict the next turn in a sequence.
        
        Args:
            sequence: The encoded sequence
            position: Position to predict (default: sequence.length)
        
        Returns:
            Predicted turn vector
        """
        if position is None:
            position = sequence.length
        
        if position >= self.config.max_positions:
            raise ValueError(f"Cannot predict position {position} (max: {self.config.max_positions-1})")
        
        predicted = self.unbind(sequence.vector, self.position_vectors[position])
        return predicted
    
    def predict_from_partial(
        self,
        partial_turns: List[torch.Tensor],
    ) -> torch.Tensor:
        """
        Given partial sequence, predict the next turn.
        
        Args:
            partial_turns: List of turn vectors so far
        
        Returns:
            Predicted next-turn vector
        """
        sequence = self.encode_sequence(partial_turns)
        return self.predict_next(sequence)
    
    def compute_surprise(
        self,
        predicted: torch.Tensor,
        actual: torch.Tensor,
    ) -> float:
        """
        Compute surprise (prediction error) for a turn.
        
        Surprise = 1 - cosine(predicted, actual)
        
        High surprise → novel, unexpected turn
        Low surprise → predicted correctly
        """
        norm_p = torch.norm(predicted)
        norm_a = torch.norm(actual)
        
        # Guard against zero vectors
        if norm_p < ZERO_NORM_THRESHOLD or norm_a < ZERO_NORM_THRESHOLD:
            return 1.0
        
        similarity = float((predicted @ actual) / (norm_p * norm_a + ZERO_NORM_THRESHOLD))
        surprise = 1.0 - similarity
        
        return surprise
    
    def get_position_vector(self, position: int) -> torch.Tensor:
        """Get the position vector for a specific position."""
        if position >= len(self.position_vectors):
            raise ValueError(f"Position {position} out of range")
        return self.position_vectors[position]
    
    def save(self, path: Path):
        """Save position vectors (atomic write)."""
        from ..utils import atomic_torch_save
        atomic_torch_save({
            'position_vectors': self.position_vectors,
            'config': {
                'dimension': self.config.dimension,
                'max_positions': self.config.max_positions,
                'sparsity': self.config.sparsity,
                'seed': self.config.seed,
            }
        }, path)
    
    def load(self, path: Path):
        """Load position vectors."""
        from ..utils import safe_torch_load
        data = safe_torch_load(path)
        self.position_vectors = data['position_vectors']
        cfg = data['config']
        self.config = TemporalConfig(
            dimension=cfg['dimension'],
            max_positions=cfg['max_positions'],
            sparsity=cfg['sparsity'],
            seed=cfg['seed'],
        )


class ConversationPredictor:
    """
    High-level interface for conversation prediction.
    """
    
    def __init__(self, encoder: TemporalEncoder, embedder=None):
        """
        Initialize predictor.
        
        Args:
            encoder: TemporalEncoder for sequence operations
            embedder: Optional embedder for text → vector
        """
        self.encoder = encoder
        self.embedder = embedder
        
        self._lock = threading.RLock()
        
        self.current_turns: List[torch.Tensor] = []
        self.current_metadata: List[Dict] = []
        
        self.last_prediction: Optional[torch.Tensor] = None
        
        self.stats = {
            'predictions_made': 0,
            'total_surprise': 0.0,
            'cache_hits': 0,
        }
    
    def add_turn(self, turn_vector: torch.Tensor, metadata: Optional[Dict] = None):
        """Add a new turn to the current conversation."""
        with self._lock:
            if self.last_prediction is not None:
                surprise = self.encoder.compute_surprise(self.last_prediction, turn_vector)
                self.stats['total_surprise'] += surprise
                self.stats['predictions_made'] += 1
                self.last_prediction = None
            
            self.current_turns.append(turn_vector)
            self.current_metadata.append(metadata or {})
            
            max_len = self.encoder.config.max_positions - 1
            if len(self.current_turns) > max_len:
                self.current_turns = self.current_turns[-max_len:]
                self.current_metadata = self.current_metadata[-max_len:]
    
    def predict_next(self) -> Optional[torch.Tensor]:
        """Predict the next turn based on current conversation."""
        with self._lock:
            if len(self.current_turns) < 1:
                return None
            
            prediction = self.encoder.predict_from_partial(self.current_turns)
            self.last_prediction = prediction
            
            return prediction
    
    def get_average_surprise(self) -> float:
        """Get average surprise across all predictions."""
        with self._lock:
            if self.stats['predictions_made'] == 0:
                return 0.0
            return self.stats['total_surprise'] / self.stats['predictions_made']
    
    def reset_conversation(self):
        """Clear the current conversation buffer."""
        with self._lock:
            self.current_turns = []
            self.current_metadata = []
            self.last_prediction = None
    
    def get_sequence_encoding(self) -> Optional[SequenceEncoding]:
        """Get the encoding of the current conversation."""
        with self._lock:
            if not self.current_turns:
                return None
            return self.encoder.encode_sequence(self.current_turns)
