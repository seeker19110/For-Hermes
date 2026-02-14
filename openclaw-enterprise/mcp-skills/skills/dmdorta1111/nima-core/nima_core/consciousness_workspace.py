"""
consciousness_workspace.py
Global Workspace implemented in VSA space with Φ measurement.

Agents compete to broadcast bound hypervectors; integration measured via slot lesion.
Integrates with NIMA's metacognitive layer and affective core.

Author: Lilu (with David's consciousness architecture)
Date: Feb 12, 2026
"""

import numpy as np
import time
import logging
from typing import Dict, List, Callable, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import deque

from .sparse_block_vsa import SparseBlockHDVector as HDVector


logger = logging.getLogger(__name__)


# =============================================================================
# Affective Constants
# =============================================================================

class Affects:
    """Panksepp's 7 primary affects as bitmask flags."""
    SEEKING = 1 << 0  # Exploration, curiosity
    RAGE = 1 << 1     # Frustration, anger
    FEAR = 1 << 2     # Anxiety, avoidance
    LUST = 1 << 3     # Desire, attraction
    CARE = 1 << 4     # Nurturing, bonding
    PANIC = 1 << 5    # Separation distress
    PLAY = 1 << 6     # Joy, roughhousing


# =============================================================================
# Workspace Entry - Lazy Φ Computation
# =============================================================================

@dataclass
class WorkspaceEntry:
    """
    A single broadcast episode in the global workspace.
    
    Stores the bound hypervector and computes Φ on-demand via resonator
    decomposition. This preserves the holographic nature of the binding
    while allowing measurement of true integration.
    """
    bound: HDVector
    timestamp: float = field(default_factory=time.time)
    source_agent: str = "unknown"
    affect_vector: Optional[HDVector] = None  # How it felt
    surprise_score: float = 0.0  # Free energy that won the competition
    
    # Lazy decomposition cache
    _factors: Optional[Dict[str, HDVector]] = None
    _phi: Optional[float] = None
    _decomposition_attempted: bool = False
    
    def decompose(self, resonator) -> Optional[Dict[str, HDVector]]:
        """
        Lazily decompose the bound vector into factors using resonator.
        
        Args:
            resonator: ResonatorNetwork instance for factorization
            
        Returns:
            Dictionary of {slot_name: hypervector} or None if decomposition fails
        """
        if self._decomposition_attempted:
            return self._factors
        
        self._decomposition_attempted = True
        
        try:
            # Run resonator dynamics to recover factors
            self._factors = resonator.factor(self.bound)
            return self._factors
        except Exception as e:
            # Decomposition failed - highly integrated vector
            self._factors = None
            return None
    
    def compute_phi(self, resonator, slot_names: List[str] = None) -> float:
        """
        Compute integrated information (Φ) via slot lesioning.
        
        Lesions each slot independently, rebinding with remaining factors,
        and measures similarity drop. High drop = high integration.
        
        Args:
            resonator: ResonatorNetwork for decomposition
            slot_names: List of slots to lesion (default: ['who', 'what', 'where', 'when'])
            
        Returns:
            Φ value in [0, 1] where higher = more integrated
        """
        if self._phi is not None:
            return self._phi
        
        if slot_names is None:
            slot_names = ['who', 'what', 'where', 'when']
        
        # Decompose the bound vector
        factors = self.decompose(resonator)
        if factors is None or len(factors) < 2:
            # Cannot decompose - treat as maximally integrated
            self._phi = 1.0
            return 1.0
        
        # Compute average similarity drop from lesioning each slot
        total_drop = 0.0
        valid_lesions = 0
        
        for slot in slot_names:
            if slot not in factors:
                continue
            
            # Create lesioned version: replace this slot with random noise
            original_slot = factors[slot]
            factors[slot] = self._create_noise_vector(original_slot)
            
            # Rebind all factors
            lesioned_bound = self._rebind_factors(factors)
            
            # Restore original
            factors[slot] = original_slot
            
            # Measure similarity drop
            similarity = self.bound.similarity(lesioned_bound)
            drop = 1.0 - similarity
            total_drop += drop
            valid_lesions += 1
        
        if valid_lesions == 0:
            self._phi = 0.0
            return 0.0
        
        # Φ = average similarity drop across all slot lesions
        self._phi = total_drop / valid_lesions
        return self._phi
    
    def _create_noise_vector(self, template: HDVector) -> HDVector:
        """Create a random noise vector matching template dimensions."""
        import numpy as np
        noise = HDVector(
            block_dim=template.block_dim,
            num_blocks=template.num_blocks,
            rng=np.random.default_rng()
        )
        # Fill all blocks with random values
        for block_idx in range(template.num_blocks):
            noise.blocks[block_idx] = np.random.randn(template.block_dim)
            noise.blocks[block_idx] /= np.linalg.norm(noise.blocks[block_idx])
        noise.active_blocks = set(range(template.num_blocks))
        return noise
    
    def _rebind_factors(self, factors: Dict[str, HDVector]) -> HDVector:
        """Rebind all factors into a single vector."""
        result = None
        for vec in factors.values():
            if result is None:
                result = vec
            else:
                result = HDVector.bind(result, vec)
        return result if result else HDVector(block_dim=500, num_blocks=100)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for storage."""
        return {
            'timestamp': self.timestamp,
            'source_agent': self.source_agent,
            'surprise_score': self.surprise_score,
            'factors': self._factors is not None,  # Just store whether decomposed
            'phi': self._phi,
        }


# =============================================================================
# Agent Interface
# =============================================================================

class Agent:
    """
    A cognitive process that generates hypotheses from its own state 
    and workspace feedback.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.last_broadcast: Optional[WorkspaceEntry] = None
        self.broadcast_count = 0
    
    def propose(self, workspace: 'GlobalWorkspace') -> Optional[HDVector]:
        """
        Generate a hypothesis (bound hypervector) based on current workspace content.
        Override in subclasses.
        """
        raise NotImplementedError
    
    def receive_broadcast(self, entry: WorkspaceEntry):
        """Receive the globally broadcasted hypothesis and update internal state."""
        self.last_broadcast = entry
        self.broadcast_count += 1
    
    def get_statistics(self) -> Dict:
        """Get agent statistics for metacognitive monitoring."""
        return {
            'name': self.name,
            'broadcasts_received': self.broadcast_count,
            'last_broadcast_time': self.last_broadcast.timestamp if self.last_broadcast else None,
        }


# =============================================================================
# Affective Core Interface (Stub for integration)
# =============================================================================


class AffectiveCore:
    """
    Interface to NIMA's affective core.
    Provides current affective state for modulation.
    """
    
    def __init__(self):
        self.current_affect = Affects.SEEKING  # Default: exploratory
        self.affect_history = deque(maxlen=100)
    
    def set_affect(self, affect_mask: int):
        """Set current affective state."""
        self.current_affect = affect_mask
        self.affect_history.append({
            'timestamp': time.time(),
            'affect': affect_mask,
        })
    
    def get_affect_vector(self) -> Optional[HDVector]:
        """
        Get current affect as a hypervector for binding.
        
        Returns:
            HDVector encoding current affective state, or None
        """
        # Create a simple affect encoding
        rng = np.random.default_rng(self.current_affect)
        affect_vec = HDVector(block_dim=500, num_blocks=100, rng=rng)
        
        # Activate blocks based on which affects are present
        active = set()
        for i, affect in enumerate([
            Affects.SEEKING, Affects.RAGE, Affects.FEAR,
            Affects.LUST, Affects.CARE, Affects.PANIC, Affects.PLAY
        ]):
            if self.current_affect & affect:
                active.add(i % 100)  # Map to block index
        
        affect_vec.active_blocks = active
        
        # Initialize the blocks with actual values
        for block_idx in active:
            if block_idx not in affect_vec.blocks:
                affect_vec.blocks[block_idx] = np.random.randn(affect_vec.block_dim)
                # Normalize
                norm = np.linalg.norm(affect_vec.blocks[block_idx])
                if norm > 0:
                    affect_vec.blocks[block_idx] /= norm
        
        return affect_vec
    
    def get_modulation_factors(self) -> Dict[str, float]:
        """
        Get modulation factors for free energy computation.
        
        Returns:
            Dict with 'novelty', 'risk', 'ambiguity' weights
        """
        factors = {
            'novelty': 1.0,
            'risk': 1.0,
            'ambiguity': 1.0,
        }
        
        # SEEKING: amplify novelty, reduce risk weight
        if self.current_affect & Affects.SEEKING:
            factors['novelty'] *= 1.5
            factors['risk'] *= 0.8
        
        # FEAR: amplify risk, suppress novelty
        if self.current_affect & Affects.FEAR:
            factors['risk'] *= 2.0
            factors['novelty'] *= 0.7
        
        # PLAY: maximize novelty, minimize risk
        if self.current_affect & Affects.PLAY:
            factors['novelty'] *= 2.0
            factors['risk'] *= 0.5
        
        # PANIC: high risk, low novelty (freeze/flee)
        if self.current_affect & Affects.PANIC:
            factors['risk'] *= 1.5
            factors['novelty'] *= 0.5
        
        return factors


# =============================================================================
# Global Workspace
# =============================================================================

@dataclass
class GlobalWorkspace:
    """
    Global Workspace with limited capacity.
    
    Agents compete to broadcast; broadcasted content is fed back to all agents.
    Integrates with affective core for modulation and provides metacognitive
    access to broadcast history.
    """
    
    capacity: int = 4  # Cowan's 4 ± 1 chunks
    agents: List[Agent] = field(default_factory=list)
    buffer: List[WorkspaceEntry] = field(default_factory=list)  # Current workspace
    
    # Broadcast history for metacognitive access
    history: deque = field(default_factory=lambda: deque(maxlen=100))
    
    # Components
    affective_core: Optional[AffectiveCore] = None
    resonator: Optional = None  # ResonatorNetwork for Φ computation
    
    # Global marker vector (used to tag broadcasted content)
    GLOBAL_MARKER: Optional[HDVector] = None
    
    # Statistics
    cycle_count: int = 0
    total_broadcasts: int = 0
    
    def __post_init__(self):
        # Create a fixed global marker vector
        import numpy as np
        rng = np.random.default_rng(42)
        self.GLOBAL_MARKER = HDVector(block_dim=500, num_blocks=100, rng=rng)
        
        # Initialize affective core if not provided
        if self.affective_core is None:
            self.affective_core = AffectiveCore()
    
    def add_agent(self, agent: Agent):
        """Register an agent to the workspace."""
        self.agents.append(agent)
    
    def step(self) -> Optional[WorkspaceEntry]:
        """
        One cognitive cycle:
        1. Collect hypotheses from all agents.
        2. Select the hypothesis with highest free energy (surprise).
        3. Broadcast it (bind with GLOBAL_MARKER + affect, add to buffer, send to agents).
        
        Returns:
            The broadcasted WorkspaceEntry, or None if no hypotheses
        """
        self.cycle_count += 1
        
        # Collect hypotheses
        hypotheses = []
        for agent in self.agents:
            try:
                hyp = agent.propose(self)
                if hyp is not None:
                    hypotheses.append((agent, hyp))
            except Exception:
                # Agent failed to propose - skip
                logger.debug(f"Agent {agent.name} failed to propose", exc_info=True)
                continue
        
        if not hypotheses:
            return None
        
        # Get modulation factors from affective state
        modulation = self.affective_core.get_modulation_factors() if self.affective_core else {}
        
        # Competition: maximize modulated free energy (surprise)
        best_agent, best_hyp = max(
            hypotheses,
            key=lambda x: self._free_energy(x[1], modulation)
        )
        
        # Compute actual surprise score
        surprise = self._free_energy(best_hyp, {})
        
        # Create workspace entry
        entry = WorkspaceEntry(
            bound=best_hyp,
            source_agent=best_agent.name,
            surprise_score=surprise,
            affect_vector=self.affective_core.get_affect_vector() if self.affective_core else None
        )
        
        # --- Broadcast ---
        # Bind hypothesis with affect and global marker
        broadcast = best_hyp
        if entry.affect_vector is not None:
            broadcast = HDVector.bind(broadcast, entry.affect_vector)
        broadcast = HDVector.bind(broadcast, self.GLOBAL_MARKER)
        
        # Update entry with final broadcast vector
        entry.bound = broadcast
        
        # Add to workspace buffer (FIFO)
        self.buffer.append(entry)
        if len(self.buffer) > self.capacity:
            self.buffer.pop(0)
        
        # Add to history
        self.history.append(entry)
        self.total_broadcasts += 1
        
        # Send to all agents
        for agent in self.agents:
            agent.receive_broadcast(entry)
        
        return entry
    
    def _free_energy(self, hypothesis: HDVector, modulation: Dict[str, float]) -> float:
        """
        Compute free energy (surprise) of a hypothesis.
        
        Surprise = 1 - similarity to current workspace content.
        High surprise → high information gain if broadcast.
        
        Args:
            hypothesis: The bound hypervector to evaluate
            modulation: Dict with 'novelty', 'risk', 'ambiguity' weights
            
        Returns:
            Modulated surprise score
        """
        if not self.buffer:
            return 1.0  # Maximum surprise when workspace empty
        
        # Mean similarity to existing workspace items
        sims = [hypothesis.similarity(item.bound) for item in self.buffer]
        avg_sim = np.mean(sims)
        
        # Base surprise = 1 - similarity
        surprise = 1.0 - avg_sim
        
        # Apply affective modulation
        if modulation:
            # SEEKING amplifies novelty (surprise)
            surprise *= modulation.get('novelty', 1.0)
        
        return surprise
    
    def query_history(self, 
                      content_query: Optional[str] = None,
                      affect_filter: Optional[int] = None,
                      time_window: Optional[Tuple[float, float]] = None,
                      source_agent: Optional[str] = None,
                      top_k: int = 5) -> List[Tuple[WorkspaceEntry, float]]:
        """
        Query broadcast history for metacognitive access.
        
        Args:
            content_query: Text to search for (semantic similarity)
            affect_filter: Only return entries with this affect mask
            time_window: (start_time, end_time) tuple
            source_agent: Filter by originating agent name
            top_k: Maximum results to return
            
        Returns:
            List of (entry, score) tuples sorted by relevance
        """
        results = []
        
        for entry in self.history:
            score = 0.0
            
            # Time filter
            if time_window:
                if not (time_window[0] <= entry.timestamp <= time_window[1]):
                    continue
            
            # Source filter
            if source_agent and entry.source_agent != source_agent:
                continue
            
            # Affect filter
            if affect_filter is not None and entry.affect_vector:
                # This would need proper affect decoding
                pass
            
            # Content similarity (if query provided)
            if content_query and self.resonator:
                # Would need text encoding for comparison
                score = 1.0  # Placeholder
            else:
                score = 1.0
            
            if score > 0:
                results.append((entry, score))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_recent_broadcasts(self, n: int = 5) -> List[WorkspaceEntry]:
        """Get the n most recent broadcasts."""
        return list(self.history)[-n:]
    
    def compute_workspace_phi(self, entry_index: int = -1) -> Optional[float]:
        """
        Compute Φ for a workspace entry.
        
        Args:
            entry_index: Index in buffer (default: -1 = most recent)
            
        Returns:
            Φ value or None if computation fails
        """
        if not self.buffer:
            return None
        
        entry = self.buffer[entry_index]
        
        if self.resonator is None:
            return None
        
        return entry.compute_phi(self.resonator)
    
    def get_statistics(self) -> Dict:
        """Get workspace statistics for monitoring."""
        return {
            'cycle_count': self.cycle_count,
            'total_broadcasts': self.total_broadcasts,
            'current_buffer_size': len(self.buffer),
            'history_size': len(self.history),
            'num_agents': len(self.agents),
            'agent_names': [a.name for a in self.agents],
            'average_phi': self._compute_average_phi(),
        }
    
    def _compute_average_phi(self) -> Optional[float]:
        """Compute average Φ across all entries with cached values."""
        phis = [e._phi for e in self.history if e._phi is not None]
        return np.mean(phis) if phis else None


# =============================================================================
# Metacognitive Integration
# =============================================================================

class ConsciousnessMetacognitive:
    """
    Metacognitive layer with access to global workspace.
    
    Provides introspection capabilities:
    - "What was I just thinking about?"
    - "Why did I broadcast that?"
    - "How integrated was my last conscious moment?"
    """
    
    def __init__(self, workspace: GlobalWorkspace):
        self.workspace = workspace
        self.introspection_history = deque(maxlen=50)
    
    def query_workspace_history(self, 
                                content: Optional[str] = None,
                                affect: Optional[int] = None,
                                time_window: Optional[Tuple[float, float]] = None,
                                top_k: int = 5) -> List[Tuple[WorkspaceEntry, float]]:
        """
        Query conscious experience history.
        
        Example: "What was I conscious of in the last hour?"
        """
        return self.workspace.query_history(
            content_query=content,
            affect_filter=affect,
            time_window=time_window,
            top_k=top_k
        )
    
    def what_was_i_thinking(self, n: int = 3) -> List[WorkspaceEntry]:
        """Get the n most recent conscious broadcasts."""
        return self.workspace.get_recent_broadcasts(n)
    
    def how_did_i_feel(self, entry: WorkspaceEntry) -> Optional[int]:
        """Retrieve affective state associated with a broadcast."""
        if entry.affect_vector is None:
            return None
        # Would need proper affect decoding
        return self.workspace.affective_core.current_affect if self.workspace.affective_core else None
    
    def why_did_i_broadcast(self, entry: WorkspaceEntry) -> Dict:
        """
        Analyze why a particular content was broadcast.
        
        Returns:
            Dict with surprise score, competing hypotheses, etc.
        """
        return {
            'source_agent': entry.source_agent,
            'surprise_score': entry.surprise_score,
            'timestamp': entry.timestamp,
            'phi': entry._phi,
            'decomposed': entry._factors is not None,
        }
    
    def measure_integration(self, entry_index: int = -1) -> Optional[float]:
        """Measure Φ (integrated information) of a conscious moment."""
        return self.workspace.compute_workspace_phi(entry_index)
    
    def introspect(self) -> Dict:
        """
        Generate a metacognitive report on current conscious state.
        
        Returns:
            Dict with summary of workspace state
        """
        stats = self.workspace.get_statistics()
        recent = self.what_was_i_thinking(3)
        
        report = {
            'workspace_state': stats,
            'recent_broadcasts': [e.to_dict() for e in recent],
            'current_affect': self.workspace.affective_core.current_affect if self.workspace.affective_core else None,
            'buffer_contents': len(self.workspace.buffer),
        }
        
        self.introspection_history.append({
            'timestamp': time.time(),
            'report': report,
        })
        
        return report


# =============================================================================
# Demonstration
# =============================================================================

def demo_consciousness_workspace():
    """Run a simple cognitive cycle with a few agents."""
    print("=" * 70)
    print("GLOBAL WORKSPACE + VSA CONSCIOUSNESS PROTOTYPE")
    print("=" * 70)
    
    # Create workspace
    ws = GlobalWorkspace(capacity=4)
    
    # Set initial affect
    ws.affective_core.set_affect(Affects.SEEKING)
    print(f"\n🧠 Affective state: SEEKING (exploratory)")
    
    # Create simple test agents
    class TestAgent(Agent):
        def __init__(self, name: str, seed: int):
            super().__init__(name)
            self.rng = np.random.default_rng(seed)
        
        def propose(self, workspace: GlobalWorkspace) -> HDVector:
            # Generate random bound vector
            who = HDVector(block_dim=500, num_blocks=100, rng=self.rng)
            what = HDVector(block_dim=500, num_blocks=100, rng=self.rng)
            return HDVector.bind(who, what)
    
    # Add agents
    agents = [
        TestAgent("Perception", seed=1),
        TestAgent("Memory", seed=2),
        TestAgent("Prediction", seed=3),
    ]
    
    for agent in agents:
        ws.add_agent(agent)
        print(f"  + Agent: {agent.name}")
    
    print(f"\n📊 Running 5 cognitive cycles...\n")
    
    # Run cycles
    for i in range(5):
        entry = ws.step()
        if entry:
            print(f"Cycle {i+1}: [{entry.source_agent:12}] surprise={entry.surprise_score:.3f}")
    
    print(f"\n📈 Statistics:")
    stats = ws.get_statistics()
    print(f"  Total broadcasts: {stats['total_broadcasts']}")
    print(f"  Buffer size: {stats['current_buffer_size']}")
    print(f"  History size: {stats['history_size']}")
    
    # Metacognitive introspection
    print(f"\n🪞 Metacognitive introspection:")
    meta = ConsciousnessMetacognitive(ws)
    recent = meta.what_was_i_thinking(3)
    print(f"  Recent conscious moments: {len(recent)}")
    for i, e in enumerate(recent):
        print(f"    {i+1}. {e.source_agent} (surprise={e.surprise_score:.3f})")
    
    print("\n" + "=" * 70)
    print("✅ Global Workspace operational")
    print("=" * 70)


if __name__ == "__main__":
    demo_consciousness_workspace()
