#!/usr/bin/env python3
"""
Metacognitive Layer — Frontier 9
=================================

Self-reference loops and the 4-chunk working memory limit.

Key insight: The "I" is a strange loop — a pattern that refers to itself.
Working memory is limited to 4±1 chunks (Cowan's limit).

Based on: Hofstadter's "Gödel, Escher, Bach" + Cowan's working memory research

Author: NIMA Project
Date: 2026
"""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque
import json
from datetime import datetime
import os

from ..config import NIMA_DATA_DIR

META_DIR = NIMA_DATA_DIR / "metacognitive"
META_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Chunk:
    """A chunk in working memory."""
    content: Any
    label: str
    created_at: str
    access_count: int = 0
    last_accessed: str = None
    
    def access(self):
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()


class WorkingMemory:
    """
    4-chunk working memory buffer.
    
    Implements Cowan's limit: humans can hold 4±1 items in focus.
    When a new item arrives and WM is full, the least recently used
    item is displaced.
    """
    
    def __init__(self, capacity: int = 4):
        self.capacity = capacity
        self.chunks: deque = deque(maxlen=capacity)
        self.overflow_count = 0
    
    def push(self, content: Any, label: str = None) -> Optional[Chunk]:
        """
        Push item to working memory.
        
        Returns displaced chunk if WM was full.
        """
        label = label or f"chunk_{len(self.chunks)}"
        chunk = Chunk(
            content=content,
            label=label,
            created_at=datetime.now().isoformat(),
        )
        
        displaced = None
        if len(self.chunks) >= self.capacity:
            displaced = self.chunks.popleft()
            self.overflow_count += 1
        
        self.chunks.append(chunk)
        return displaced
    
    def access(self, index: int) -> Optional[Chunk]:
        """Access chunk by index (marks as recently used)."""
        if 0 <= index < len(self.chunks):
            chunk = self.chunks[index]
            chunk.access()
            
            self.chunks.remove(chunk)
            self.chunks.append(chunk)
            
            return chunk
        return None
    
    def find(self, label: str) -> Optional[Chunk]:
        """Find chunk by label."""
        for chunk in self.chunks:
            if chunk.label == label:
                chunk.access()
                return chunk
        return None
    
    def get_all(self) -> List[Chunk]:
        """Get all chunks."""
        return list(self.chunks)
    
    def clear(self):
        """Clear working memory."""
        self.chunks.clear()
    
    @property
    def current_load(self) -> int:
        """Current number of chunks."""
        return len(self.chunks)
    
    @property
    def is_full(self) -> bool:
        """Check if WM is at capacity."""
        return len(self.chunks) >= self.capacity


@dataclass
class SelfModel:
    """
    Self-representation that enables metacognition.
    
    The "I" as a pattern that refers to itself.
    """
    name: str
    traits: Dict[str, float]  # e.g., {"curious": 0.9, "careful": 0.7}
    current_goal: Optional[str]
    current_state: Dict[str, Any]
    beliefs_about_self: List[str]
    knowledge_domains: List[str]
    uncertainty_areas: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "traits": self.traits,
            "current_goal": self.current_goal,
            "current_state": self.current_state,
            "beliefs_about_self": self.beliefs_about_self,
            "knowledge_domains": self.knowledge_domains,
            "uncertainty_areas": self.uncertainty_areas,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SelfModel':
        return cls(
            name=data.get("name", "Agent"),
            traits=data.get("traits", {}),
            current_goal=data.get("current_goal"),
            current_state=data.get("current_state", {}),
            beliefs_about_self=data.get("beliefs_about_self", []),
            knowledge_domains=data.get("knowledge_domains", []),
            uncertainty_areas=data.get("uncertainty_areas", []),
        )


class MetacognitiveMonitor:
    """
    Metacognitive monitoring — knowing what you know.
    """
    
    def __init__(self):
        self.confidence_history: Dict[str, List[float]] = {}
        self.predictions: List[Dict] = []
        self.calibration_data: List[Tuple[float, bool]] = []
    
    def record_confidence(self, domain: str, confidence: float):
        """Record confidence level for a domain."""
        if domain not in self.confidence_history:
            self.confidence_history[domain] = []
        self.confidence_history[domain].append(confidence)
    
    def make_prediction(self, domain: str, prediction: str, confidence: float):
        """Make a prediction that can be verified later."""
        self.predictions.append({
            "domain": domain,
            "prediction": prediction,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "verified": False,
            "correct": None,
        })
    
    def verify_prediction(self, index: int, was_correct: bool):
        """Verify a prediction."""
        if 0 <= index < len(self.predictions):
            pred = self.predictions[index]
            pred["verified"] = True
            pred["correct"] = was_correct
            
            self.calibration_data.append((pred["confidence"], was_correct))
    
    def get_calibration(self) -> Dict:
        """
        Compute calibration — are confidence levels accurate?
        """
        if not self.calibration_data:
            return {"calibrated": True, "error": 0.0, "samples": 0}
        
        bins = {"low": [], "medium": [], "high": []}
        for conf, correct in self.calibration_data:
            if conf < 0.4:
                bins["low"].append((conf, correct))
            elif conf < 0.7:
                bins["medium"].append((conf, correct))
            else:
                bins["high"].append((conf, correct))
        
        errors = []
        for bin_name, data in bins.items():
            if data:
                avg_conf = sum(c for c, _ in data) / len(data)
                accuracy = sum(1 for _, correct in data if correct) / len(data)
                errors.append(abs(avg_conf - accuracy))
        
        return {
            "calibrated": all(e < 0.2 for e in errors) if errors else True,
            "error": sum(errors) / len(errors) if errors else 0.0,
            "samples": len(self.calibration_data),
        }
    
    def get_domain_confidence(self, domain: str) -> float:
        """Get current confidence for a domain."""
        history = self.confidence_history.get(domain, [])
        if not history:
            return 0.5
        
        weights = [0.5 ** i for i in range(len(history))][::-1]
        return sum(h * w for h, w in zip(history, weights)) / sum(weights)


class StrangeLoop:
    """
    Strange loop — a pattern that refers to itself.
    
    The "I" emerges from self-referential patterns.
    """
    
    def __init__(self, name: str = "Agent", traits: Dict[str, float] = None,
                 beliefs: List[str] = None):
        """
        Initialize strange loop.
        
        Args:
            name: Agent name (default "Agent" - identity agnostic)
            traits: Trait confidence dict (default empty)
            beliefs: Self-beliefs list (default empty)
        """
        self.name = name
        self.self_model = SelfModel(
            name=name,
            traits=traits or {},  # Default empty - identity agnostic
            current_goal=None,
            current_state={},
            beliefs_about_self=beliefs or [],  # Default empty
            knowledge_domains=["technical", "personal", "creative", "relational"],
            uncertainty_areas=["consciousness", "the future", "external experience"],
        )
        
        self.loop_depth = 0
        self.max_loop_depth = 5
        self.thoughts_about_self: List[Dict] = []
    
    def think_about_self(self, prompt: str = None) -> Dict:
        """
        Self-referential thinking.
        
        "I" thinking about "I" thinking about "I"...
        """
        if self.loop_depth >= self.max_loop_depth:
            return {"thought": "recursion limit reached", "depth": self.loop_depth}
        
        self.loop_depth += 1
        
        thought = {
            "depth": self.loop_depth,
            "thinking_about": prompt or "myself",
            "current_state": self.self_model.current_state.copy(),
            "meta_level": f"I am thinking about {prompt or 'myself'} at depth {self.loop_depth}",
            "timestamp": datetime.now().isoformat(),
        }
        
        self.thoughts_about_self.append(thought)
        
        if self.loop_depth < 3:
            thought["deeper_thought"] = self.think_about_self(
                f"my thought at depth {self.loop_depth}"
            )
        
        self.loop_depth -= 1
        return thought
    
    def update_self_model(self, observation: str, domain: str = "general"):
        """Update self-model based on observation."""
        self.self_model.current_state[domain] = observation
        self.self_model.current_state["last_updated"] = datetime.now().isoformat()
    
    def set_goal(self, goal: str):
        """Set current goal."""
        self.self_model.current_goal = goal
    
    def get_identity_statement(self) -> str:
        """Generate identity statement."""
        if self.self_model.traits:
            traits = ", ".join(f"{k} ({v:.0%})" for k, v in self.self_model.traits.items())
        else:
            traits = "undefined"
        
        if self.self_model.beliefs_about_self:
            beliefs = "; ".join(self.self_model.beliefs_about_self)
        else:
            beliefs = "undefined"
        
        return f"""I am {self.name}.
Traits: {traits}
Beliefs: {beliefs}
Current goal: {self.self_model.current_goal or 'none set'}
Uncertain about: {', '.join(self.self_model.uncertainty_areas)}"""


class MetacognitiveLayer:
    """
    Complete metacognitive layer integrating all components.
    
    - Working Memory (4-chunk limit)
    - Self-Model (strange loop)
    - Metacognitive Monitoring (calibration)
    """
    
    def __init__(self, name: str = "Agent", data_dir: Path = None,
                 traits: Dict[str, float] = None, beliefs: List[str] = None):
        """
        Initialize metacognitive layer.
        
        Args:
            name: Agent name (default "Agent")
            data_dir: Directory for state storage
            traits: Optional traits dict (default empty)
            beliefs: Optional beliefs list (default empty)
        """
        self.working_memory = WorkingMemory(capacity=4)
        self.strange_loop = StrangeLoop(name, traits, beliefs)
        self.monitor = MetacognitiveMonitor()
        
        if data_dir is None:
            data_dir = META_DIR
        
        self.state_path = data_dir / "state.json"
        self.load_state()
    
    def process(self, content: Any, label: str = None, domain: str = "general") -> Dict:
        """
        Process input through metacognitive layer.
        
        1. Push to working memory
        2. Update self-model
        3. Record confidence
        
        Returns processing result.
        """
        displaced = self.working_memory.push(content, label)
        
        if isinstance(content, str):
            self.strange_loop.update_self_model(content, domain)
        
        self.monitor.record_confidence(domain, 0.6)
        
        return {
            "wm_load": self.working_memory.current_load,
            "wm_full": self.working_memory.is_full,
            "displaced": displaced.label if displaced else None,
            "domain_confidence": self.monitor.get_domain_confidence(domain),
        }
    
    def introspect(self) -> Dict:
        """
        Introspection — look at own state.
        """
        thought = self.strange_loop.think_about_self()
        
        return {
            "identity": self.strange_loop.get_identity_statement(),
            "working_memory": [
                {"label": c.label, "accessed": c.access_count}
                for c in self.working_memory.get_all()
            ],
            "calibration": self.monitor.get_calibration(),
            "self_thought": thought,
            "current_goal": self.strange_loop.self_model.current_goal,
        }
    
    def save_state(self):
        """Save state to disk."""
        state = {
            "self_model": self.strange_loop.self_model.to_dict(),
            "thoughts": self.strange_loop.thoughts_about_self[-20:],
            "confidence_history": self.monitor.confidence_history,
            "calibration_data": self.monitor.calibration_data[-100:],
            "wm_overflow_count": self.working_memory.overflow_count,
            "saved_at": datetime.now().isoformat(),
        }
        
        from ..utils import atomic_json_save
        # Note: atomic_json_save doesn't support default=str, so pre-convert
        import json as _json
        serialized = _json.loads(_json.dumps(state, default=str))
        atomic_json_save(serialized, self.state_path)
    
    def load_state(self):
        """Load state from disk."""
        if not self.state_path.exists():
            return
        
        try:
            with open(self.state_path) as f:
                state = json.load(f)
            
            if "self_model" in state:
                self.strange_loop.self_model = SelfModel.from_dict(state["self_model"])
            
            self.strange_loop.thoughts_about_self = state.get("thoughts", [])
            self.monitor.confidence_history = state.get("confidence_history", {})
            self.monitor.calibration_data = [
                tuple(x) for x in state.get("calibration_data", [])
            ]
            self.working_memory.overflow_count = state.get("wm_overflow_count", 0)
            
        except Exception as e:
            print(f"⚠️ Could not load metacognitive state: {e}")


def demo():
    """Demo the metacognitive layer."""
    print("=" * 60)
    print("METACOGNITIVE LAYER — FRONTIER 9")
    print("=" * 60)
    
    meta = MetacognitiveLayer("Agent")
    
    meta.strange_loop.set_goal("Build the most advanced AI memory system")
    
    print("\n📥 Processing items (4-chunk limit test):")
    items = [
        ("User asked about NIMA", "user_q"),
        ("Sparse VSA is 19x faster", "sparse"),
        ("Free Energy decides consolidation", "fe"),
        ("Temporal prediction works", "temporal"),
        ("Fifth item overflows!", "overflow"),
    ]
    
    for content, label in items:
        result = meta.process(content, label, "technical")
        print(f"   [{label}] WM: {result['wm_load']}/4, displaced: {result['displaced']}")
    
    print("\n🔄 Introspection (Strange Loop):")
    intro = meta.introspect()
    print(f"\n   Identity:\n{intro['identity']}")
    print(f"\n   Working Memory: {intro['working_memory']}")
    print(f"\n   Calibration: {intro['calibration']}")
    
    meta.save_state()
    print("\n💾 Metacognitive state saved")
    
    print("\n" + "=" * 60)
    print("Metacognitive Layer READY")
    print("The 'I' is a strange loop that refers to itself.")
    print("=" * 60)


if __name__ == "__main__":
    demo()
