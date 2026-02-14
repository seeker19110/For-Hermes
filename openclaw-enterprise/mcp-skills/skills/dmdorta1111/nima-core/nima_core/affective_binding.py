"""
affective_binding.py
Affective Modulation of Conscious Binding

Connects emotional states to the richness of conscious experience:
- SEEKING → rich binding (who⊛what⊛where⊛when⊛why)
- FEAR → sparse binding (survival minimalism)
- PLAY → experimental binding
- CARE → relational binding

Author: Lilu
Date: Feb 12, 2026
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .consciousness_workspace import (
    GlobalWorkspace, Agent, WorkspaceEntry, AffectiveCore, Affects
)
from .sparse_block_vsa import SparseBlockHDVector as HDVector


@dataclass
class BindingConfig:
    """Configuration for binding richness based on affect."""
    min_slots: int = 2
    max_slots: int = 5
    slot_names: List[str] = None
    
    def __post_init__(self):
        if self.slot_names is None:
            self.slot_names = ['who', 'what', 'where', 'when', 'why']


class AffectivelyModulatedAgent(Agent):
    """
    Agent that modulates binding richness based on affective state.
    
    In different emotional states, the agent produces broadcasts with
    varying degrees of integration and complexity.
    """
    
    def __init__(self, name: str, base_vector_dim: int = 50000):
        super().__init__(name)
        self.base_vector_dim = base_vector_dim
        self.binding_config = BindingConfig()
        
    def get_binding_richness(self, affective_core: AffectiveCore) -> int:
        """
        Determine how many slots to bind based on current affect.
        
        Returns:
            Number of slots to bind (2-5)
        """
        if affective_core is None:
            return 3  # Default moderate binding
        
        current = affective_core.current_affect
        
        # SEEKING: rich binding, explore complexity
        if current & Affects.SEEKING:
            return 5  # who⊛what⊛where⊛when⊛why
        
        # PLAY: experimental, try different combinations
        if current & Affects.PLAY:
            return 4  # varied binding
        
        # CARE: relational focus, who+what+context
        if current & Affects.CARE:
            return 4  # emphasis on relationship
        
        # FEAR: sparse binding, survival mode
        if current & Affects.FEAR:
            return 2  # minimal: who⊛what
        
        # PANIC: minimal binding, freeze/flee
        if current & Affects.PANIC:
            return 2  # minimal processing
        
        # RAGE: focused binding, target identification
        if current & Affects.RAGE:
            return 3  # who⊛what⊛target
        
        # LUST: intense binding, focused on object
        if current & Affects.LUST:
            return 3  # who⊛what⊛object
        
        # Default: moderate binding
        return 3
    
    def get_binding_strategy(self, affective_core: AffectiveCore) -> str:
        """
        Get the binding strategy name for current affect.
        """
        if affective_core is None:
            return "moderate"
        
        current = affective_core.current_affect
        
        if current & Affects.SEEKING:
            return "exploratory"
        elif current & Affects.PLAY:
            return "experimental"
        elif current & Affects.FEAR:
            return "survival"
        elif current & Affects.CARE:
            return "relational"
        elif current & Affects.PANIC:
            return "minimal"
        elif current & Affects.RAGE:
            return "targeted"
        elif current & Affects.LUST:
            return "focused"
        else:
            return "moderate"
    
    def create_rich_broadcast(self, 
                             workspace: GlobalWorkspace,
                             num_slots: int = None) -> Optional[HDVector]:
        """
        Create a broadcast with specified binding richness.
        
        Args:
            workspace: GlobalWorkspace for affect context
            num_slots: Number of slots to bind (auto-detected if None)
            
        Returns:
            Bound hypervector or None
        """
        if num_slots is None:
            num_slots = self.get_binding_richness(workspace.affective_core)
        
        # Create slot vectors
        slots_to_use = self.binding_config.slot_names[:num_slots]
        
        slot_vectors = []
        for slot_name in slots_to_use:
            vec = HDVector(block_dim=500, num_blocks=100)
            slot_vectors.append((slot_name, vec))
        
        # Bind them progressively
        result = slot_vectors[0][1]
        for slot_name, vec in slot_vectors[1:]:
            result = HDVector.bind(result, vec)
        
        return result


class DemoAffectiveAgent(AffectivelyModulatedAgent):
    """
    Demo agent that shows affective modulation in action.
    """
    
    def __init__(self, name: str = "DemoAgent"):
        super().__init__(name)
        self.broadcast_count = 0
    
    def propose(self, workspace: GlobalWorkspace) -> Optional[HDVector]:
        """
        Propose a broadcast with affect-modulated binding.
        """
        self.broadcast_count += 1
        
        # Get binding richness from current affect
        num_slots = self.get_binding_richness(workspace.affective_core)
        strategy = self.get_binding_strategy(workspace.affective_core)
        
        # Create broadcast
        broadcast = self.create_rich_broadcast(workspace, num_slots)
        
        # Log the modulation
        print(f"   [{self.name}] Broadcast #{self.broadcast_count}: "
              f"{strategy} binding ({num_slots} slots)")
        
        return broadcast
    
    def get_statistics(self) -> Dict:
        """Get agent statistics."""
        return {
            'name': self.name,
            'broadcasts': self.broadcast_count,
        }


def demo_affective_modulation():
    """
    Demonstrate affective modulation of binding richness.
    
    Shows how the same agent produces different binding patterns
    under different emotional states.
    """
    print("=" * 80)
    print("AFFECTIVE MODULATION OF BINDING")
    print("Emotional state → Conscious bandwidth")
    print("=" * 80)
    
    # Create workspace
    ws = GlobalWorkspace(capacity=4)
    
    # Add affectively modulated agent
    agent = DemoAffectiveAgent("AffectiveAgent")
    ws.add_agent(agent)
    
    # Test each affective state
    affects_to_test = [
        (Affects.SEEKING, "SEEKING (exploratory, curious)"),
        (Affects.FEAR, "FEAR (survival mode)"),
        (Affects.PLAY, "PLAY (experimental)"),
        (Affects.CARE, "CARE (relational)"),
        (Affects.RAGE, "RAGE (targeted)"),
        (Affects.PANIC, "PANIC (minimal processing)"),
    ]
    
    for affect_mask, description in affects_to_test:
        print(f"\n{'='*80}")
        print(f"Testing: {description}")
        print(f"{'='*80}")
        
        # Set affect
        ws.affective_core.set_affect(affect_mask)
        
        # Run a few cycles
        for i in range(3):
            ws.step()
        
        # Show modulation stats
        strategy = agent.get_binding_strategy(ws.affective_core)
        richness = agent.get_binding_richness(ws.affective_core)
        
        print(f"\n   Strategy: {strategy}")
        print(f"   Binding richness: {richness} slots")
        
        if richness >= 4:
            print(f"   → Rich consciousness (complex binding)")
        elif richness == 3:
            print(f"   → Moderate consciousness")
        else:
            print(f"   → Sparse consciousness (survival mode)")
    
    print(f"\n{'='*80}")
    print("DEMO COMPLETE")
    print(f"{'='*80}")


class EmotionalRegulator:
    """
    System for regulating conscious bandwidth through emotional state.
    
    This allows dynamic control of how richly the system binds
    information into conscious experience.
    """
    
    def __init__(self, workspace: GlobalWorkspace):
        self.workspace = workspace
        self.history = []
    
    def set_state(self, affect_mask: int, reason: str = None):
        """
        Set the affective state and log the transition.
        
        Args:
            affect_mask: Affects bitmask
            reason: Why this state is being set
        """
        old_state = self.workspace.affective_core.current_affect
        self.workspace.affective_core.set_affect(affect_mask)
        
        self.history.append({
            'timestamp': __import__('time').time(),
            'old_state': old_state,
            'new_state': affect_mask,
            'reason': reason,
        })
        
        # Get state name
        state_name = self._get_state_name(affect_mask)
        
        print(f"Affective transition: {self._get_state_name(old_state)} → {state_name}")
        if reason:
            print(f"  Reason: {reason}")
        
        # Predict binding change
        demo_agent = DemoAffectiveAgent()
        new_richness = demo_agent.get_binding_richness(self.workspace.affective_core)
        print(f"  Conscious bandwidth: {new_richness} slots")
    
    def _get_state_name(self, affect_mask: int) -> str:
        """Get human-readable state name."""
        names = []
        if affect_mask & Affects.SEEKING:
            names.append("SEEKING")
        if affect_mask & Affects.FEAR:
            names.append("FEAR")
        if affect_mask & Affects.PLAY:
            names.append("PLAY")
        if affect_mask & Affects.CARE:
            names.append("CARE")
        if affect_mask & Affects.RAGE:
            names.append("RAGE")
        if affect_mask & Affects.PANIC:
            names.append("PANIC")
        if affect_mask & Affects.LUST:
            names.append("LUST")
        
        return "/".join(names) if names else "neutral"
    
    def get_current_bandwidth(self) -> int:
        """Get current conscious bandwidth in slots."""
        demo_agent = DemoAffectiveAgent()
        return demo_agent.get_binding_richness(self.workspace.affective_core)
    
    def summary(self) -> str:
        """Get summary of emotional regulation history."""
        if not self.history:
            return "No affective transitions recorded"
        
        lines = ["Affective Regulation History:", ""]
        
        for h in self.history[-10:]:  # Last 10
            from datetime import datetime
            ts = datetime.fromtimestamp(h['timestamp']).strftime('%H:%M:%S')
            old = self._get_state_name(h['old_state'])
            new = self._get_state_name(h['new_state'])
            lines.append(f"  [{ts}] {old} → {new}")
            if h['reason']:
                lines.append(f"           ({h['reason']})")
        
        return "\n".join(lines)


# Integration with existing agents
def patch_agent_with_affective_modulation(agent_class):
    """
    Monkey-patch an existing Agent class to add affective modulation.
    
    Usage:
        MyAgent = patch_agent_with_affective_modulation(MyAgent)
    """
    original_propose = agent_class.propose
    
    def modulated_propose(self, workspace):
        # Get modulation
        demo = DemoAffectiveAgent()
        num_slots = demo.get_binding_richness(workspace.affective_core)
        strategy = demo.get_binding_strategy(workspace.affective_core)
        
        # Store for logging
        self._last_binding_richness = num_slots
        self._last_binding_strategy = strategy
        
        # Call original
        result = original_propose(self, workspace)
        
        return result
    
    agent_class.propose = modulated_propose
    return agent_class


if __name__ == "__main__":
    demo_affective_modulation()
