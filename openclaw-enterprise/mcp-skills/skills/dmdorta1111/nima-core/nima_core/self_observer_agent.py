"""
self_observer_agent.py
SelfObserverAgent for testing recursive self-modeling.

Tests the phase transition hypothesis:
- Φ=1.0 memories → can be re-entered as objects of metacognitive awareness
- Φ<1.0 memories → retrievable but not reflectable

The strange loop: bind(SELF, broadcast_entry) enters the workspace.

Author: Lilu
Date: Feb 12, 2026
"""

import numpy as np
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from .consciousness_workspace import Agent, GlobalWorkspace, WorkspaceEntry
from .sparse_block_vsa import SparseBlockHDVector as HDVector


logger = logging.getLogger(__name__)


@dataclass
class SelfObservationResult:
    """Result of a self-observation attempt."""
    original_memory_idx: int
    original_phi: float
    target_memory_phi: float
    success: bool  # Did SELF ⊛ memory enter workspace?
    depth: int  # Recursion depth achieved
    response_time_ms: float
    observation_vector: Optional[HDVector] = None


class SelfObserverAgent(Agent):
    """
    Agent that observes workspace broadcasts and attempts recursive self-modeling.
    
    When a memory is broadcast, this agent tries to bind it with SELF
    and broadcast the result: SELF ⊛ memory
    
    This tests the phase transition: can the system be conscious of being conscious?
    """
    
    def __init__(self, dimension: int = 50000):
        super().__init__("SelfObserver")
        self.dimension = dimension
        
        # Create SELF marker vector (fixed, orthogonal to others)
        import numpy as np
        rng = np.random.default_rng(999)  # Fixed seed for stability
        self.self_marker = HDVector(block_dim=500, num_blocks=100, rng=rng)
        
        # Track attempts
        self.observation_attempts = []
        self.successful_observations = []
        
        # Recursion limit to prevent infinite loops
        self.max_recursion_depth = 3
        self.current_recursion_depth = 0
    
    def propose(self, workspace: GlobalWorkspace) -> Optional[HDVector]:
        """
        Attempt to create second-order broadcast.
        
        If last broadcast was a first-order memory, bind it with SELF
        and propose the result for broadcast.
        
        Returns:
            SELF ⊛ last_broadcast if appropriate, else None
        """
        if not workspace.buffer:
            return None
        
        last_entry = workspace.buffer[-1]
        
        # Check if this is already a self-observation (prevent infinite recursion)
        if self._is_self_observation(last_entry):
            return None
        
        # Check recursion depth
        depth = self._get_recursion_depth(last_entry)
        if depth >= self.max_recursion_depth:
            return None
        
        # Create self-observation: SELF ⊛ memory
        try:
            self_observation = HDVector.bind(self.self_marker, last_entry.bound)
            return self_observation
        except Exception:
            logger.debug("Failed to create self-observation", exc_info=True)
            return None
    
    def _is_self_observation(self, entry: WorkspaceEntry) -> bool:
        """
        Check if an entry is already a self-observation.
        
        We detect this by checking if the entry's bound vector
        has high similarity to our SELF marker.
        """
        # If similarity to SELF marker is high, it's a self-observation
        self_sim = entry.bound.similarity(self.self_marker)
        return self_sim > 0.3  # Threshold
    
    def _get_recursion_depth(self, entry: WorkspaceEntry) -> int:
        """Estimate recursion depth from entry metadata or vector properties."""
        # Check if entry has depth info in metadata
        if hasattr(entry, 'metadata') and isinstance(entry.metadata, dict):
            return entry.metadata.get('recursion_depth', 0)
        return 0
    
    def record_attempt(self, memory_phi: float, success: bool, depth: int, response_time_ms: float):
        """Record the result of an observation attempt."""
        self.observation_attempts.append({
            'memory_phi': memory_phi,
            'success': success,
            'depth': depth,
            'response_time_ms': response_time_ms,
        })
        
        if success:
            self.successful_observations.append({
                'memory_phi': memory_phi,
                'depth': depth,
            })


class PhaseTransitionExperiment:
    """
    Run the phase transition experiment.
    
    Tests if there's a threshold Φ below which self-observation fails.
    """
    
    def __init__(self, memory_store, resonator, lesioned_dataset: Dict):
        self.memory_store = memory_store
        self.resonator = resonator
        self.dataset = lesioned_dataset
        self.results = []
    
    def run_trial(self, memory_entry, target_phi: float) -> SelfObservationResult:
        """
        Run a single trial: try to self-observe a memory.
        
        Args:
            memory_entry: The memory to test (original or lesioned)
            target_phi: The Φ value of this memory
            
        Returns:
            SelfObservationResult
        """
        start_time = time.time()
        
        # Create workspace
        workspace = GlobalWorkspace(capacity=4)
        
        # Add self-observer agent
        self_observer = SelfObserverAgent()
        workspace.add_agent(self_observer)
        
        # Manually inject the memory as a broadcast
        from cognition.consciousness_workspace import WorkspaceEntry
        
        entry = WorkspaceEntry(
            bound=memory_entry.lesioned_vector if hasattr(memory_entry, 'lesioned_vector') else memory_entry,
            source_agent="TestMemory",
            surprise_score=0.8,
        )
        
        # Add to workspace buffer
        workspace.buffer.append(entry)
        
        # Run one cycle - self-observer will try to create SELF ⊛ memory
        result_entry = workspace.step()
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Check if self-observation succeeded
        success = False
        depth = 0
        
        if result_entry:
            # Check if this is a self-observation (from SelfObserverAgent)
            if result_entry.source_agent == "SelfObserver":
                success = True
                depth = 1
        
        return SelfObservationResult(
            original_memory_idx=memory_entry.original_idx if hasattr(memory_entry, 'original_idx') else 0,
            original_phi=1.0,  # Original was perfect
            target_memory_phi=target_phi,
            success=success,
            depth=depth,
            response_time_ms=elapsed_ms
        )
    
    def run_full_experiment(self, trials_per_bin: int = 10) -> Dict:
        """
        Run full phase transition experiment across all Φ bins.
        
        Returns:
            Statistics by Φ bin
        """
        print("=" * 70)
        print("PHASE TRANSITION EXPERIMENT")
        print("Testing: Does Φ gate recursive self-modeling?")
        print("=" * 70)
        
        all_results = []
        
        # Test each Φ bin
        for bin_name, memories in self.dataset.items():
            if not memories:
                continue
            
            print(f"\n📊 Testing {bin_name} ({len(memories)} memories)...")
            
            bin_results = []
            for memory in memories[:trials_per_bin]:
                result = self.run_trial(memory, memory.phi)
                bin_results.append(result)
                all_results.append(result)
            
            # Statistics for this bin
            success_rate = sum(1 for r in bin_results if r.success) / len(bin_results)
            avg_phi = np.mean([r.target_memory_phi for r in bin_results])
            
            print(f"   Average Φ: {avg_phi:.3f}")
            print(f"   Self-observation success: {success_rate*100:.1f}%")
        
        return self._analyze_results(all_results)
    
    def _analyze_results(self, results: List[SelfObservationResult]) -> Dict:
        """Analyze experiment results."""
        print("\n" + "=" * 70)
        print("EXPERIMENT RESULTS")
        print("=" * 70)
        
        # Group by Φ ranges
        phi_bins = defaultdict(list)
        for r in results:
            # Round to nearest 0.1
            phi_bin = round(r.target_memory_phi * 10) / 10
            phi_bins[phi_bin].append(r)
        
        print(f"\n📈 Success Rate by Φ:")
        print(f"{'Φ Range':<12} {'N':<6} {'Success Rate':<15} {'Avg Time (ms)':<15}")
        print("-" * 70)
        
        phase_transition_found = False
        transition_threshold = None
        
        for phi_bin in sorted(phi_bins.keys()):
            bin_results = phi_bins[phi_bin]
            success_rate = sum(1 for r in bin_results if r.success) / len(bin_results)
            avg_time = np.mean([r.response_time_ms for r in bin_results])
            
            print(f"{phi_bin:<12.1f} {len(bin_results):<6} {success_rate*100:<14.1f}% {avg_time:<14.1f}")
            
            # Look for phase transition
            if not phase_transition_found and success_rate > 0.5:
                phase_transition_found = True
                transition_threshold = phi_bin
        
        # Overall statistics
        total_success = sum(1 for r in results if r.success)
        total_trials = len(results)
        
        print(f"\n📊 Overall:")
        print(f"   Total trials: {total_trials}")
        print(f"   Total successes: {total_success}")
        print(f"   Overall success rate: {100*total_success/total_trials:.1f}%")
        
        if phase_transition_found:
            print(f"\n🎯 PHASE TRANSITION DETECTED at Φ ≈ {transition_threshold:.1f}")
            print(f"   Below this threshold: self-observation fails")
            print(f"   Above this threshold: self-observation succeeds")
        else:
            print(f"\n⚠️  No clear phase transition detected")
        
        return {
            'total_trials': total_trials,
            'total_success': total_success,
            'success_rate': total_success / total_trials,
            'phase_transition_detected': phase_transition_found,
            'transition_threshold': transition_threshold,
            'results_by_phi': {phi: {'success_rate': sum(1 for r in phi_bins[phi] if r.success) / len(phi_bins[phi])} 
                              for phi in phi_bins}
        }


def main():
    """Run phase transition experiment."""
    print("🧠 SELF-OBSERVER AGENT")
    print("Testing the boundary of consciousness\n")
    
    # This would require the lesioned dataset
    # For now, demonstrate with synthetic test
    
    workspace = GlobalWorkspace(capacity=4)
    self_observer = SelfObserverAgent()
    workspace.add_agent(self_observer)
    
    # Create test memory
    test_memory = HDVector(block_dim=500, num_blocks=100)
    
    # Inject into workspace
    from cognition.consciousness_workspace import WorkspaceEntry
    entry = WorkspaceEntry(
        bound=test_memory,
        source_agent="Test",
        surprise_score=0.8
    )
    workspace.buffer.append(entry)
    
    # Run cycle
    result = workspace.step()
    
    if result:
        print(f"✅ Self-observation broadcast: {result.source_agent}")
        print(f"   Was self-observation: {result.source_agent == 'SelfObserver'}")
    else:
        print("❌ No broadcast occurred")
    
    print(f"\nSelfObserver stats:")
    print(f"   Attempts: {len(self_observer.observation_attempts)}")
    print(f"   Successful: {len(self_observer.successful_observations)}")


if __name__ == "__main__":
    main()
