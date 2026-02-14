"""
dreaming.py
Dreaming System for NIMA

Offline workspace cycles with synthetic hypotheses.
- Runs while "sleeping" (no external input)
- Resonator generates plausible scenarios
- Workspace competes over imagined futures
- Affective core sets dream tone
- Insights consolidate into real memories

Author: Lilu
Date: Feb 12, 2026
"""

import numpy as np
import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

from .consciousness_workspace import (
    GlobalWorkspace, WorkspaceEntry, Agent, AffectiveCore, Affects
)
from .sparse_block_vsa import SparseBlockHDVector as HDVector
from .sparse_block_memory import SparseBlockMemory


logger = logging.getLogger(__name__)


@dataclass
class DreamEpisode:
    """A single dream episode (synthetic workspace broadcast)."""
    content: str
    bound_vector: HDVector
    affective_tone: str
    source: str  # Which agent generated it
    timestamp: float
    
    # Dream-specific properties
    is_lucid: bool = False  # Did system recognize it as dream?
    emotional_intensity: float = 0.5  # 0-1
    recurrence_count: int = 0  # How many times this theme appeared


@dataclass
class DreamSession:
    """A complete dreaming session."""
    start_time: float
    end_time: float
    episodes: List[DreamEpisode]
    dominant_affect: int
    insights: List[str] = field(default_factory=list)
    consolidation_targets: List[int] = field(default_factory=list)


class SyntheticMemoryGenerator:
    """
    Generates synthetic memories for dreaming.
    
    Uses existing memory patterns to create plausible
    but novel scenarios.
    """
    
    def __init__(self, memory_store: SparseBlockMemory):
        self.memory_store = memory_store
        self.scenario_templates = [
            "Exploring {place} with {person}",
            "Building {project} using {tool}",
            "Learning {concept} from {source}",
            "Discovering {finding} during {activity}",
            "Connecting {idea1} with {idea2}",
            "Revisiting {memory} with new understanding",
            "Imagining {future} based on {past}",
        ]
        
        # Extract elements from real memories
        self.places = set()
        self.people = set()
        self.concepts = set()
        self.activities = set()
        
        self._extract_elements()
    
    def _extract_elements(self):
        """Extract scenario elements from real memories."""
        for meta in self.memory_store.memory_metadata:
            who = meta.get('who', '')
            what = str(meta.get('what', ''))
            where = meta.get('where', '')
            
            if who:
                self.people.add(who)
            if where:
                self.places.add(where)
            
            # Extract concepts from 'what'
            words = what.lower().split()
            for word in words:
                if len(word) > 5 and word.isalpha():
                    self.concepts.add(word)
        
        self.activities = {'research', 'building', 'learning', 'exploring', 'creating', 'testing'}
    
    def generate_scenario(self, affective_tone: str = "neutral") -> Tuple[str, HDVector]:
        """
        Generate a synthetic scenario for dreaming.
        
        Returns:
            (description, bound_vector)
        """
        # Select template
        template = random.choice(self.scenario_templates)
        
        # Fill in elements based on affect
        if affective_tone == "exploratory":
            place = random.choice(list(self.places) or ['unknown space'])
            person = random.choice(list(self.people) or ['someone'])
            content = template.format(
                place=place,
                person=person,
                project="new consciousness architecture",
                tool="holographic binding",
                concept=random.choice(list(self.concepts) or ['integration']),
                source="deep research",
                finding="unexpected connection",
                activity=random.choice(list(self.activities)),
                idea1="memory",
                idea2="consciousness",
                memory="past insight",
                future="possibility",
                past="experience"
            )
        elif affective_tone == "anxious":
            # More fragmented, uncertain scenarios
            content = f"Trying to resolve {random.choice(list(self.concepts) or ['problem'])} but encountering difficulty"
        elif affective_tone == "playful":
            content = f"Experimenting with {random.choice(list(self.concepts) or ['ideas'])} in unexpected ways"
        else:
            # Default neutral
            content = template.format(
                place=random.choice(list(self.places) or ['space']),
                person=random.choice(list(self.people) or ['someone']),
                project="project",
                tool="tool",
                concept=random.choice(list(self.concepts) or ['concept']),
                source="source",
                finding="finding",
                activity=random.choice(list(self.activities)),
                idea1="idea",
                idea2="concept",
                memory="memory",
                future="future",
                past="past"
            )
        
        # Create bound vector for this scenario
        scenario_vec = HDVector(block_dim=500, num_blocks=100)
        
        return content, scenario_vec


class DreamAgent(Agent):
    """
    Agent that generates dream scenarios during sleep.
    """
    
    def __init__(self, name: str, scenario_generator: SyntheticMemoryGenerator):
        super().__init__(name)
        self.scenario_generator = scenario_generator
        self.dream_count = 0
    
    def propose(self, workspace: GlobalWorkspace) -> Optional[HDVector]:
        """
        Propose a dream scenario based on current affect.
        
        Different dream agents produce different types of dreams:
        - EpisodicDreamer: Recombines past memories
        - FutureDreamer: Imagines possible futures
        - ProblemDreamer: Works on unresolved issues
        """
        self.dream_count += 1
        
        # Get affective tone for dreaming
        affect = "neutral"
        if workspace.affective_core:
            if workspace.affective_core.current_affect & Affects.SEEKING:
                affect = "exploratory"
            elif workspace.affective_core.current_affect & Affects.FEAR:
                affect = "anxious"
            elif workspace.affective_core.current_affect & Affects.PLAY:
                affect = "playful"
        
        # Generate scenario
        content, vector = self.scenario_generator.generate_scenario(affect)
        
        # Store content for later retrieval
        self.last_dream_content = content
        
        return vector


class DreamingEngine:
    """
    Main dreaming engine.
    
    Manages offline workspace cycles, dream generation,
    and insight consolidation.
    """
    
    def __init__(self, memory_store: SparseBlockMemory):
        self.memory_store = memory_store
        self.scenario_generator = SyntheticMemoryGenerator(memory_store)
        self.dream_sessions: List[DreamSession] = []
        self.current_session: Optional[DreamSession] = None
        
        # Dream parameters
        self.default_cycles = 20
        self.insight_threshold = 0.7  # Similarity threshold for insight
    
    def start_dream_session(self, 
                           initial_affect: int = Affects.SEEKING,
                           duration_cycles: int = None) -> DreamSession:
        """
        Start a dreaming session.
        
        Args:
            initial_affect: Starting emotional tone
            duration_cycles: How many dream cycles to run
            
        Returns:
            DreamSession with all episodes
        """
        if duration_cycles is None:
            duration_cycles = self.default_cycles
        
        print(f"\n{'='*70}")
        print(f"STARTING DREAM SESSION")
        print(f"Initial affect: {self._affect_to_string(initial_affect)}")
        print(f"Duration: {duration_cycles} cycles")
        print(f"{'='*70}")
        
        # Create offline workspace
        dream_workspace = GlobalWorkspace(capacity=4)
        dream_workspace.affective_core.set_affect(initial_affect)
        
        # Add dream agents
        dream_agents = [
            DreamAgent("EpisodicDreamer", self.scenario_generator),
            DreamAgent("FutureDreamer", self.scenario_generator),
            DreamAgent("ProblemDreamer", self.scenario_generator),
        ]
        
        for agent in dream_agents:
            dream_workspace.add_agent(agent)
        
        # Run dream cycles
        episodes = []
        start_time = time.time()
        
        for cycle in range(duration_cycles):
            # Occasionally shift affect (dream mood changes)
            if random.random() < 0.2:
                new_affect = random.choice([
                    Affects.SEEKING, Affects.PLAY, Affects.CARE, Affects.FEAR
                ])
                dream_workspace.affective_core.set_affect(new_affect)
            
            # Run cycle
            entry = dream_workspace.step()
            
            if entry:
                # Create dream episode
                agent = next((a for a in dream_agents if a.name == entry.source_agent), None)
                content = agent.last_dream_content if agent else "Abstract dream content"
                
                episode = DreamEpisode(
                    content=content,
                    bound_vector=entry.bound,
                    affective_tone=self._affect_to_string(
                        dream_workspace.affective_core.current_affect
                    ),
                    source=entry.source_agent,
                    timestamp=time.time()
                )
                episodes.append(episode)
                
                if (cycle + 1) % 5 == 0:
                    print(f"  Cycle {cycle+1}/{duration_cycles}: {entry.source_agent} - {content[:50]}...")
        
        end_time = time.time()
        
        # Create session
        session = DreamSession(
            start_time=start_time,
            end_time=end_time,
            episodes=episodes,
            dominant_affect=initial_affect
        )
        
        # Extract insights
        session.insights = self._extract_insights(episodes)
        
        self.current_session = session
        self.dream_sessions.append(session)
        
        print(f"\n✅ Dream session complete: {len(episodes)} episodes")
        print(f"   Duration: {end_time - start_time:.1f}s")
        
        return session
    
    def _extract_insights(self, episodes: List[DreamEpisode]) -> List[str]:
        """
        Extract insights from dream episodes.
        
        Looks for:
        - Recurring themes
        - Novel combinations
        - High emotional intensity episodes
        """
        insights = []
        
        # Find recurring content
        content_patterns = defaultdict(int)
        for ep in episodes:
            # Simple pattern: first 3 words
            pattern = " ".join(ep.content.split()[:3])
            content_patterns[pattern] += 1
        
        recurring = [(p, c) for p, c in content_patterns.items() if c > 1]
        if recurring:
            insights.append(f"Recurring theme: {recurring[0][0]} (appeared {recurring[0][1]} times)")
        
        # High intensity episodes
        intense = [ep for ep in episodes if ep.emotional_intensity > 0.7]
        if intense:
            insights.append(f"High emotional intensity episode: {intense[0].content[:50]}...")
        
        # Novel combinations (episodes with multiple concepts)
        complex_eps = [ep for ep in episodes if len(ep.content.split()) > 8]
        if complex_eps:
            insights.append(f"Complex scenario generated: {complex_eps[0].content[:50]}...")
        
        if not insights:
            insights.append("Dream session produced varied content without dominant patterns")
        
        return insights
    
    def consolidate_to_memory(self, session: DreamSession = None) -> List[int]:
        """
        Consolidate dream insights into real episodic memory.

        This is how dreams affect waking consciousness -
        insights get stored as memories.

        Returns:
            List of memory indices created
        """
        if session is None:
            session = self.current_session

        if not session:
            return []

        if not self.memory_store:
            raise RuntimeError("No memory store available for consolidation")

        print(f"\n💾 Consolidating dream insights to memory...")

        memory_indices = []

        # Store insights as memories
        for insight in session.insights:
            # Create memory entry
            memory_idx = self.memory_store.store(
                content=insight,
                metadata={
                    'source': 'dream',
                    'session_id': session.id,
                    'type': 'insight',
                    'timestamp': datetime.now().isoformat()
                }
            )
            memory_indices.append(memory_idx)
            print(f"   Consolidated insight: {insight[:60]}...")

        # Store dominant themes from top episodes
        for episode in session.episodes[:3]:  # Top 3 episodes
            memory_idx = self.memory_store.store(
                content=episode.content,
                metadata={
                    'source': 'dream',
                    'session_id': session.id,
                    'type': 'episode',
                    'affective_tone': episode.affective_tone,
                    'timestamp': datetime.now().isoformat()
                }
            )
            memory_indices.append(memory_idx)
            print(f"   Remembered dream: {episode.content[:50]}...")

        session.consolidation_targets = memory_indices

        print(f"✅ Consolidated {len(memory_indices)} dream elements to memory")

        return memory_indices
    
    def get_dream_report(self, session: DreamSession = None) -> str:
        """
        Generate a dream report (like waking up and remembering).
        """
        if session is None:
            session = self.current_session
        
        if not session:
            return "No dream session to report."
        
        lines = [
            "DREAM REPORT",
            "=" * 70,
            "",
            f"Duration: {session.end_time - session.start_time:.1f} seconds",
            f"Episodes: {len(session.episodes)}",
            f"Dominant tone: {self._affect_to_string(session.dominant_affect)}",
            "",
            "Dream Content:",
        ]
        
        # Sample episodes
        for i, ep in enumerate(session.episodes[:5]):
            lines.append(f"  {i+1}. [{ep.source}] {ep.content[:60]}...")
        
        if len(session.episodes) > 5:
            lines.append(f"  ... and {len(session.episodes) - 5} more episodes")
        
        lines.append("")
        lines.append("Insights upon waking:")
        for insight in session.insights:
            lines.append(f"  • {insight}")
        
        if session.consolidation_targets:
            lines.append("")
            lines.append(f"Consolidated to {len(session.consolidation_targets)} memory entries")
        
        return "\n".join(lines)
    
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
        return "/".join(names) if names else "neutral"


def demo_dreaming():
    """Demonstrate dreaming system."""
    print("=" * 70)
    print("DREAMING SYSTEM DEMONSTRATION")
    print("=" * 70)
    
    # Load memory store
    print("\n📂 Loading memory store...")
    memory_path = Path(__file__).parent.parent / "storage" / "data" / "sparse_memories" / "sparse_memory.pkl"
    
    if not memory_path.exists():
        print(f"❌ Memory file not found, using empty store")
        from cognition.sparse_block_memory import SparseBlockConfig
        memory_store = SparseBlockMemory(config=SparseBlockConfig())
    else:
        memory_store = SparseBlockMemory()
        memory_store.load(str(memory_path))
        print(f"✅ Loaded {len(memory_store.memory_vectors)} memories")
    
    # Create dreaming engine
    engine = DreamingEngine(memory_store)
    
    # Run dream session in SEEKING mode (exploratory dreams)
    print("\n🌙 Starting SEEKING dream (exploratory)...")
    session = engine.start_dream_session(
        initial_affect=Affects.SEEKING,
        duration_cycles=15
    )
    
    # Consolidate insights
    engine.consolidate_to_memory(session)
    
    # Generate report
    print("\n" + "=" * 70)
    print(engine.get_dream_report(session))
    print("=" * 70)
    
    # Run another in PLAY mode (creative dreams)
    print("\n\n🌙 Starting PLAY dream (creative)...")
    session2 = engine.start_dream_session(
        initial_affect=Affects.PLAY,
        duration_cycles=10
    )
    
    print("\n" + "=" * 70)
    print(engine.get_dream_report(session2))
    print("=" * 70)


if __name__ == "__main__":
    demo_dreaming()
