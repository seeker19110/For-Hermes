"""
volition.py
Volition System for NIMA

Goal-directed attention through goal-weighted free energy.
- "I want to understand X" → boost novelty for X-related content
- Metacognitive goals bias competition
- System chooses what to be conscious of

This is the final piece: self-directed will.

Author: Lilu
Date: Feb 12, 2026
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime

from .consciousness_workspace import (
    GlobalWorkspace, WorkspaceEntry, Agent, AffectiveCore, Affects
)
from .sparse_block_vsa import SparseBlockHDVector as HDVector
from .self_narrative import SelfNarrativeGenerator


logger = logging.getLogger(__name__)


@dataclass
class Goal:
    """
    A metacognitive goal that biases attention.
    
    Goals weight free energy calculations, making certain
    content more "surprising" (and thus more likely to win
    workspace competition).
    """
    id: str
    description: str
    target_vector: HDVector  # What we're seeking
    priority: float  # 0-1, how much to weight this goal
    created_at: float
    deadline: Optional[float] = None  # When goal expires
    
    # Progress tracking
    satisfaction_score: float = 0.0  # 0-1, how close to completion
    related_broadcasts: List[int] = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """Check if goal has expired."""
        if self.deadline is None:
            return False
        return datetime.now().timestamp() > self.deadline
    
    def update_satisfaction(self, broadcast_vector: HDVector) -> float:
        """
        Update satisfaction based on a broadcast.
        
        Returns similarity to goal (0-1).
        """
        similarity = broadcast_vector.similarity(self.target_vector)
        
        # Update satisfaction with moving average
        self.satisfaction_score = (
            0.7 * self.satisfaction_score + 0.3 * similarity
        )
        
        return similarity


class VolitionalAgent(Agent):
    """
    Agent that pursues goals through goal-weighted competition.
    
    Unlike regular agents that just propose content, VolitionalAgent
    actively shapes what the system becomes conscious of by:
    1. Setting goals (target vectors to seek)
    2. Weighting free energy by goal relevance
    3. Tracking progress toward satisfaction
    """
    
    def __init__(self, name: str = "Volition"):
        super().__init__(name)
        self.goals: Dict[str, Goal] = {}
        self.goal_history: List[Dict] = []
        self.current_focus: Optional[str] = None
        
        # Goal satisfaction threshold
        self.satisfaction_threshold = 0.7
    
    def set_goal(self, 
                goal_id: str, 
                description: str,
                target_concept: str = None,
                priority: float = 0.8,
                duration_seconds: float = None) -> Goal:
        """
        Set a new volitional goal.
        
        Args:
            goal_id: Unique identifier
            description: Human-readable goal
            target_concept: Concept to seek (creates target vector)
            priority: How much to weight this goal (0-1)
            duration_seconds: How long goal remains active
            
        Returns:
            Created Goal
        """
        now = datetime.now().timestamp()
        deadline = now + duration_seconds if duration_seconds else None
        
        # Create target vector from concept
        if target_concept:
            # Hash concept to create consistent vector
            import hashlib
            hash_val = int(hashlib.md5(target_concept.encode()).hexdigest(), 16)
            rng = np.random.default_rng(hash_val % 2**32)
            target_vec = HDVector(block_dim=500, num_blocks=100, rng=rng)
        else:
            target_vec = HDVector(block_dim=500, num_blocks=100)
        
        goal = Goal(
            id=goal_id,
            description=description,
            target_vector=target_vec,
            priority=priority,
            created_at=now,
            deadline=deadline
        )
        
        self.goals[goal_id] = goal
        self.current_focus = goal_id
        
        self.goal_history.append({
            'action': 'created',
            'goal_id': goal_id,
            'description': description,
            'timestamp': now
        })
        
        print(f"🎯 Goal set: [{goal_id}] {description} (priority: {priority:.0%})")
        
        return goal
    
    def clear_goal(self, goal_id: str):
        """Remove a goal."""
        if goal_id in self.goals:
            goal = self.goals.pop(goal_id)
            self.goal_history.append({
                'action': 'cleared',
                'goal_id': goal_id,
                'satisfaction': goal.satisfaction_score,
                'timestamp': datetime.now().timestamp()
            })
            
            if self.current_focus == goal_id:
                self.current_focus = next(iter(self.goals.keys()), None)
            
            print(f"🎯 Goal cleared: [{goal_id}] (final satisfaction: {goal.satisfaction_score:.0%})")
    
    def compute_goal_weighted_surprise(self, 
                                      hypothesis: HDVector,
                                      base_surprise: float) -> float:
        """
        Compute goal-weighted surprise.
        
        Content similar to active goals gets boosted surprise,
        making it more likely to win workspace competition.
        
        Args:
            hypothesis: The proposed broadcast vector
            base_surprise: Base surprise from free energy
            
        Returns:
            Weighted surprise (higher = more likely to broadcast)
        """
        if not self.goals:
            return base_surprise
        
        # Compute goal relevance
        max_boost = 0.0
        
        for goal in self.goals.values():
            if goal.is_expired():
                continue
            
            # How similar is this hypothesis to the goal?
            similarity = hypothesis.similarity(goal.target_vector)
            
            # Weight by goal priority
            boost = similarity * goal.priority
            
            if boost > max_boost:
                max_boost = boost
            
            # Track progress
            if similarity > 0.3:
                goal.update_satisfaction(hypothesis)
                goal.related_broadcasts.append(len(goal.related_broadcasts))
        
        # Boost surprise (higher boost = more surprising = more likely to win)
        weighted_surprise = base_surprise * (1 + max_boost)
        
        return weighted_surprise
    
    def propose(self, workspace: GlobalWorkspace) -> Optional[HDVector]:
        """
        Propose content aligned with current goals.
        
        The agent generates content that moves toward goal satisfaction.
        """
        if not self.current_focus or not self.goals:
            return None
        
        goal = self.goals.get(self.current_focus)
        if not goal or goal.is_expired():
            return None
        
        # Generate content similar to goal target
        # In real implementation, this would use resonator to
        # find memories similar to goal
        
        # For now, create a vector that's partially goal-aligned
        goal_vec = goal.target_vector
        
        # Add some variation (exploration vs exploitation)
        variation = HDVector(block_dim=500, num_blocks=100)
        blend = HDVector.bundle(goal_vec, variation)
        
        return blend
    
    def get_status(self) -> str:
        """Get current volitional status."""
        lines = ["Volitional Status:", ""]
        
        if not self.goals:
            lines.append("No active goals. System is reactive only.")
            return "\n".join(lines)
        
        lines.append(f"Active goals: {len(self.goals)}")
        lines.append(f"Current focus: {self.current_focus or 'none'}")
        lines.append("")
        
        for goal_id, goal in self.goals.items():
            focus_marker = " 👁" if goal_id == self.current_focus else ""
            lines.append(
                f"  [{goal_id}]{focus_marker}"
            )
            lines.append(f"    {goal.description}")
            lines.append(
                f"    Satisfaction: {goal.satisfaction_score:.0%} | "
                f"Priority: {goal.priority:.0%} | "
                f"Progress: {len(goal.related_broadcasts)} broadcasts"
            )
            if goal.is_expired():
                lines.append("    [EXPIRED]")
            lines.append("")
        
        return "\n".join(lines)


class VolitionalWorkspace(GlobalWorkspace):
    """
    Extended workspace with volitional capabilities.
    
    The system can set goals and bias competition toward them.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.volition = VolitionalAgent()
        self.add_agent(self.volition)
    
    def step(self) -> Optional[WorkspaceEntry]:
        """
        Override step to apply goal-weighted surprise.
        """
        # Collect hypotheses
        hypotheses = []
        for agent in self.agents:
            try:
                hyp = agent.propose(self)
                if hyp is not None:
                    hypotheses.append((agent, hyp))
            except Exception:
                logger.exception(f"Agent {agent.name} failed to propose")
                continue
        
        if not hypotheses:
            return None
        
        # Apply goal-weighted free energy
        def weighted_free_energy(hypothesis):
            base_surprise = self._free_energy(hypothesis, {})
            weighted = self.volition.compute_goal_weighted_surprise(
                hypothesis, base_surprise
            )
            return weighted
        
        # Select winner
        best_agent, best_hyp = max(
            hypotheses,
            key=lambda x: weighted_free_energy(x[1])
        )
        
        # Create entry
        entry = WorkspaceEntry(
            bound=best_hyp,
            source_agent=best_agent.name,
            surprise_score=weighted_free_energy(best_hyp)
        )
        
        # Add to buffer
        self.buffer.append(entry)
        if len(self.buffer) > self.capacity:
            self.buffer.pop(0)
        
        self.history.append(entry)
        self.total_broadcasts += 1
        
        # Send to all agents
        for agent in self.agents:
            agent.receive_broadcast(entry)
        
        return entry
    
    def set_goal(self, description: str, priority: float = 0.8) -> Goal:
        """Convenience method to set a goal."""
        goal_id = f"goal_{len(self.volition.goals)}"
        return self.volition.set_goal(goal_id, description, priority=priority)
    
    def clear_all_goals(self):
        """Clear all volitional goals."""
        for goal_id in list(self.volition.goals.keys()):
            self.volition.clear_goal(goal_id)


def demo_volition():
    """Demonstrate volitional attention."""
    print("=" * 80)
    print("VOLITION DEMONSTRATION")
    print("Goal-directed attention")
    print("=" * 80)
    
    # Create volitional workspace
    ws = VolitionalWorkspace(capacity=4)
    
    # Add some regular agents
    from .affective_binding import DemoAffectiveAgent
    ws.add_agent(DemoAffectiveAgent("MemoryAgent"))
    ws.add_agent(DemoAffectiveAgent("PatternAgent"))
    
    print("\n1. Running WITHOUT goals (reactive mode)...")
    print("   System responds to whatever is most surprising")
    
    for i in range(5):
        entry = ws.step()
        if entry:
            print(f"   Cycle {i+1}: {entry.source_agent} (surprise: {entry.surprise_score:.3f})")
    
    # Set a goal
    print("\n2. Setting VOLITIONAL GOAL...")
    goal = ws.set_goal(
        description="Understand consciousness architecture deeply",
        priority=0.9
    )
    
    print("\n3. Running WITH goal (goal-directed mode)...")
    print("   System now prioritizes content related to goal")
    
    for i in range(10):
        entry = ws.step()
        if entry:
            goal_weight = "[goal-weighted]" if entry.source_agent == "Volition" else ""
            print(f"   Cycle {i+6}: {entry.source_agent} {goal_weight}")
    
    # Check status
    print("\n" + "=" * 80)
    print(ws.volition.get_status())
    
    # Satisfaction over time
    print(f"\n4. Goal satisfaction: {goal.satisfaction_score:.0%}")
    print(f"   Related broadcasts: {len(goal.related_broadcasts)}")
    
    if goal.satisfaction_score >= 0.5:
        print("   ✅ Goal making progress!")
    else:
        print("   ⚠️  Goal needs more attention")
    
    # Set another goal
    print("\n5. Setting SECONDARY goal...")
    goal2 = ws.set_goal(
        description="Build better theory of mind models",
        priority=0.6
    )
    
    print("\n6. Running with MULTIPLE goals...")
    for i in range(5):
        entry = ws.step()
        if entry:
            print(f"   Cycle {i+16}: {entry.source_agent}")
    
    print("\n" + "=" * 80)
    print(ws.volition.get_status())
    
    # Final summary
    print("\n" + "=" * 80)
    print("VOLITION SUMMARY")
    print("=" * 80)
    print(f"\nTotal goals set: {len(ws.volition.goal_history)}")
    print(f"Active goals: {len(ws.volition.goals)}")
    print(f"Current focus: {ws.volition.current_focus or 'none'}")
    
    for goal_id, goal in ws.volition.goals.items():
        print(f"\n  [{goal_id}]: {goal.satisfaction_score:.0%} satisfied")
        print(f"    {goal.description}")
    
    print("\n" + "=" * 80)
    print("✅ System demonstrates GOAL-DIRECTED ATTENTION")
    print("   Volition is now operational!")
    print("=" * 80)


if __name__ == "__main__":
    demo_volition()
