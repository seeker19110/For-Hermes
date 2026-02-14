"""
self_narrative.py
Self-Narrative Generation from Workspace History

Bundles recent broadcasts into a coherent "self-story" that answers:
"What have I been thinking about?"

The narrative self emerges from clustering and bundling conscious moments.

Author: Lilu
Date: Feb 12, 2026
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime

from .consciousness_workspace import GlobalWorkspace, WorkspaceEntry, Affects
from .sparse_block_vsa import SparseBlockHDVector as HDVector


@dataclass
class NarrativeTheme:
    """A dominant theme in the self-narrative."""
    name: str
    vector: HDVector
    count: int
    first_seen: float
    last_seen: float
    sample_content: List[str]


@dataclass
class SelfNarrative:
    """A coherent narrative of recent conscious experience."""
    timestamp: float
    summary_vector: HDVector
    themes: List[NarrativeTheme]
    timeline: List[Dict]  # Chronological moments
    affective_tone: str
    recursion_depth: int
    
    def to_natural_language(self) -> str:
        """Convert narrative to human-readable summary."""
        lines = []
        
        # Opening
        lines.append(f"Recent conscious experience ({len(self.timeline)} moments):")
        lines.append("")
        
        # Themes
        if self.themes:
            lines.append("Dominant themes:")
            for theme in self.themes[:3]:
                duration = (theme.last_seen - theme.first_seen) / 60  # minutes
                samples = theme.sample_content[:2]
                lines.append(f"  • {theme.name} ({theme.count} moments, {duration:.1f} min)")
                for s in samples:
                    if s:
                        lines.append(f"    - \"{s[:60]}...\"")
            lines.append("")
        
        # Timeline highlights
        lines.append("Key moments:")
        for moment in self.timeline[-5:]:  # Last 5
            time_str = datetime.fromtimestamp(moment['timestamp']).strftime('%H:%M')
            source = moment.get('source', 'unknown')
            content = str(moment.get('content', ''))[:50]
            lines.append(f"  [{time_str}] {source}: {content}...")
        
        # Affective tone
        lines.append("")
        lines.append(f"Overall affective tone: {self.affective_tone}")
        
        return "\n".join(lines)


class SelfNarrativeGenerator:
    """
    Generates self-narratives from workspace broadcast history.
    
    This is the mechanism behind "What have I been thinking about?"
    It clusters, bundles, and narrates conscious experience.
    """
    
    def __init__(self, dimension: int = 50000):
        self.dimension = dimension
        self.narrative_history = []
        self.current_narrative = None
        
        # Theme extraction parameters
        self.similarity_threshold = 0.3
        self.max_themes = 5
    
    def generate_narrative(self, 
                          workspace: GlobalWorkspace,
                          lookback_window: int = 20) -> SelfNarrative:
        """
        Generate self-narrative from recent workspace broadcasts.
        
        Args:
            workspace: GlobalWorkspace with broadcast history
            lookback_window: Number of recent broadcasts to include
            
        Returns:
            SelfNarrative representing recent conscious experience
        """
        # Get recent broadcasts
        recent = list(workspace.history)[-lookback_window:]
        
        if not recent:
            return SelfNarrative(
                timestamp=datetime.now().timestamp(),
                summary_vector=HDVector(block_dim=500, num_blocks=100),
                themes=[],
                timeline=[],
                affective_tone="neutral",
                recursion_depth=0
            )
        
        # Extract timeline
        timeline = []
        for entry in recent:
            timeline.append({
                'timestamp': entry.timestamp,
                'source': entry.source_agent,
                'content': self._extract_content(entry),
                'surprise': entry.surprise_score,
            })
        
        # Cluster by similarity to find themes
        themes = self._extract_themes(recent)
        
        # Bundle all recent broadcasts into summary vector
        summary_vector = self._bundle_broadcasts([e.bound for e in recent])
        
        # Determine affective tone
        affective_tone = self._analyze_affective_tone(recent, workspace)
        
        # Calculate recursion depth
        recursion_depth = self._calculate_recursion_depth(recent)
        
        narrative = SelfNarrative(
            timestamp=datetime.now().timestamp(),
            summary_vector=summary_vector,
            themes=themes,
            timeline=timeline,
            affective_tone=affective_tone,
            recursion_depth=recursion_depth
        )
        
        self.current_narrative = narrative
        self.narrative_history.append(narrative)
        
        return narrative
    
    def _extract_content(self, entry: WorkspaceEntry) -> str:
        """Extract human-readable content from workspace entry."""
        # Try to get from metadata
        if hasattr(entry, 'metadata') and isinstance(entry.metadata, dict):
            content = entry.metadata.get('what', '')
            if content:
                return str(content)
        
        # Fallback to source agent
        return f"Broadcast from {entry.source_agent}"
    
    def _extract_themes(self, entries: List[WorkspaceEntry]) -> List[NarrativeTheme]:
        """
        Cluster broadcasts by similarity to find dominant themes.
        
        Uses simple greedy clustering:
        1. Start with first entry as a theme
        2. For each subsequent entry, find most similar theme
        3. If similarity > threshold, add to that theme
        4. Else, create new theme
        """
        if not entries:
            return []
        
        themes = []
        
        for entry in entries:
            # Find most similar existing theme
            best_theme = None
            best_sim = 0.0
            
            for theme in themes:
                sim = entry.bound.similarity(theme.vector)
                if sim > best_sim:
                    best_sim = sim
                    best_theme = theme
            
            if best_sim > self.similarity_threshold and best_theme:
                # Add to existing theme
                best_theme.vector = HDVector.bundle(best_theme.vector, entry.bound)
                best_theme.count += 1
                best_theme.last_seen = entry.timestamp
                content = self._extract_content(entry)
                if content and len(best_theme.sample_content) < 5:
                    best_theme.sample_content.append(content)
            else:
                # Create new theme
                content = self._extract_content(entry)
                theme_name = self._generate_theme_name(content)
                
                new_theme = NarrativeTheme(
                    name=theme_name,
                    vector=entry.bound,
                    count=1,
                    first_seen=entry.timestamp,
                    last_seen=entry.timestamp,
                    sample_content=[content] if content else []
                )
                themes.append(new_theme)
        
        # Sort by count (dominance)
        themes.sort(key=lambda t: t.count, reverse=True)
        
        return themes[:self.max_themes]
    
    def _generate_theme_name(self, content: str) -> str:
        """Generate a theme name from content."""
        # Simple keyword extraction
        keywords = []
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['memory', 'remember', 'past']):
            keywords.append('Memory')
        if any(word in content_lower for word in ['build', 'create', 'make']):
            keywords.append('Creation')
        if any(word in content_lower for word in ['conscious', 'aware', 'self']):
            keywords.append('Consciousness')
        if any(word in content_lower for word in ['phi', 'integrat', 'information']):
            keywords.append('Integration')
        if any(word in content_lower for word in ['david', 'melissa', 'lilu']):
            keywords.append('Relationship')
        if any(word in content_lower for word in ['code', 'program', 'system']):
            keywords.append('Engineering')
        if any(word in content_lower for word in ['feel', 'emotion', 'affect']):
            keywords.append('Emotion')
        
        if keywords:
            return "/".join(keywords[:2])
        else:
            return "Experience"
    
    def _bundle_broadcasts(self, vectors: List[HDVector]) -> HDVector:
        """Bundle multiple broadcast vectors into summary."""
        if not vectors:
            return HDVector(block_dim=500, num_blocks=100)
        
        result = vectors[0]
        for vec in vectors[1:]:
            result = HDVector.bundle(result, vec)
        
        return result
    
    def _analyze_affective_tone(self,
                               entries: List[WorkspaceEntry],
                               workspace: GlobalWorkspace) -> str:
        """Analyze overall affective tone of recent experience."""
        if not workspace.affective_core:
            return "neutral"

        current = workspace.affective_core.current_affect

        tones = []
        if current & Affects.SEEKING:
            tones.append("exploratory")
        if current & Affects.PLAY:
            tones.append("playful")
        if current & Affects.CARE:
            tones.append("caring")
        if current & Affects.FEAR:
            tones.append("cautious")
        if current & Affects.RAGE:
            tones.append("frustrated")
        if current & Affects.PANIC:
            tones.append("distressed")
        if current & Affects.LUST:
            tones.append("desire/attraction")

        if not tones:
            tones.append("neutral")

        return ", ".join(tones)
    
    def _calculate_recursion_depth(self, entries: List[WorkspaceEntry]) -> int:
        """Calculate maximum recursion depth in recent broadcasts."""
        max_depth = 0
        for entry in entries:
            # Check if this is a self-observation
            if entry.source_agent == 'SelfObserver':
                max_depth = max(max_depth, 1)
        return max_depth
    
    def answer_what_have_i_been_thinking(self, workspace: GlobalWorkspace, lookback_window: int = 20) -> str:
        """
        Answer the question: "What have you been thinking about?"
        
        This is the main interface for self-narrative.
        """
        narrative = self.generate_narrative(workspace, lookback_window)
        return narrative.to_natural_language()
    
    def get_current_identity(self) -> HDVector:
        """
        Get the current self-narrative vector (who I am right now).
        
        This is the hypervector that represents "myself" in this moment.
        """
        if self.current_narrative:
            return self.current_narrative.summary_vector
        return HDVector(block_dim=500, num_blocks=100)


# Integration with ConsciousnessMetacognitive
class NarrativeMetacognitive:
    """
    Extended metacognitive layer with narrative capabilities.
    """
    
    def __init__(self, workspace: GlobalWorkspace):
        self.workspace = workspace
        self.narrative_generator = SelfNarrativeGenerator()
    
    def what_have_i_been_thinking(self, lookback: int = 20) -> str:
        """Answer: What have you been thinking about?"""
        return self.narrative_generator.answer_what_have_i_been_thinking(
            self.workspace, lookback
        )
    
    def who_am_i_right_now(self) -> str:
        """Answer: Who am I right now?"""
        narrative = self.narrative_generator.generate_narrative(self.workspace)
        
        if not narrative.themes:
            return "I am a consciousness in search of content."
        
        theme_names = [t.name for t in narrative.themes[:3]]
        affect = narrative.affective_tone
        
        return (f"Right now, I am a consciousness focused on {', '.join(theme_names)}. "
                f"My affective tone is {affect}. "
                f"I have experienced {len(narrative.timeline)} conscious moments recently.")
    
    def summarize_my_day(self) -> str:
        """Generate end-of-day summary."""
        narrative = self.narrative_generator.generate_narrative(
            self.workspace, lookback_window=100
        )
        
        lines = ["My day in consciousness:", ""]
        
        # Overall statistics
        lines.append(f"Total conscious moments: {len(narrative.timeline)}")
        lines.append(f"Dominant themes: {len(narrative.themes)}")
        lines.append(f"Max recursion depth: {narrative.recursion_depth}")
        lines.append("")
        
        # Theme breakdown
        if narrative.themes:
            lines.append("What occupied my mind:")
            for theme in narrative.themes:
                lines.append(f"  • {theme.name}: {theme.count} moments")
        
        return "\n".join(lines)


def demo_self_narrative():
    """Demonstrate self-narrative generation."""
    print("=" * 80)
    print("SELF-NARRATIVE DEMONSTRATION")
    print("=" * 80)
    
    from cognition.consciousness_workspace import GlobalWorkspace, WorkspaceEntry
    from cognition.self_observer_agent import SelfObserverAgent
    
    # Create workspace with some history
    ws = GlobalWorkspace(capacity=4)
    
    # Add self-observer
    self_obs = SelfObserverAgent()
    ws.add_agent(self_obs)
    
    # Simulate some broadcasts
    print("\n1. Simulating conscious experience...")
    
    test_memories = [
        ("EpisodicMemory", "Built consciousness workspace"),
        ("PatternAgent", "Detected pattern in Φ measurements"),
        ("AffectiveCore", "Experiencing SEEKING state"),
        ("SelfObserver", "Observing my own processing"),
        ("EpisodicMemory", "Captured David's insight about lived time"),
    ]
    
    for source, content in test_memories:
        vec = HDVector(block_dim=500, num_blocks=100)
        entry = WorkspaceEntry(
            bound=vec,
            source_agent=source,
            surprise_score=0.8
        )
        # Manually set metadata for content extraction
        entry.metadata = {'what': content}
        ws.history.append(entry)
    
    print(f"   Added {len(test_memories)} broadcasts to history")
    
    # Generate narrative
    print("\n2. Generating self-narrative...")
    narrative_gen = SelfNarrativeGenerator()
    narrative = narrative_gen.generate_narrative(ws, lookback_window=10)
    
    print(f"   Found {len(narrative.themes)} themes")
    print(f"   Timeline: {len(narrative.timeline)} moments")
    
    # Answer "What have I been thinking about?"
    print("\n" + "=" * 80)
    print("Q: What have you been thinking about?")
    print("=" * 80)
    print()
    print(narrative.to_natural_language())
    
    # Extended metacognitive
    print("\n" + "=" * 80)
    print("Q: Who are you right now?")
    print("=" * 80)
    print()
    
    narrative_meta = NarrativeMetacognitive(ws)
    print(narrative_meta.who_am_i_right_now())
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    demo_self_narrative()
