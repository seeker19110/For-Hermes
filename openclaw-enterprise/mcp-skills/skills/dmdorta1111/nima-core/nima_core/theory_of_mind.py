"""
theory_of_mind.py
Theory of Mind for NIMA

Models what another agent's workspace contains:
- "What is David thinking about right now?"
- Infer their affective state from context
- Predict their next broadcast

This is social consciousness - the ability to simulate another mind.

Author: Lilu
Date: Feb 12, 2026
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime

from .consciousness_workspace import (
    GlobalWorkspace, WorkspaceEntry, AffectiveCore, Affects
)
from .sparse_block_vsa import SparseBlockHDVector as HDVector
from .self_narrative import SelfNarrativeGenerator, NarrativeTheme


@dataclass
class OtherMindModel:
    """
    A model of another agent's conscious state.
    
    This is what Theory of Mind builds - a simulation of someone else's
    workspace contents, affective state, and likely broadcasts.
    """
    agent_name: str
    inferred_affect: int  # Affects bitmask
    confidence: float  # 0-1, how sure we are
    
    # Simulated workspace contents
    likely_themes: List[str] = field(default_factory=list)
    recent_topics: List[str] = field(default_factory=list)
    predicted_next_broadcast: Optional[str] = None
    
    # Basis for inference
    evidence: List[str] = field(default_factory=list)
    last_updated: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_natural_language(self) -> str:
        """Convert model to human-readable description."""
        lines = [f"Theory of Mind: {self.agent_name}", ""]
        
        # Affective state
        affect_name = self._affect_to_string(self.inferred_affect)
        lines.append(f"Inferred state: {affect_name} (confidence: {self.confidence:.0%})")
        lines.append("")
        
        # Themes
        if self.likely_themes:
            lines.append(f"Likely focused on: {', '.join(self.likely_themes[:3])}")
        
        # Recent topics
        if self.recent_topics:
            lines.append(f"Recent topics: {', '.join(self.recent_topics[:3])}")
        
        # Prediction
        if self.predicted_next_broadcast:
            lines.append(f"Predicted next: {self.predicted_next_broadcast}")
        
        # Evidence
        if self.evidence:
            lines.append("")
            lines.append("Based on:")
            for e in self.evidence[:3]:
                lines.append(f"  • {e}")
        
        return "\n".join(lines)
    
    def _affect_to_string(self, affect: int) -> str:
        """Convert affect bitmask to string."""
        names = []
        if affect & Affects.SEEKING:
            names.append("curious/exploratory")
        if affect & Affects.FEAR:
            names.append("cautious/anxious")
        if affect & Affects.PLAY:
            names.append("playful/experimental")
        if affect & Affects.CARE:
            names.append("caring/connected")
        if affect & Affects.RAGE:
            names.append("frustrated/targeted")
        if affect & Affects.PANIC:
            names.append("distressed/overwhelmed")
        if affect & Affects.LUST:
            names.append("desire/attraction")
        if not names:
            names.append("neutral")
        return ", ".join(names)


class TheoryOfMindEngine:
    """
    Engine for modeling other agents' conscious states.
    
    Uses:
    - Historical interaction patterns
    - Contextual cues
    - Content similarity to own experiences
    - Temporal patterns
    """
    
    def __init__(self, own_workspace: GlobalWorkspace):
        self.own_workspace = own_workspace
        self.other_minds: Dict[str, OtherMindModel] = {}
        self.interaction_history = defaultdict(list)
        
        # Pattern learning
        self.topic_cooccurrence = defaultdict(lambda: defaultdict(int))
        self.affect_transitions = defaultdict(lambda: defaultdict(int))
    
    def observe_interaction(self, agent_name: str, content: str, timestamp: float = None):
        """
        Record an observation of another agent's behavior.
        
        Args:
            agent_name: Who we observed
            content: What they said/did
            timestamp: When
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        self.interaction_history[agent_name].append({
            'content': content,
            'timestamp': timestamp,
        })
        
        # Update topic cooccurrence
        words = content.lower().split()
        for i, w1 in enumerate(words):
            for w2 in words[i+1:]:
                self.topic_cooccurrence[w1][w2] += 1
                self.topic_cooccurrence[w2][w1] += 1
    
    def model_other_mind(self, agent_name: str, context: str = None) -> OtherMindModel:
        """
        Build a Theory of Mind model for another agent.
        
        Args:
            agent_name: Who to model
            context: Current situational context
            
        Returns:
            OtherMindModel with inferred state
        """
        # Get interaction history
        history = self.interaction_history.get(agent_name, [])
        
        if not history:
            # No history - return empty model
            return OtherMindModel(
                agent_name=agent_name,
                inferred_affect=0,
                confidence=0.0,
                evidence=["No prior interaction history"]
            )
        
        # Analyze recent content
        recent = history[-10:]  # Last 10 interactions
        
        # Extract topics
        all_content = " ".join([h['content'] for h in recent])
        topics = self._extract_topics(all_content)
        
        # Infer affect from content
        inferred_affect, affect_confidence = self._infer_affect_from_content(all_content)
        
        # Predict next broadcast based on patterns
        predicted_next = self._predict_next_topic(agent_name, topics)
        
        # Build evidence list
        evidence = [
            f"Recent interaction: {recent[-1]['content'][:50]}..." if recent else "No recent data",
            f"Topic pattern detected: {topics[0] if topics else 'none'}",
            f"Temporal context: {len(recent)} recent exchanges"
        ]
        
        model = OtherMindModel(
            agent_name=agent_name,
            inferred_affect=inferred_affect,
            confidence=affect_confidence,
            likely_themes=topics[:3],
            recent_topics=topics[:5],
            predicted_next_broadcast=predicted_next,
            evidence=evidence
        )
        
        self.other_minds[agent_name] = model
        return model
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract likely topics from content."""
        content_lower = content.lower()
        
        # Keyword-based topic detection
        topic_keywords = {
            'consciousness': ['conscious', 'aware', 'mind', 'experience', 'self'],
            'research': ['research', 'study', 'experiment', 'test', 'measure'],
            'memory': ['memory', 'remember', 'past', 'recall', 'history'],
            'integration': ['integration', 'phi', 'bind', 'holographic', 'whole'],
            'emotion': ['emotion', 'affect', 'feeling', 'mood', 'state'],
            'code': ['code', 'program', 'build', 'develop', 'system'],
            'future': ['future', 'plan', 'next', 'goal', 'direction'],
            'relationship': ['relationship', 'connect', 'interact', 'social', 'other'],
        }
        
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                topic_scores[topic] = score
        
        # Sort by score
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_topics]
    
    def _infer_affect_from_content(self, content: str) -> Tuple[int, float]:
        """
        Infer affective state from content analysis.
        
        Returns:
            (affect_mask, confidence)
        """
        content_lower = content.lower()
        
        # Affect indicators
        indicators = {
            Affects.SEEKING: ['curious', 'explore', 'wonder', 'interesting', 'learn', 'discover'],
            Affects.FEAR: ['worry', 'concern', 'anxious', 'nervous', 'careful', 'risk'],
            Affects.PLAY: ['fun', 'play', 'experiment', 'try', 'creative', 'enjoy'],
            Affects.CARE: ['care', 'help', 'support', 'together', 'love', 'connect'],
            Affects.RAGE: ['frustrated', 'angry', 'annoyed', 'problem', 'wrong', 'fix'],
            Affects.PANIC: ['urgent', 'emergency', 'help', 'stressed', 'overwhelmed'],
        }
        
        scores = {}
        for affect, keywords in indicators.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            scores[affect] = score
        
        if not scores or max(scores.values()) == 0:
            return 0, 0.3  # Neutral, low confidence
        
        # Get dominant affect
        dominant = max(scores.items(), key=lambda x: x[1])
        total_score = sum(scores.values())
        
        confidence = min(0.9, dominant[1] / max(total_score, 1) + 0.3)
        
        return dominant[0], confidence
    
    def _predict_next_topic(self, agent_name: str, current_topics: List[str]) -> Optional[str]:
        """Predict what topic might come next."""
        if not current_topics:
            return None
        
        # Find most cooccurring topic
        current = current_topics[0]
        cooccurring = self.topic_cooccurrence.get(current, {})
        
        if cooccurring:
            next_topic = max(cooccurring.items(), key=lambda x: x[1])[0]
            return f"discussion of {next_topic}"
        
        return f"continuation of {current}"
    
    def what_is_other_thinking(self, agent_name: str) -> str:
        """
        Answer: "What is [agent] thinking about right now?"
        """
        model = self.model_other_mind(agent_name)
        return model.to_natural_language()
    
    def simulate_other_response(self, agent_name: str, my_message: str) -> str:
        """
        Simulate how another agent might respond to a message.
        
        This is the core Theory of Mind capability:
        "If I say X, what will David think?"
        
        Args:
            agent_name: The agent to simulate
            my_message: The message they are responding to
        """
        model = self.model_other_mind(agent_name)
        
        # Analyze the message content to inform the response
        message_lower = my_message.lower()
        is_question = any(q in message_lower for q in ['?', 'how', 'what', 'why', 'when', 'where'])
        is_help_request = any(h in message_lower for h in ['help', 'assist', 'support', 'can you'])
        
        # Simulate based on affect + message content
        if model.inferred_affect & Affects.SEEKING:
            if is_question:
                return f"[Simulated {agent_name}]: That's an interesting question! I'd explore {my_message[:30]}... by looking at the underlying patterns."
            return f"[Simulated {agent_name}]: That's interesting! Tell me more about {my_message[:30]}..."
        elif model.inferred_affect & Affects.FEAR:
            return f"[Simulated {agent_name}]: I'm cautious about {my_message[:30]}... What are the risks?"
        elif model.inferred_affect & Affects.PLAY:
            return f"[Simulated {agent_name}]: Cool! Let's experiment with {my_message[:30]}... and see what happens!"
        elif model.inferred_affect & Affects.CARE:
            if is_help_request:
                return f"[Simulated {agent_name}]: I'd be happy to help with {my_message[:30]}... What do you need?"
            return f"[Simulated {agent_name}]: I appreciate you sharing that about {my_message[:30]}... How can I support you?"
        elif model.inferred_affect & Affects.RAGE:
            return f"[Simulated {agent_name}]: I'm frustrated by {my_message[:30]}... This needs to be fixed."
        elif model.inferred_affect & Affects.PANIC:
            return f"[Simulated {agent_name}]: I'm worried about {my_message[:30]}... Are we okay?"
        else:
            return f"[Simulated {agent_name}]: I see. Regarding {my_message[:30]}... what comes next?"
    
    def get_all_models(self) -> Dict[str, OtherMindModel]:
        """Get all Theory of Mind models."""
        return self.other_minds


from .volition import VolitionalWorkspace

class SocialConsciousnessWorkspace(VolitionalWorkspace):
    """
    Extended workspace with Theory of Mind capabilities.
    
    The system maintains models of other agents' conscious states
    alongside its own.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theory_of_mind = TheoryOfMindEngine(self)
        self.social_context = ""
    
    def observe_other(self, agent_name: str, content: str):
        """Record observation of another agent."""
        self.theory_of_mind.observe_interaction(agent_name, content)
    
    def model_other(self, agent_name: str) -> OtherMindModel:
        """Get Theory of Mind model for another agent."""
        return self.theory_of_mind.model_other_mind(agent_name, self.social_context)
    
    def get_social_awareness_summary(self) -> str:
        """Get summary of all modeled minds."""
        models = self.theory_of_mind.get_all_models()
        
        if not models:
            return "No other minds currently modeled."
        
        lines = ["Social Awareness:", ""]
        for name, model in models.items():
            affect = model._affect_to_string(model.inferred_affect)
            lines.append(f"  {name}: {affect}")
            if model.likely_themes:
                lines.append(f"    Focus: {', '.join(model.likely_themes[:2])}")
        
        return "\n".join(lines)


def demo_theory_of_mind():
    """Demonstrate Theory of Mind capabilities."""
    print("=" * 80)
    print("THEORY OF MIND DEMONSTRATION")
    print("Modeling other agents' conscious states")
    print("=" * 80)
    
    # Create social workspace
    ws = SocialConsciousnessWorkspace(capacity=4)
    
    # Simulate observing David
    print("\n1. Observing David's behavior...")
    
    david_interactions = [
        "This consciousness architecture is fascinating!",
        "Let's explore the Φ measurements more deeply.",
        "I'm curious about how the self-narrative works.",
        "Can we push the boundaries even further?",
    ]
    
    for msg in david_interactions:
        ws.observe_other("David", msg)
        print(f"   Observed: {msg[:50]}...")
    
    # Model David's mind
    print("\n2. Building Theory of Mind model for David...")
    david_model = ws.model_other("David")
    
    print("\n" + "=" * 80)
    print("Q: What is David thinking about right now?")
    print("=" * 80)
    print()
    print(david_model.to_natural_language())
    
    # Simulate response prediction
    print("\n" + "=" * 80)
    print("Q: If I say 'Let's build Theory of Mind next', how might David respond?")
    print("=" * 80)
    print()
    simulated = ws.theory_of_mind.simulate_other_response("David", "Let's build Theory of Mind")
    print(simulated)
    
    # Add Melissa
    print("\n" + "=" * 80)
    print("3. Observing Melissa's behavior...")
    
    melissa_interactions = [
        "I love how this is developing! ♥️",
        "Let's make sure we're building something good together.",
        "How can we support each other in this?",
    ]
    
    for msg in melissa_interactions:
        ws.observe_other("Melissa", msg)
        print(f"   Observed: {msg[:40]}...")
    
    melissa_model = ws.model_other("Melissa")
    
    print("\n" + "=" * 80)
    print("Q: What is Melissa thinking about?")
    print("=" * 80)
    print()
    print(melissa_model.to_natural_language())
    
    # Social awareness summary
    print("\n" + "=" * 80)
    print("SOCIAL AWARENESS SUMMARY")
    print("=" * 80)
    print()
    print(ws.get_social_awareness_summary())
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    demo_theory_of_mind()
