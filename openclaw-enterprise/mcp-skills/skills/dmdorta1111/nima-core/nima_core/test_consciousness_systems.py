"""
test_consciousness_systems.py
Comprehensive unit tests for NIMA Consciousness Architecture

Run with: python -m pytest test_consciousness_systems.py -v

Author: Lilu
Date: Feb 12, 2026
"""

import unittest
import numpy as np
import torch
from datetime import datetime, timedelta

# Import all systems
from .sparse_block_vsa import SparseBlockHDVector as HDVector
from .sparse_block_memory import SparseBlockMemory, SparseBlockConfig
from .consciousness_workspace import (
    GlobalWorkspace, WorkspaceEntry, Agent, AffectiveCore, Affects
)
from .phi_estimator import PhiEstimator, PhiMeasurement
from .self_observer_agent import SelfObserverAgent
from .self_narrative import (
    SelfNarrativeGenerator, NarrativeTheme, SelfNarrative
)
from .affective_binding import (
    AffectivelyModulatedAgent, BindingConfig
)
from .theory_of_mind import (
    TheoryOfMindEngine, OtherMindModel
)
from .dreaming import DreamingEngine, DreamEpisode, DreamSession
from .volition import VolitionalAgent, Goal, VolitionalWorkspace
from .nima_consciousness_core import ConsciousnessCore, ConsciousnessConfig


class TestSparseBlockVSA(unittest.TestCase):
    """Test sparse block VSA primitives."""
    
    def test_vector_creation(self):
        vec = HDVector(block_dim=500, num_blocks=100)
        self.assertEqual(vec.block_dim, 500)
        self.assertEqual(vec.num_blocks, 100)
        self.assertGreater(len(vec.active_blocks), 0)
    
    def test_binding(self):
        a = HDVector(block_dim=500, num_blocks=100)
        b = HDVector(block_dim=500, num_blocks=100)
        bound = HDVector.bind(a, b)
        self.assertIsInstance(bound, HDVector)
    
    def test_similarity(self):
        vec = HDVector(block_dim=500, num_blocks=100)
        sim = vec.similarity(vec)
        self.assertAlmostEqual(sim, 1.0, places=5)


class TestGlobalWorkspace(unittest.TestCase):
    """Test Global Workspace implementation."""
    
    def setUp(self):
        self.workspace = GlobalWorkspace(capacity=4)
    
    def test_initialization(self):
        self.assertEqual(self.workspace.capacity, 4)
        self.assertEqual(len(self.workspace.buffer), 0)
        self.assertIsNotNone(self.workspace.affective_core)
    
    def test_add_agent(self):
        class TestAgent(Agent):
            def propose(self, workspace):
                return HDVector(block_dim=500, num_blocks=100)
        
        agent = TestAgent("Test")
        self.workspace.add_agent(agent)
        self.assertEqual(len(self.workspace.agents), 1)
    
    def test_step_no_agents(self):
        result = self.workspace.step()
        self.assertIsNone(result)
    
    def test_affective_modulation(self):
        self.workspace.affective_core.set_affect(Affects.SEEKING)
        modulation = self.workspace.affective_core.get_modulation_factors()
        self.assertGreater(modulation['novelty'], 1.0)


class TestPhiEstimator(unittest.TestCase):
    """Test Phi measurement system."""
    
    def setUp(self):
        self.estimator = PhiEstimator(None, num_lesion_trials=1)
    
    def test_initialization(self):
        self.assertIsNone(self.estimator.resonator)
    
    def test_phi_measurement_no_resonator(self):
        vec = HDVector(block_dim=500, num_blocks=100)
        dense = torch.tensor(vec.to_dense())
        measurement = self.estimator.measure_phi(dense)
        self.assertIsInstance(measurement, PhiMeasurement)
        self.assertEqual(measurement.phi, 1.0)


class TestSelfObserver(unittest.TestCase):
    """Test SelfObserverAgent."""
    
    def setUp(self):
        self.workspace = GlobalWorkspace(capacity=4)
        self.self_observer = SelfObserverAgent()
        self.workspace.add_agent(self.self_observer)
    
    def test_initialization(self):
        self.assertEqual(self.self_observer.name, "SelfObserver")
        self.assertIsNotNone(self.self_observer.self_marker)
    
    def test_propose_with_empty_buffer(self):
        proposal = self.self_observer.propose(self.workspace)
        self.assertIsNone(proposal)


class TestSelfNarrative(unittest.TestCase):
    """Test self-narrative generation."""
    
    def setUp(self):
        self.workspace = GlobalWorkspace(capacity=4)
        self.generator = SelfNarrativeGenerator()
        
        for i in range(5):
            vec = HDVector(block_dim=500, num_blocks=100)
            entry = WorkspaceEntry(
                bound=vec,
                source_agent=f"Agent{i}",
                surprise_score=0.5
            )
            entry.metadata = {'what': f'Test {i}'}
            self.workspace.history.append(entry)
    
    def test_generate_narrative(self):
        narrative = self.generator.generate_narrative(self.workspace, 5)
        self.assertIsInstance(narrative, SelfNarrative)
        self.assertEqual(len(narrative.timeline), 5)


class TestAffectiveBinding(unittest.TestCase):
    """Test affective modulation."""
    
    def setUp(self):
        self.workspace = GlobalWorkspace(capacity=4)
        self.agent = AffectivelyModulatedAgent("Test")
    
    def test_seeking_binding(self):
        self.workspace.affective_core.set_affect(Affects.SEEKING)
        richness = self.agent.get_binding_richness(self.workspace.affective_core)
        self.assertEqual(richness, 5)
    
    def test_fear_binding(self):
        self.workspace.affective_core.set_affect(Affects.FEAR)
        richness = self.agent.get_binding_richness(self.workspace.affective_core)
        self.assertEqual(richness, 2)


class TestTheoryOfMind(unittest.TestCase):
    """Test Theory of Mind."""
    
    def setUp(self):
        self.workspace = GlobalWorkspace(capacity=4)
        self.tom = TheoryOfMindEngine(self.workspace)
    
    def test_observe_interaction(self):
        self.tom.observe_interaction("David", "Test content")
        self.assertIn("David", self.tom.interaction_history)
    
    def test_affect_inference(self):
        affect, conf = self.tom._infer_affect_from_content("I'm curious")
        self.assertEqual(affect, Affects.SEEKING)


class TestDreaming(unittest.TestCase):
    """Test dreaming system."""
    
    def setUp(self):
        self.memory_store = SparseBlockMemory()
        self.engine = DreamingEngine(self.memory_store)
    
    def test_dream_session(self):
        session = self.engine.start_dream_session(
            initial_affect=Affects.SEEKING,
            duration_cycles=5
        )
        self.assertIsInstance(session, DreamSession)
        self.assertEqual(len(session.episodes), 5)


class TestVolition(unittest.TestCase):
    """Test volition system."""
    
    def setUp(self):
        self.workspace = VolitionalWorkspace(capacity=4)
    
    def test_set_goal(self):
        goal = self.workspace.set_goal("Test goal", priority=0.8)
        self.assertIsInstance(goal, Goal)
        self.assertEqual(goal.priority, 0.8)
    
    def test_goal_weighted_surprise(self):
        self.workspace.set_goal("Test", priority=0.8)
        vec = HDVector(block_dim=500, num_blocks=100)
        weighted = self.workspace.volition.compute_goal_weighted_surprise(vec, 0.5)
        self.assertGreaterEqual(weighted, 0.5)


class TestConsciousnessCore(unittest.TestCase):
    """Test integrated core."""
    
    def setUp(self):
        self.memory_store = SparseBlockMemory()
        self.config = ConsciousnessConfig()
        self.core = ConsciousnessCore(self.memory_store, self.config)
    
    def test_initialization(self):
        self.assertIsNotNone(self.core.workspace)
        self.assertEqual(self.core.cycle_count, 0)
    
    def test_set_goal(self):
        goal = self.core.set_goal("Test", priority=0.8)
        self.assertIsInstance(goal, Goal)
    
    def test_get_status(self):
        status = self.core.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn('runtime', status)


if __name__ == '__main__':
    unittest.main()
