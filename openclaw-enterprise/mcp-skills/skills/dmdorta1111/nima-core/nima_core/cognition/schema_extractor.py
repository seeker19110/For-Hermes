#!/usr/bin/env python3
"""
Schema Extractor for NIMA Memory System
========================================

Production implementation of schema extraction via Hopfield dynamics.

Core insight: Global superposition of related memories, combined with noisy
Hopfield dynamics, produces stable attractors that represent domain schemas
without requiring LLM-based summarization.

Author: NIMA Project
Date: 2026
"""

import torch
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from datetime import datetime
from pathlib import Path
import json
import os
from ..config import ZERO_NORM_THRESHOLD


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class SchemaConfig:
    """Configuration for schema extraction."""
    
    # Hopfield parameters
    vsa_dimension: int = 10000
    sparsity_k: int = 100  # 1% sparsity for individual memories
    schema_sparsity_k: int = 300  # 3% for schemas (superposed roles)
    
    # Temperature schedule
    temperature_schedule: str = 'annealing'  # 'fixed', 'annealing', 'adaptive'
    temp_start: float = 0.8
    temp_end: float = 0.1
    
    # Noise parameters
    noise_scale: float = 0.3
    noise_schedule: str = 'fixed'  # 'fixed', 'decreasing', 'adaptive'
    
    # Convergence
    max_steps: int = 50
    convergence_threshold: float = 0.01
    early_stopping: bool = True
    
    # Multi-pass consolidation
    num_replays: int = 50  # Simulates biological replay events
    replay_averaging: bool = True
    
    # Validation
    min_distinctness: float = 0.3  # Schema should be <0.3 similar to any memory
    min_generalization: float = 0.6  # Should recognize novel instances


@dataclass
class Schema:
    """A consolidated schema extracted from memories."""
    
    # Core representation
    vector: torch.Tensor  # VSA hypervector
    
    # Metadata
    theme: str
    source_memory_ids: List[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Quality metrics
    strength: float = 0.0  # Based on memory count and coherence
    distinctness: float = 0.0  # How different from individual memories
    generalization: float = 0.0  # How well it recognizes novel instances
    
    # Convergence info
    convergence_steps: int = 0
    energy_trajectory: List[float] = field(default_factory=list)
    
    # Optional components (if role-filler binding used)
    components: Optional[Dict[str, torch.Tensor]] = None
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary (for storage)."""
        return {
            'theme': self.theme,
            'source_memory_ids': self.source_memory_ids,
            'created_at': self.created_at,
            'strength': float(self.strength),
            'distinctness': float(self.distinctness),
            'generalization': float(self.generalization),
            'convergence_steps': self.convergence_steps,
            'energy_trajectory': [float(e) for e in self.energy_trajectory],
        }
    
    def __repr__(self):
        return (f"Schema(theme='{self.theme}', strength={self.strength:.2f}, "
                f"distinctness={self.distinctness:.2f}, "
                f"memories={len(self.source_memory_ids)})")


@dataclass
class MemoryCluster:
    """A thematically related cluster of memories."""
    
    theme: str
    memory_ids: List[str]
    memory_vectors: List[torch.Tensor]
    coherence: float = 0.0  # Average pairwise similarity


# =============================================================================
# Modern Hopfield Network
# =============================================================================

class SparseHopfield:
    """
    Modern Hopfield network for sparse VSA patterns.
    
    Uses softmax attention with temperature control for pattern completion.
    Based on "Hopfield Networks is All You Need" (Ramsauer et al., 2020).
    """
    
    def __init__(self, patterns: torch.Tensor, config: SchemaConfig):
        """
        Initialize Hopfield network.
        
        Args:
            patterns: Tensor of shape (N, D) - stored memory patterns
            config: Schema extraction configuration
        """
        self.patterns = patterns
        self.config = config
        self.N, self.D = patterns.shape
        
        assert self.D == config.vsa_dimension, \
            f"Pattern dimension {self.D} != config dimension {config.vsa_dimension}"
    
    def energy(self, state: torch.Tensor) -> torch.Tensor:
        """
        Compute Hopfield energy for a state.
        
        Modern Hopfield: E = -log(sum(exp(beta * <state, pattern>)))
        """
        similarities = state @ self.patterns.T
        similarities = torch.clamp(similarities, min=-20.0, max=20.0)  # Prevent overflow
        beta = 1.0
        return -torch.logsumexp(beta * similarities, dim=-1)
    
    def temperature_at_step(self, step: int) -> float:
        """Get temperature for current step."""
        if self.config.temperature_schedule == 'fixed':
            return self.config.temp_start
        
        elif self.config.temperature_schedule == 'annealing':
            progress = step / self.config.max_steps
            log_start = np.log(self.config.temp_start)
            log_end = np.log(self.config.temp_end)
            log_temp = log_start + progress * (log_end - log_start)
            return np.exp(log_temp)
        
        elif self.config.temperature_schedule == 'adaptive':
            progress = step / self.config.max_steps
            temp_range = self.config.temp_start - self.config.temp_end
            decay = temp_range * (1 - progress) ** 2
            return self.config.temp_end + decay
        
        return 0.1
    
    def update_step(self, state: torch.Tensor, temperature: float) -> torch.Tensor:
        """Single Hopfield update step."""
        similarities = state @ self.patterns.T
        attention = torch.softmax(similarities / temperature, dim=-1)
        new_state = attention @ self.patterns
        new_state = self._sparsify(new_state, self.config.schema_sparsity_k)
        return new_state
    
    def update(self, initial_state: torch.Tensor, 
               steps: Optional[int] = None,
               verbose: bool = False) -> Tuple[torch.Tensor, List[float]]:
        """
        Run Hopfield dynamics to find attractor.
        
        Returns:
            (final_state, energy_trajectory)
        """
        if steps is None:
            steps = self.config.max_steps
        
        current = initial_state.clone()
        energies = [self.energy(current).item()]
        
        for step in range(steps):
            temp = self.temperature_at_step(step)
            new_state = self.update_step(current, temp)
            energy = self.energy(new_state).item()
            energies.append(energy)
            
            energy_change = abs(energies[-1] - energies[-2])
            if self.config.early_stopping and energy_change < self.config.convergence_threshold:
                if verbose:
                    print(f"   Converged at step {step+1} (ΔE={energy_change:.6f})")
                break
            
            current = new_state
        
        if verbose and step == steps - 1:
            print(f"   Max steps reached (ΔE={energy_change:.6f})")
        
        return current, energies
    
    @staticmethod
    def _sparsify(x: torch.Tensor, k: int) -> torch.Tensor:
        """Keep only top-k values by magnitude."""
        if x.dim() == 1:
            x = x.unsqueeze(0)
            squeeze = True
        else:
            squeeze = False
        
        sparse = torch.zeros_like(x)
        _, indices = torch.topk(torch.abs(x), k, dim=-1)
        sparse.scatter_(-1, indices, x.gather(-1, indices))
        
        if squeeze:
            sparse = sparse.squeeze(0)
        
        return sparse


# =============================================================================
# Schema Extractor
# =============================================================================

class SchemaExtractor:
    """
    Extract schemas from episodic memories via Hopfield dynamics.
    
    This is the main production class for consolidation-based schema extraction.
    """
    
    def __init__(self, config: Optional[SchemaConfig] = None):
        """
        Initialize schema extractor.
        
        Args:
            config: Configuration (uses defaults if None)
        """
        self.config = config or SchemaConfig()
        self.stats = {
            'schemas_extracted': 0,
            'total_replays': 0,
            'avg_convergence_steps': 0.0,
        }
    
    def extract_schema(self, 
                      memories: List[torch.Tensor],
                      theme: str = "unknown",
                      memory_ids: Optional[List[str]] = None,
                      verbose: bool = False) -> Schema:
        """
        Extract a schema from a collection of memories using global superposition.
        
        Uses Hopfield dynamics with noisy replay to find stable attractors that
        represent domain patterns. This method has been validated and is the
        recommended approach for schema extraction.
        
        Args:
            memories: List of VSA memory vectors (minimum 3)
            theme: Thematic label for the schema
            memory_ids: IDs of source memories (for tracking)
            verbose: Print extraction details
        
        Returns:
            Schema object with consolidated pattern
        """
        if len(memories) < 3:
            raise ValueError(f"Need at least 3 memories for schema extraction (got {len(memories)})")
        
        if memory_ids is None:
            memory_ids = [f"mem_{i}" for i in range(len(memories))]
        
        if verbose:
            print(f"\n🧠 Extracting schema: {theme}")
            print(f"   Memories: {len(memories)}")
        
        return self._extract_global_schema(memories, theme, memory_ids, verbose)
    
    def _extract_global_schema(self,
                              memories: List[torch.Tensor],
                              theme: str,
                              memory_ids: List[str],
                              verbose: bool) -> Schema:
        """Global superposition method (RECOMMENDED)."""
        memory_tensors = torch.stack(memories)
        hopfield = SparseHopfield(memory_tensors, self.config)
        
        if verbose:
            print(f"   Hopfield network: {hopfield.N} patterns, D={hopfield.D}")
        
        superposition = torch.mean(memory_tensors, dim=0)
        
        if self.config.replay_averaging:
            replays = self._multi_pass_replay(
                hopfield, superposition, verbose=verbose
            )
            schema_vector = torch.mean(torch.stack(replays), dim=0)
            schema_vector = hopfield._sparsify(schema_vector, self.config.schema_sparsity_k)
            # Get energies for schema metadata (convergence tracking)
            _, energies = hopfield.update(
                superposition + self._get_noise(superposition),
                verbose=False
            )
        else:
            noisy_superposition = superposition + self._get_noise(superposition)
            schema_vector, energies = hopfield.update(
                noisy_superposition, verbose=verbose
            )
        
        schema = Schema(
            vector=schema_vector,
            theme=theme,
            source_memory_ids=memory_ids,
            energy_trajectory=energies,
            convergence_steps=len(energies) - 1
        )
        
        schema.strength = self._calculate_strength(schema, memory_tensors)
        schema.distinctness = self._calculate_distinctness(schema, memory_tensors)
        
        if verbose:
            print(f"   ✓ Schema extracted:")
            print(f"     - Strength: {schema.strength:.3f}")
            print(f"     - Distinctness: {schema.distinctness:.3f}")
            print(f"     - Convergence: {schema.convergence_steps} steps")
            print(f"     - Energy: {energies[0]:.2f} → {energies[-1]:.2f}")
        
        self.stats['schemas_extracted'] += 1
        self.stats['avg_convergence_steps'] = (
            (self.stats['avg_convergence_steps'] * (self.stats['schemas_extracted'] - 1)
             + schema.convergence_steps) / self.stats['schemas_extracted']
        )
        
        return schema
    
    def _multi_pass_replay(self,
                          hopfield: SparseHopfield,
                          superposition: torch.Tensor,
                          verbose: bool = False) -> List[torch.Tensor]:
        """Simulate multiple sharp-wave ripples for robust schema extraction."""
        replays = []
        
        if verbose:
            print(f"   Running {self.config.num_replays} replay passes...")
        
        for replay_num in range(self.config.num_replays):
            noise = self._get_noise(superposition, replay_num)
            noisy_state = superposition + noise
            attractor, _ = hopfield.update(noisy_state, verbose=False)
            replays.append(attractor)
            
            if len(replays) >= 10:
                recent_var = torch.var(torch.stack(replays[-10:]), dim=0).mean()
                if recent_var < 0.001:
                    if verbose:
                        print(f"   Stable after {replay_num + 1} replays")
                    break
        
        self.stats['total_replays'] += len(replays)
        
        return replays
    
    def _get_noise(self, 
                   state: torch.Tensor, 
                   replay_num: Optional[int] = None) -> torch.Tensor:
        """Generate noise for replay."""
        base_noise = torch.randn_like(state) * self.config.noise_scale
        
        if self.config.noise_schedule == 'decreasing' and replay_num is not None:
            scale = 1.0 - (replay_num / self.config.num_replays)
            base_noise *= scale
        
        state_norm = torch.norm(state)
        if state_norm > 0:
            base_noise *= state_norm
        
        return base_noise
    
    def _calculate_strength(self, 
                           schema: Schema,
                           memories: torch.Tensor) -> float:
        """Calculate schema strength."""
        count_factor = min(len(schema.source_memory_ids) / 20, 1.0)
        
        sims = []
        for i in range(len(memories)):
            for j in range(i + 1, len(memories)):
                sim = self._cosine_sim(memories[i], memories[j])
                sims.append(sim)
        
        coherence = np.mean(sims) if sims else 0.5
        
        energy_drop = abs(schema.energy_trajectory[-1] - schema.energy_trajectory[0])
        convergence_factor = min(energy_drop / 500, 1.0)
        
        strength = 0.4 * count_factor + 0.4 * coherence + 0.2 * convergence_factor
        return float(strength)
    
    def _calculate_distinctness(self,
                               schema: Schema,
                               memories: torch.Tensor) -> float:
        """Calculate distinctness."""
        sims = []
        for mem in memories:
            sim = self._cosine_sim(schema.vector, mem)
            sims.append(sim)
        
        distinctness = 1.0 - np.mean(sims)
        return float(distinctness)
    
    def validate_schema(self,
                       schema: Schema,
                       training_memories: List[torch.Tensor],
                       test_in_domain: List[torch.Tensor],
                       test_out_domain: List[torch.Tensor]) -> Dict:
        """Validate schema quality."""
        train_sims = [self._cosine_sim(schema.vector, m) for m in training_memories]
        distinctness = 1.0 - np.mean(train_sims)
        
        in_sims = [self._cosine_sim(schema.vector, m) for m in test_in_domain]
        out_sims = [self._cosine_sim(schema.vector, m) for m in test_out_domain]
        
        generalization_ratio = np.mean(in_sims) / (np.mean(out_sims) + 1e-6)
        
        threshold = (np.mean(in_sims) + np.mean(out_sims)) / 2
        correct = sum(s > threshold for s in in_sims) + sum(s < threshold for s in out_sims)
        accuracy = correct / (len(in_sims) + len(out_sims))
        
        metrics = {
            'distinctness': float(distinctness),
            'generalization_ratio': float(generalization_ratio),
            'accuracy': float(accuracy),
            'in_domain_sim_mean': float(np.mean(in_sims)),
            'out_domain_sim_mean': float(np.mean(out_sims)),
            'passes_distinctness': distinctness >= self.config.min_distinctness,
            'passes_generalization': generalization_ratio >= self.config.min_generalization,
        }
        
        schema.distinctness = distinctness
        schema.generalization = generalization_ratio
        
        return metrics
    
    def consolidate_cluster(self, cluster: MemoryCluster, verbose: bool = False) -> Schema:
        """Consolidate a memory cluster into a schema."""
        return self.extract_schema(
            memories=cluster.memory_vectors,
            theme=cluster.theme,
            memory_ids=cluster.memory_ids,
            verbose=verbose
        )
    
    @staticmethod
    def _cosine_sim(a: torch.Tensor, b: torch.Tensor) -> float:
        """Compute cosine similarity."""
        norm_a = torch.norm(a)
        norm_b = torch.norm(b)
        # Guard against zero vectors
        if norm_a < ZERO_NORM_THRESHOLD or norm_b < ZERO_NORM_THRESHOLD:
            return 0.0
        return float((a @ b) / (norm_a * norm_b + ZERO_NORM_THRESHOLD))
    
    def get_stats(self) -> Dict:
        """Get extraction statistics."""
        return self.stats.copy()
    
    def save_schema(self, schema: Schema, path: Path):
        """Save schema to disk (atomic writes)."""
        from ..utils import atomic_json_save, atomic_torch_save
        path.mkdir(parents=True, exist_ok=True)
        metadata_path = path / f"schema_{schema.theme}.json"
        atomic_json_save(schema.to_dict(), metadata_path)
        
        vector_path = path / f"schema_{schema.theme}.pt"
        atomic_torch_save(schema.vector, vector_path)
    
    def load_schema(self, path: Path, theme: str) -> Schema:
        """Load schema from disk."""
        metadata_path = path / f"schema_{theme}.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        vector_path = path / f"schema_{theme}.pt"
        from ..utils import safe_torch_load
        vector = safe_torch_load(vector_path)
        
        schema = Schema(
            vector=vector,
            theme=metadata['theme'],
            source_memory_ids=metadata['source_memory_ids'],
            created_at=metadata['created_at'],
            strength=metadata['strength'],
            distinctness=metadata['distinctness'],
            generalization=metadata.get('generalization', 0.0),
            convergence_steps=metadata['convergence_steps'],
            energy_trajectory=metadata['energy_trajectory'],
        )
        
        return schema


def create_memory_cluster(memory_ids: List[str],
                         memory_vectors: List[torch.Tensor],
                         theme: str = "unknown") -> MemoryCluster:
    """Create a memory cluster from vectors."""
    sims = []
    for i in range(len(memory_vectors)):
        for j in range(i + 1, len(memory_vectors)):
            a = memory_vectors[i]
            b = memory_vectors[j]
            norm_a = torch.norm(a)
            norm_b = torch.norm(b)
            if norm_a > 0 and norm_b > 0:
                sim = (a @ b) / (norm_a * norm_b)
                sims.append(float(sim))
    
    coherence = float(np.mean(sims)) if sims else 0.0
    
    return MemoryCluster(
        theme=theme,
        memory_ids=memory_ids,
        memory_vectors=memory_vectors,
        coherence=coherence
    )
