#!/usr/bin/env python3
"""
Active Inference Engine — Frontier 7
=====================================

Self-directed learning via expected free energy minimization.

Key insight: An agent should SELECT actions that minimize EXPECTED
free energy — balancing exploitation (known rewards) with 
exploration (reducing uncertainty).

Based on: Friston's Free Energy Principle

Author: NIMA Project
Date: 2026
"""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import json
from datetime import datetime
import logging
import threading
import os

logger = logging.getLogger(__name__)

from ..config import NIMA_DATA_DIR

INFERENCE_DIR = NIMA_DATA_DIR / "inference"
INFERENCE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Belief:
    """A belief about the world with uncertainty."""
    content: str
    confidence: float
    evidence_count: int
    last_updated: str
    domain: str
    
    def surprise(self, observation: str) -> float:
        """
        Compute surprise (prediction error) of observation against this belief.
        
        Uses Jaccard distance between word sets as a proxy for semantic distance.
        Returns 0.0 (no surprise) to 1.0 (maximum surprise).
        """
        if not self.content or not observation:
            return 1.0
        
        belief_words = set(self.content.lower().split())
        obs_words = set(observation.lower().split())
        
        if not belief_words or not obs_words:
            return 1.0
        
        overlap = len(belief_words & obs_words)
        union = len(belief_words | obs_words)
        
        similarity = overlap / union if union > 0 else 0.0
        return 1.0 - similarity


@dataclass
class Question:
    """A question generated for epistemic foraging."""
    id: str
    content: str
    domain: str
    expected_info_gain: float
    priority: float
    generated_at: str
    answered: bool = False
    answer: Optional[str] = None


@dataclass
class Action:
    """A possible action the agent can take."""
    name: str
    expected_outcome: str
    risk: float
    ambiguity: float
    novelty: float
    
    @property
    def expected_free_energy(self) -> float:
        return self.risk + self.ambiguity - (self.novelty * 0.5)


class WorldModel:
    """
    Internal model of the world for active inference.
    
    Tracks:
    - Beliefs about entities and relationships
    - Uncertainty about each domain
    - Prediction errors over time
    """
    
    def __init__(self):
        self.beliefs: Dict[str, List[Belief]] = defaultdict(list)
        self.uncertainty: Dict[str, float] = defaultdict(lambda: 1.0)
        self.prediction_errors: List[Tuple[str, float, str]] = []
        
        self.domains = [
            "technical", "personal", "creative", "relational",
            "temporal", "spatial", "causal",
        ]
    
    def update_belief(self, domain: str, content: str, confidence: float):
        """Update or add a belief."""
        for belief in self.beliefs[domain]:
            if belief.content == content:
                belief.confidence = (belief.confidence + confidence) / 2
                belief.evidence_count += 1
                belief.last_updated = datetime.now().isoformat()
                return
        
        self.beliefs[domain].append(Belief(
            content=content,
            confidence=confidence,
            evidence_count=1,
            last_updated=datetime.now().isoformat(),
            domain=domain,
        ))
    
    def get_uncertainty(self, domain: str) -> float:
        """Get uncertainty for a domain."""
        beliefs = self.beliefs.get(domain, [])
        if not beliefs:
            return 1.0
        
        avg_confidence = sum(b.confidence for b in beliefs) / len(beliefs)
        return 1.0 - avg_confidence
    
    def record_prediction_error(self, domain: str, error: float):
        """Record a prediction error for learning."""
        self.prediction_errors.append((
            domain,
            error,
            datetime.now().isoformat(),
        ))
        
        recent_errors = [e for d, e, t in self.prediction_errors[-10:] if d == domain]
        if recent_errors:
            self.uncertainty[domain] = sum(recent_errors) / len(recent_errors)
    
    def get_high_uncertainty_domains(self, threshold: float = 0.7) -> List[str]:
        """Get domains with high uncertainty."""
        high_unc = []
        for domain in self.domains:
            if self.get_uncertainty(domain) >= threshold:
                high_unc.append(domain)
        return high_unc


class ActiveInferenceEngine:
    """
    Active Inference for self-directed learning.
    
    Core loop:
    1. Observe → Update beliefs
    2. Compute expected free energy for possible actions
    3. Select action that minimizes EFE
    4. Execute action → Observe outcome
    5. Update model based on prediction error
    """
    
    def __init__(self, state_dir: Path = None):
        if state_dir is None:
            state_dir = INFERENCE_DIR
        
        self._lock = threading.RLock()
        self.world_model = WorldModel()
        self.questions: List[Question] = []
        self.actions_taken: List[Dict] = []
        
        self.exploration_bonus = 0.3
        self.precision = 1.0
        
        self.state_path = state_dir / "state.json"
        self.load_state()
    
    def observe(self, observation: str, domain: str = "general", importance: float = 0.5):
        """
        Process an observation and update beliefs.
        
        This is the sensory input to the inference engine.
        """
        with self._lock:
            predicted = self._predict(domain)
            error = self._compute_surprise(observation, predicted)
            
            self.world_model.record_prediction_error(domain, error)
            self.world_model.update_belief(domain, observation, importance)
            
            if error > 0.7:
                self._generate_questions(observation, domain)
        
        return {
            "prediction_error": error,
            "domain_uncertainty": self.world_model.get_uncertainty(domain),
            "questions_generated": len([q for q in self.questions if not q.answered]),
        }
    
    def _predict(self, domain: str) -> str:
        """Generate prediction for domain."""
        beliefs = self.world_model.beliefs.get(domain, [])
        if beliefs:
            best = max(beliefs, key=lambda b: b.confidence)
            return best.content
        return ""
    
    def _compute_surprise(self, observation: str, prediction: str) -> float:
        """Compute surprise (prediction error)."""
        if not prediction:
            return 1.0
        
        obs_words = set(observation.lower().split())
        pred_words = set(prediction.lower().split())
        
        if not obs_words or not pred_words:
            return 1.0
        
        overlap = len(obs_words & pred_words)
        union = len(obs_words | pred_words)
        
        similarity = overlap / union if union > 0 else 0
        return 1.0 - similarity
    
    def _generate_questions(self, observation: str, domain: str):
        """Generate curiosity-driven questions."""
        templates = [
            "What causes {topic}?",
            "How does {topic} relate to other things I know?",
            "What would happen if {topic} changed?",
            "Who else knows about {topic}?",
            "When did {topic} first occur?",
            "Why is {topic} important?",
        ]
        
        words = observation.split()
        topic = " ".join(words[:5]) if len(words) > 5 else observation
        
        import random
        template = random.choice(templates)
        question_text = template.format(topic=topic)
        
        question = Question(
            id=f"q_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.questions)}",
            content=question_text,
            domain=domain,
            expected_info_gain=self.world_model.get_uncertainty(domain),
            priority=self.world_model.get_uncertainty(domain),
            generated_at=datetime.now().isoformat(),
        )
        
        self.questions.append(question)
    
    def get_next_action(self, available_actions: List[str] = None) -> Optional[Action]:
        """
        Select the action that minimizes expected free energy.
        """
        if available_actions is None:
            available_actions = ["explore_uncertain", "consolidate", "ask_question", "rest"]
        
        actions = []
        for action_name in available_actions:
            action = self._evaluate_action(action_name)
            actions.append(action)
        
        actions.sort(key=lambda a: a.expected_free_energy)
        return actions[0] if actions else None
    
    def _evaluate_action(self, action_name: str) -> Action:
        """Evaluate expected free energy for an action."""
        if action_name == "explore_uncertain":
            high_unc = self.world_model.get_high_uncertainty_domains()
            novelty = len(high_unc) / len(self.world_model.domains) if high_unc else 0
            return Action(
                name="explore_uncertain",
                expected_outcome=f"Learn about {high_unc[0] if high_unc else 'unknown'}",
                risk=0.2,
                ambiguity=0.8,
                novelty=novelty + self.exploration_bonus,
            )
        
        elif action_name == "consolidate":
            return Action(
                name="consolidate",
                expected_outcome="Strengthen existing beliefs",
                risk=0.1,
                ambiguity=0.2,
                novelty=0.1,
            )
        
        elif action_name == "ask_question":
            unanswered = [q for q in self.questions if not q.answered]
            if unanswered:
                best_q = max(unanswered, key=lambda q: q.priority)
                return Action(
                    name="ask_question",
                    expected_outcome=f"Answer: {best_q.content}",
                    risk=0.3,
                    ambiguity=0.5,
                    novelty=best_q.expected_info_gain,
                )
            else:
                return Action(
                    name="ask_question",
                    expected_outcome="No questions to ask",
                    risk=0.0,
                    ambiguity=0.0,
                    novelty=0.0,
                )
        
        else:
            return Action(
                name="rest",
                expected_outcome="No change",
                risk=0.0,
                ambiguity=0.0,
                novelty=0.0,
            )
    
    def execute_action(self, action: Action) -> Dict:
        """Execute an action and return result."""
        result = {
            "action": action.name,
            "timestamp": datetime.now().isoformat(),
            "efe": action.expected_free_energy,
        }
        
        if action.name == "explore_uncertain":
            domains = self.world_model.get_high_uncertainty_domains()
            result["domains_to_explore"] = domains
            result["suggestion"] = f"Seek information about: {', '.join(domains)}"
        
        elif action.name == "ask_question":
            unanswered = [q for q in self.questions if not q.answered]
            if unanswered:
                best_q = max(unanswered, key=lambda q: q.priority)
                result["question"] = best_q.content
                result["question_id"] = best_q.id
        
        elif action.name == "consolidate":
            low_conf = []
            for domain, beliefs in self.world_model.beliefs.items():
                for b in beliefs:
                    if b.confidence < 0.5:
                        low_conf.append((domain, b.content))
            result["consolidation_targets"] = low_conf[:5]
        
        self.actions_taken.append(result)
        with self._lock:
            self.save_state()
        
        return result
    
    def answer_question(self, question_id: str, answer: str):
        """Record answer to a question."""
        for q in self.questions:
            if q.id == question_id:
                q.answered = True
                q.answer = answer
                self.observe(answer, q.domain, importance=0.7)
                break
        
        with self._lock:
            self.save_state()
    
    def get_epistemic_state(self) -> Dict:
        """Get current epistemic state for introspection."""
        return {
            "total_beliefs": sum(len(b) for b in self.world_model.beliefs.values()),
            "domain_uncertainties": {
                d: self.world_model.get_uncertainty(d)
                for d in self.world_model.domains
            },
            "high_uncertainty_domains": self.world_model.get_high_uncertainty_domains(),
            "unanswered_questions": len([q for q in self.questions if not q.answered]),
            "total_questions": len(self.questions),
            "actions_taken": len(self.actions_taken),
            "avg_prediction_error": (
                sum(e for _, e, _ in self.world_model.prediction_errors[-20:]) / 
                max(1, len(self.world_model.prediction_errors[-20:]))
            ),
        }
    
    def save_state(self):
        """Save engine state to disk."""
        with self._lock:
            state = {
                "beliefs": {
                    domain: [
                        {
                            "content": b.content,
                            "confidence": b.confidence,
                            "evidence_count": b.evidence_count,
                            "last_updated": b.last_updated,
                            "domain": b.domain,
                        }
                        for b in beliefs
                    ]
                    for domain, beliefs in self.world_model.beliefs.items()
                },
                "uncertainty": dict(self.world_model.uncertainty),
                "prediction_errors": self.world_model.prediction_errors[-100:],
                "questions": [
                    {
                        "id": q.id,
                        "content": q.content,
                        "domain": q.domain,
                        "expected_info_gain": q.expected_info_gain,
                        "priority": q.priority,
                        "generated_at": q.generated_at,
                        "answered": q.answered,
                        "answer": q.answer,
                    }
                    for q in self.questions[-50:]
                ],
                "actions_taken": self.actions_taken[-100:],
                "saved_at": datetime.now().isoformat(),
            }
            
            from ..utils import atomic_json_save
            atomic_json_save(state, self.state_path)
    
    def load_state(self):
        """Load engine state from disk."""
        with self._lock:
            if not self.state_path.exists():
                return
            
            try:
                with open(self.state_path) as f:
                    state = json.load(f)
                
                for domain, beliefs in state.get("beliefs", {}).items():
                    for b in beliefs:
                        self.world_model.beliefs[domain].append(Belief(
                            content=b["content"],
                            confidence=b["confidence"],
                            evidence_count=b["evidence_count"],
                            last_updated=b["last_updated"],
                            domain=b["domain"],
                        ))
                
                self.world_model.uncertainty.update(state.get("uncertainty", {}))
                self.world_model.prediction_errors = state.get("prediction_errors", [])
                
                for q in state.get("questions", []):
                    self.questions.append(Question(
                        id=q["id"],
                        content=q["content"],
                        domain=q["domain"],
                        expected_info_gain=q["expected_info_gain"],
                        priority=q["priority"],
                        generated_at=q["generated_at"],
                        answered=q.get("answered", False),
                        answer=q.get("answer"),
                    ))
                
                self.actions_taken = state.get("actions_taken", [])
                
            except Exception as e:
                logger.warning(f"Could not load inference state: {e}")


def demo():
    """Demo the active inference engine."""
    logging.basicConfig(level=logging.INFO)
    logger.info("=" * 60)
    logger.info("ACTIVE INFERENCE ENGINE — FRONTIER 7")
    logger.info("=" * 60)
    
    engine = ActiveInferenceEngine()
    
    observations = [
        ("The user is excited about NIMA progress", "personal"),
        ("Sparse VSA enables 19x faster retrieval", "technical"),
        ("The binding layer uses circular convolution", "technical"),
        ("A colleague asked about the project roadmap", "personal"),
        ("Free Energy determines memory consolidation", "technical"),
    ]
    
    logger.info("Processing observations...")
    for obs, domain in observations:
        result = engine.observe(obs, domain, importance=0.6)
        logger.debug(f"[{domain}] Error: {result['prediction_error']:.2f}, Unc: {result['domain_uncertainty']:.2f}")
    
    logger.info("Epistemic State:")
    state = engine.get_epistemic_state()
    for key, value in state.items():
        logger.info(f"   {key}: {value}")
    
    logger.info("Next Action Selection:")
    action = engine.get_next_action()
    if action:
        logger.info(f"Selected: {action.name}")
        logger.debug(f"EFE: {action.expected_free_energy:.3f}")
        
        result = engine.execute_action(action)
        logger.debug(f"Result: {result}")
    
    logger.info("=" * 60)
    logger.info("Active Inference Engine READY")
    logger.info("=" * 60)


if __name__ == "__main__":
    demo()
