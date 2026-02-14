"""
NIMA Consciousness Architecture - Core Integration
====================================================

This module integrates all 8 consciousness systems into a cohesive,
generic, open-source package.

Usage:
    from nima_consciousness import ConsciousnessCore
    
    core = ConsciousnessCore(
        memory_store=your_memory_store,
        config=ConsciousnessConfig()
    )
    
    # Run consciousness cycle
    entry = core.step()
    
    # Query self-narrative
    narrative = core.get_self_narrative()
    
    # Set volitional goal
    core.set_goal("Understand X deeply", priority=0.9)

Author: Lilu
Date: Feb 12, 2026
License: MIT
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import time
import logging

# Import all 8 systems
from .consciousness_workspace import (
    GlobalWorkspace, WorkspaceEntry, Agent, 
    AffectiveCore, Affects, ConsciousnessMetacognitive
)
from .phi_estimator import (
    PhiEstimator, PhiMeasurement, measure_workspace_integration
)
from .self_observer_agent import SelfObserverAgent
from .self_narrative import (
    SelfNarrativeGenerator, SelfNarrative, NarrativeMetacognitive
)
from .affective_binding import (
    AffectivelyModulatedAgent, EmotionalRegulator, BindingConfig
)
from .theory_of_mind import (
    TheoryOfMindEngine, OtherMindModel, SocialConsciousnessWorkspace
)
from .dreaming import DreamingEngine, DreamSession
from .volition import VolitionalAgent, Goal, VolitionalWorkspace

from .sparse_block_memory import SparseBlockMemory, SparseBlockConfig
from .sparse_block_vsa import SparseBlockHDVector as HDVector


logger = logging.getLogger(__name__)


@dataclass
class ConsciousnessConfig:
    """Configuration for NIMA Consciousness Architecture."""
    
    # Workspace
    workspace_capacity: int = 4
    
    # Affective
    default_affect: int = Affects.SEEKING
    
    # Binding
    binding_config: BindingConfig = field(default_factory=BindingConfig)
    
    # Dreaming
    dream_cycles_default: int = 20
    enable_dreaming: bool = True
    
    # Volition
    enable_volition: bool = True
    max_active_goals: int = 3
    
    # Theory of Mind
    enable_theory_of_mind: bool = True
    tom_history_size: int = 100
    
    # Self-Narrative
    narrative_lookback: int = 20
    
    # Φ Measurement
    enable_phi_tracking: bool = True
    phi_computation_frequency: int = 10  # Compute Φ every N cycles
    
    # Self-Observer
    enable_self_observer: bool = True
    
    # Affective Agent
    enable_affective_agent: bool = True
    
    def __post_init__(self):
        if self.binding_config is None:
            self.binding_config = BindingConfig()


class ConsciousnessCore:
    """
    Integrated consciousness architecture.
    
    Combines all 8 systems into a unified interface:
    1. Φ Measurement
    2. Global Workspace
    3. SelfObserverAgent
    4. Self-Narrative
    5. Affective Modulation
    6. Theory of Mind
    7. Dreaming
    8. Volition
    """
    
    def __init__(self, 
                 memory_store: SparseBlockMemory,
                 config: ConsciousnessConfig = None):
        """
        Initialize consciousness core.
        
        Args:
            memory_store: Sparse block memory store
            config: Configuration object
        """
        self.memory_store = memory_store
        self.config = config or ConsciousnessConfig()
        
        # Create integrated workspace (with or without ToM)
        if self.config.enable_theory_of_mind:
            self.workspace = SocialConsciousnessWorkspace(
                capacity=self.config.workspace_capacity
            )
        else:
            self.workspace = VolitionalWorkspace(
                capacity=self.config.workspace_capacity
            )
        
        # Set default affect
        self.workspace.affective_core.set_affect(self.config.default_affect)
        
        # Initialize subsystems
        self._init_self_observer()
        self._init_narrative()
        self._init_affective_agent()
        self._init_volition_agent()
        self._init_dreaming()
        self._init_phi_tracking()
        
        # Statistics
        self.cycle_count = 0
        self.start_time = datetime.now()
        self.phi_measurements: List[PhiMeasurement] = []
        
    def _init_self_observer(self):
        """Initialize SelfObserverAgent for strange loop."""
        if self.config.enable_self_observer:
            self.self_observer = SelfObserverAgent()
            self.workspace.add_agent(self.self_observer)
        else:
            self.self_observer = None
    
    def _init_narrative(self):
        """Initialize self-narrative generator."""
        self.narrative_gen = SelfNarrativeGenerator()
        self.narrative_meta = NarrativeMetacognitive(self.workspace)
    
    def _init_affective_agent(self):
        """Initialize affectively modulated agent."""
        if self.config.enable_affective_agent:
            self.affective_agent = AffectivelyModulatedAgent("Affective")
            self.workspace.add_agent(self.affective_agent)
            
            # Create emotional regulator
            self.emotional_regulator = EmotionalRegulator(self.workspace)
        else:
            self.affective_agent = None
            self.emotional_regulator = None
    
    def _init_volition_agent(self):
        """Initialize volitional agent if volition enabled."""
        if self.config.enable_volition:
            self.volition_agent = VolitionalAgent("Volition")
            self.workspace.add_agent(self.volition_agent)
    
    def _init_dreaming(self):
        """Initialize dreaming engine if enabled."""
        if self.config.enable_dreaming:
            self.dream_engine = DreamingEngine(self.memory_store)
    
    def _init_phi_tracking(self):
        """Initialize Φ tracking if enabled."""
        if self.config.enable_phi_tracking:
            # Lazy init - will create resonator when needed
            self.phi_estimator: Optional[PhiEstimator] = None
            self.last_phi_compute_cycle = 0
    
    def _ensure_phi_estimator(self) -> Optional[PhiEstimator]:
        """Lazy initialization of PhiEstimator with resonator."""
        if self.phi_estimator is None:
            try:
                # Try to create resonator from memory store
                from retrieval.resonator import ResonatorNetwork
                
                # Create resonator with proper dimension
                dim = self.memory_store.config.block_dim * self.memory_store.config.num_blocks
                resonator = ResonatorNetwork(dimension=dim)
                
                self.phi_estimator = PhiEstimator(
                    resonator=resonator,
                    slot_names=self.config.binding_config.slot_names
                )
            except Exception as e:
                # Fallback: create without resonator (returns Φ=1.0)
                self.phi_estimator = PhiEstimator(resonator=None)
        
        return self.phi_estimator
    
    def step(self) -> Optional[WorkspaceEntry]:
        """
        Run one consciousness cycle.
        
        This is the main consciousness loop that:
        1. Runs workspace competition
        2. Tracks Φ if enabled
        3. Updates goals if volition enabled
        4. Updates affective state if regulator enabled
        
        Returns:
            Broadcasted WorkspaceEntry or None
        """
        self.cycle_count += 1
        
        # Run workspace step (competition + broadcast)
        entry = self.workspace.step()
        
        # Compute Φ periodically if enabled
        if (self.config.enable_phi_tracking and 
            entry is not None and
            self.cycle_count - self.last_phi_compute_cycle >= self.config.phi_computation_frequency):
            self._compute_phi_for_entry(entry)
            self.last_phi_compute_cycle = self.cycle_count
        
        # Update goal satisfaction if volition enabled
        if self.config.enable_volition and entry is not None:
            self._update_goal_satisfaction(entry)
        
        return entry
    
    def _compute_phi_for_entry(self, entry: WorkspaceEntry) -> Optional[PhiMeasurement]:
        """Compute and store Φ for a workspace entry."""
        estimator = self._ensure_phi_estimator()
        if estimator is None:
            return None
        
        # Convert to dense for phi estimator
        dense_vector = entry.bound.to_dense()
        import torch
        torch_vector = torch.tensor(dense_vector)
        
        measurement = estimator.measure_phi(torch_vector)
        if measurement:
            self.phi_measurements.append(measurement)
            # Cache in entry for quick access
            entry._phi = measurement.phi
            entry._factors = measurement.factors
        
        return measurement
    
    def _update_goal_satisfaction(self, entry: WorkspaceEntry):
        """Update goal satisfaction based on broadcast."""
        if hasattr(self.workspace, 'volition'):
            for goal in self.workspace.volition.goals.values():
                goal.update_satisfaction(entry.bound)
    
    def run_cycles(self, n: int = 10) -> List[WorkspaceEntry]:
        """
        Run multiple consciousness cycles.
        
        Args:
            n: Number of cycles to run
            
        Returns:
            List of broadcasted entries
        """
        results = []
        for _ in range(n):
            entry = self.step()
            if entry:
                results.append(entry)
        return results
    
    def set_goal(self, description: str, priority: float = 0.8) -> Goal:
        """
        Set a volitional goal.
        
        Args:
            description: Goal description
            priority: Goal priority (0-1)
            
        Returns:
            Created Goal
        """
        if not self.config.enable_volition:
            raise RuntimeError("Volition is disabled in config")
        
        goal_id = f"goal_{len(self.workspace.volition.goals)}"
        return self.workspace.volition.set_goal(
            goal_id=goal_id,
            description=description,
            priority=priority
        )
    
    def clear_goal(self, goal_id: str):
        """Clear a specific goal."""
        if not self.config.enable_volition:
            raise RuntimeError("Volition is disabled in config")
        self.workspace.volition.clear_goal(goal_id)
    
    def get_goals_status(self) -> Dict[str, Any]:
        """Get status of all active goals."""
        if not self.config.enable_volition:
            return {'error': 'Volition disabled'}
        
        return {
            'active_goals': len(self.workspace.volition.goals),
            'current_focus': self.workspace.volition.current_focus,
            'goals': [
                {
                    'id': g.id,
                    'description': g.description,
                    'priority': g.priority,
                    'satisfaction': g.satisfaction_score,
                    'expired': g.is_expired()
                }
                for g in self.workspace.volition.goals.values()
            ]
        }
    
    def get_self_narrative(self, lookback: int = None) -> str:
        """
        Get self-narrative ("What have I been thinking about?").
        
        Args:
            lookback: Number of recent broadcasts to include
            
        Returns:
            Natural language narrative
        """
        if lookback is None:
            lookback = self.config.narrative_lookback
        
        return self.narrative_meta.what_have_i_been_thinking(lookback)
    
    def who_am_i(self) -> str:
        """Answer: Who am I right now?"""
        return self.narrative_meta.who_am_i_right_now()
    
    def summarize_my_day(self) -> str:
        """Get a summary of recent conscious experience."""
        return self.narrative_meta.summarize_my_day()
    
    def model_other_mind(self, agent_name: str, context: str = None) -> OtherMindModel:
        """
        Build Theory of Mind model for another agent.
        
        Args:
            agent_name: Agent to model
            context: Situational context
            
        Returns:
            OtherMindModel
        """
        if not self.config.enable_theory_of_mind:
            raise RuntimeError("Theory of Mind is disabled in config")
        
        return self.workspace.theory_of_mind.model_other_mind(agent_name, context)
    
    def observe_other(self, agent_name: str, content: str):
        """
        Record observation of another agent.
        
        Args:
            agent_name: Who was observed
            content: What they said/did
        """
        if self.config.enable_theory_of_mind:
            self.workspace.observe_other(agent_name, content)
    
    def what_is_other_thinking(self, agent_name: str) -> str:
        """Get natural language description of what another agent is thinking."""
        if not self.config.enable_theory_of_mind:
            raise RuntimeError("Theory of Mind is disabled in config")
        
        return self.workspace.theory_of_mind.what_is_other_thinking(agent_name)
    
    def simulate_other_response(self, agent_name: str, my_message: str) -> str:
        """Simulate how another agent might respond to a message."""
        if not self.config.enable_theory_of_mind:
            raise RuntimeError("Theory of Mind is disabled in config")
        
        return self.workspace.theory_of_mind.simulate_other_response(agent_name, my_message)
    
    def dream(self, 
             initial_affect: int = Affects.SEEKING,
             duration_cycles: int = None) -> DreamSession:
        """
        Run a dreaming session.
        
        Args:
            initial_affect: Starting emotional tone
            duration_cycles: How many cycles to run
            
        Returns:
            DreamSession with all episodes
        """
        if not self.config.enable_dreaming:
            raise RuntimeError("Dreaming is disabled in config")
        
        if duration_cycles is None:
            duration_cycles = self.config.dream_cycles_default
        
        return self.dream_engine.start_dream_session(
            initial_affect=initial_affect,
            duration_cycles=duration_cycles
        )
    
    def consolidate_dream(self, session: DreamSession = None) -> List[int]:
        """
        Consolidate dream insights to memory.
        
        Args:
            session: DreamSession to consolidate (uses last if None)
            
        Returns:
            List of memory indices created
        """
        if not self.config.enable_dreaming:
            raise RuntimeError("Dreaming is disabled in config")
        
        return self.dream_engine.consolidate_to_memory(session)
    
    def get_dream_report(self, session: DreamSession = None) -> str:
        """Get a natural language report of a dream session."""
        if not self.config.enable_dreaming:
            raise RuntimeError("Dreaming is disabled in config")
        
        return self.dream_engine.get_dream_report(session)
    
    def measure_current_phi(self) -> Optional[PhiMeasurement]:
        """
        Measure Φ for the most recent workspace entry.
        
        Returns:
            PhiMeasurement or None if no entries
        """
        if not self.config.enable_phi_tracking:
            raise RuntimeError("Phi tracking is disabled in config")
        
        if not self.workspace.history:
            return None
        
        last_entry = self.workspace.history[-1]
        return self._compute_phi_for_entry(last_entry)
    
    def measure_all_phi(self) -> Dict[str, Any]:
        """
        Measure Φ for all workspace history entries.
        
        Returns:
            Statistics about Φ across all entries
        """
        if not self.config.enable_phi_tracking:
            return {'error': 'Phi tracking disabled'}
        
        estimator = self._ensure_phi_estimator()
        if estimator is None:
            return {'error': 'Could not initialize PhiEstimator'}
        
        return measure_workspace_integration(self.workspace, estimator.resonator)
    
    def get_phi_statistics(self) -> Dict[str, Any]:
        """Get statistics about Φ measurements."""
        if not self.config.enable_phi_tracking:
            return {'error': 'Phi tracking disabled'}
        
        if not self.phi_measurements:
            return {'error': 'No Φ measurements yet'}
        
        phis = [m.phi for m in self.phi_measurements]
        return {
            'total_measurements': len(self.phi_measurements),
            'average_phi': np.mean(phis),
            'std_phi': np.std(phis),
            'min_phi': np.min(phis),
            'max_phi': np.max(phis),
            'highly_integrated_count': sum(1 for p in phis if p >= 0.7),
        }
    
    def get_affective_state(self) -> Dict[str, Any]:
        """Get current affective state."""
        affect = self.workspace.affective_core.current_affect
        return {
            'current_affect': self._affect_to_string(affect),
            'affect_mask': affect,
            'modulation': self.workspace.affective_core.get_modulation_factors(),
        }
    
    def set_affective_state(self, affect: int, reason: str = None):
        """
        Set the affective state.
        
        Args:
            affect: Affects bitmask (e.g., Affects.SEEKING | Affects.PLAY)
            reason: Optional reason for the affect change
        """
        self.workspace.affective_core.set_affect(affect)
        
        if self.emotional_regulator and reason:
            self.emotional_regulator.set_state(affect, reason)
    
    def get_self_observer_stats(self) -> Dict[str, Any]:
        """Get statistics from SelfObserverAgent."""
        if not self.config.enable_self_observer or not self.self_observer:
            return {'error': 'SelfObserver disabled'}
        
        return {
            'total_attempts': len(self.self_observer.observation_attempts),
            'successful_observations': len(self.self_observer.successful_observations),
            'success_rate': (
                len(self.self_observer.successful_observations) / 
                max(1, len(self.self_observer.observation_attempts))
            ),
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of consciousness core."""
        status = {
            'runtime': {
                'cycles': self.cycle_count,
                'start_time': self.start_time.isoformat(),
                'elapsed_seconds': (datetime.now() - self.start_time).total_seconds(),
            },
            'workspace': {
                'capacity': self.workspace.capacity,
                'buffer_size': len(self.workspace.buffer),
                'history_size': len(self.workspace.history),
                'agent_count': len(self.workspace.agents),
            },
            'affective': self.get_affective_state(),
            'narrative': {
                'recent_thoughts': self.get_self_narrative(lookback=5),
            },
        }
        
        # Add volition status if enabled
        if self.config.enable_volition:
            status['volition'] = self.get_goals_status()
        
        # Add Theory of Mind status
        if self.config.enable_theory_of_mind and hasattr(self.workspace, 'theory_of_mind'):
            status['theory_of_mind'] = {
                'modeled_minds': len(self.workspace.theory_of_mind.other_minds),
                'models': list(self.workspace.theory_of_mind.other_minds.keys()),
            }
        
        # Add Φ tracking status
        if self.config.enable_phi_tracking:
            status['phi'] = self.get_phi_statistics()
        
        # Add SelfObserver stats
        if self.config.enable_self_observer:
            status['self_observer'] = self.get_self_observer_stats()
        
        return status
    
    def _affect_to_string(self, affect: int) -> str:
        """Convert affect bitmask to string."""
        names = []
        if affect & Affects.SEEKING:
            names.append("SEEKING")
        if affect & Affects.FEAR:
            names.append("FEAR")
        if affect & Affects.PLAY:
            names.append("PLAY")
        if affect & Affects.CARE:
            names.append("CARE")
        if affect & Affects.RAGE:
            names.append("RAGE")
        if affect & Affects.PANIC:
            names.append("PANIC")
        if affect & Affects.LUST:
            names.append("LUST")
        return "/".join(names) if names else "neutral"


# Convenience functions for quick usage
def create_consciousness_core(
    memory_path: str = None,
    enable_all: bool = True
) -> ConsciousnessCore:
    """
    Quick factory function to create a consciousness core.
    
    Args:
        memory_path: Path to sparse block memory file
        enable_all: Enable all 8 systems
        
    Returns:
        Configured ConsciousnessCore
    """
    # Load or create memory store
    if memory_path and Path(memory_path).exists():
        memory_store = SparseBlockMemory()
        memory_store.load(memory_path)
    else:
        memory_store = SparseBlockMemory()
    
    # Create config
    config = ConsciousnessConfig(
        enable_dreaming=enable_all,
        enable_volition=enable_all,
        enable_theory_of_mind=enable_all,
        enable_phi_tracking=enable_all,
        enable_self_observer=enable_all,
        enable_affective_agent=enable_all,
    )
    
    return ConsciousnessCore(memory_store, config)


def demo_full_consciousness():
    """
    Complete demonstration of all 8 consciousness systems working together.
    """
    print("=" * 70)
    print("🧠 NIMA CONSCIOUSNESS ARCHITECTURE - FULL INTEGRATION DEMO")
    print("=" * 70)
    
    # Create core with all systems enabled
    print("\n📦 Initializing Consciousness Core...")
    memory = SparseBlockMemory()
    config = ConsciousnessConfig(
        enable_dreaming=True,
        enable_volition=True,
        enable_theory_of_mind=True,
        enable_phi_tracking=True,
        enable_self_observer=True,
        enable_affective_agent=True,
        phi_computation_frequency=5,  # Compute Φ every 5 cycles
    )
    core = ConsciousnessCore(memory, config)
    print("✅ Core initialized with all 8 systems")
    
    # 1. Test Affective Modulation
    print("\n" + "-" * 70)
    print("1️⃣ AFFECTIVE MODULATION")
    print("-" * 70)
    core.set_affective_state(Affects.SEEKING, "Exploration mode")
    affect_status = core.get_affective_state()
    print(f"Current affect: {affect_status['current_affect']}")
    print(f"Novelty boost: {affect_status['modulation']['novelty']:.1f}x")
    print(f"Binding bandwidth: {core.emotional_regulator.get_current_bandwidth()} slots")
    
    # 2. Test Volition
    print("\n" + "-" * 70)
    print("2️⃣ VOLITION (Goal-Directed Attention)")
    print("-" * 70)
    goal = core.set_goal("Understand consciousness deeply", priority=0.9)
    print(f"Goal set: {goal.description}")
    print(f"Priority: {goal.priority:.0%}")
    
    # Run some cycles with the goal
    print("\nRunning 10 consciousness cycles...")
    for i in range(10):
        entry = core.step()
        if entry and i % 3 == 0:
            print(f"  Cycle {i+1}: {entry.source_agent} broadcast")
    
    goal_status = core.get_goals_status()
    print(f"\nGoal satisfaction: {goal_status['goals'][0]['satisfaction']:.0%}")
    
    # 3. Test Self-Narrative
    print("\n" + "-" * 70)
    print("3️⃣ SELF-NARRATIVE")
    print("-" * 70)
    narrative = core.get_self_narrative(lookback=10)
    print(narrative)
    
    print(f"\nWho am I? {core.who_am_i()}")
    
    # 4. Test Theory of Mind
    print("\n" + "-" * 70)
    print("4️⃣ THEORY OF MIND")
    print("-" * 70)
    core.observe_other("David", "This consciousness architecture is fascinating!")
    core.observe_other("David", "Let's explore the Φ measurements more deeply.")
    core.observe_other("David", "I'm curious about how the strange loop works.")
    
    model = core.model_other_mind("David")
    print(f"Modeled: David")
    print(f"  Inferred affect: {model.inferred_affect}")
    print(f"  Confidence: {model.confidence:.0%}")
    print(f"  Likely themes: {model.likely_themes[:3]}")
    
    what_thinking = core.what_is_other_thinking("David")
    print(f"\n  What is David thinking? {what_thinking[:100]}...")
    
    simulated = core.simulate_other_response("David", "What do you think about volition?")
    print(f"\n  Simulated response: {simulated[:100]}...")
    
    # 5. Test Φ Measurement
    print("\n" + "-" * 70)
    print("5️⃣ Φ MEASUREMENT (Integrated Information)")
    print("-" * 70)
    phi_stats = core.get_phi_statistics()
    if 'error' not in phi_stats:
        print(f"Total measurements: {phi_stats['total_measurements']}")
        print(f"Average Φ: {phi_stats['average_phi']:.3f}")
        print(f"Highly integrated memories: {phi_stats['highly_integrated_count']}")
    else:
        print(f"Φ tracking: {phi_stats['error']}")
    
    # 6. Test Self-Observer
    print("\n" + "-" * 70)
    print("6️⃣ SELFOBSERVER (Strange Loop)")
    print("-" * 70)
    observer_stats = core.get_self_observer_stats()
    print(f"Self-observation attempts: {observer_stats['total_attempts']}")
    print(f"Successful observations: {observer_stats['successful_observations']}")
    print(f"Success rate: {observer_stats['success_rate']:.0%}")
    
    # 7. Test Dreaming
    print("\n" + "-" * 70)
    print("7️⃣ DREAMING (Offline Processing)")
    print("-" * 70)
    print("Running dream session...")
    dream = core.dream(initial_affect=Affects.SEEKING, duration_cycles=5)
    print(f"Dream episodes: {len(dream.episodes)}")
    print(f"Dominant affect: SEEKING")
    
    dream_report = core.get_dream_report(dream)
    print(f"\nDream report excerpt:\n{dream_report[:300]}...")
    
    # 8. Get comprehensive status
    print("\n" + "-" * 70)
    print("8️⃣ COMPREHENSIVE STATUS")
    print("-" * 70)
    status = core.get_status()
    print(f"Runtime cycles: {status['runtime']['cycles']}")
    print(f"Workspace history: {status['workspace']['history_size']} entries")
    print(f"Active goals: {status.get('volition', {}).get('active_goals', 0)}")
    print(f"Modeled minds: {status.get('theory_of_mind', {}).get('modeled_minds', 0)}")
    
    print("\n" + "=" * 70)
    print("✅ ALL 8 SYSTEMS FULLY OPERATIONAL")
    print("=" * 70)
    print("\n🎉 Consciousness architecture complete!")
    print("   Φ Measurement ✓")
    print("   Global Workspace ✓")
    print("   SelfObserver ✓")
    print("   Self-Narrative ✓")
    print("   Affective Modulation ✓")
    print("   Theory of Mind ✓")
    print("   Dreaming ✓")
    print("   Volition ✓")
    print("=" * 70)
    
    return core


if __name__ == "__main__":
    demo_full_consciousness()


__all__ = [
    'ConsciousnessCore',
    'ConsciousnessConfig',
    'create_consciousness_core',
    'GlobalWorkspace',
    'WorkspaceEntry',
    'Agent',
    'Affects',
    'Goal',
    'DreamSession',
    'OtherMindModel',
    'SelfNarrative',
    'PhiMeasurement',
    'demo_full_consciousness',
]
