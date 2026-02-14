#!/usr/bin/env python3
"""
Resonator Network for NIMA v2 — Frontier 6
==========================================

Factorized retrieval from partial cues via iterative VSA decomposition.

"Something about CAD recently... who was it?"
→ Resonator iterates → Alice asked about CAD on Tuesday

The mechanism:
1. Maintain one "estimate" vector per role slot (who, what, where, when)
2. Each estimate starts as random noise
3. On each iteration:
   - For each slot, unbind all other current estimates from the memory
   - The residual approximates the true filler for that slot
   - Clean up by finding the nearest known concept vector
   - Update the estimate
4. Repeat until convergence (typically 5-15 iterations)

This is factorized retrieval — recovering the WHO, WHAT, WHERE, WHEN 
from a partially-cued memory without knowing them in advance.

Author: NIMA Project
Date: 2026
Frontier: 6
"""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Codebook:
    """
    A collection of known concept vectors for a role slot.
    
    E.g., the WHO codebook contains vectors for Alice, Bob, Agent, etc.
    """
    name: str  # "who", "what", "topic", "when"
    vectors: Dict[str, torch.Tensor] = field(default_factory=dict)
    
    def add(self, label: str, vector: torch.Tensor):
        """Add a concept to the codebook."""
        self.vectors[label] = vector
    
    def nearest(self, query: torch.Tensor, top_k: int = 1) -> List[Tuple[str, float]]:
        """Find nearest concepts to query vector."""
        if not self.vectors:
            return []
        
        results = []
        for label, vec in self.vectors.items():
            sim = self._cosine_sim(query, vec)
            results.append((label, float(sim)))
        
        results.sort(key=lambda x: -x[1])
        return results[:top_k]
    
    def get(self, label: str) -> Optional[torch.Tensor]:
        """Get vector by label."""
        return self.vectors.get(label)
    
    def random(self) -> Tuple[str, torch.Tensor]:
        """Get a random concept from the codebook."""
        if not self.vectors:
            raise ValueError(f"Codebook '{self.name}' is empty")
        label = np.random.choice(list(self.vectors.keys()))
        return label, self.vectors[label]
    
    def __len__(self):
        return len(self.vectors)
    
    @staticmethod
    def _cosine_sim(a: torch.Tensor, b: torch.Tensor) -> float:
        """Compute cosine similarity."""
        norm_a = torch.norm(a)
        norm_b = torch.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float((a @ b) / (norm_a * norm_b))


@dataclass
class ResonatorResult:
    """Result of resonator decomposition."""
    converged: bool
    iterations: int
    slots: Dict[str, str]  # role -> recovered label
    confidences: Dict[str, float]  # role -> confidence score
    trajectory: List[Dict[str, str]]  # iteration history


class ResonatorNetwork:
    """
    Iterative factorization network for VSA decomposition.
    
    Given a bound memory vector and partial knowledge of its slots,
    recovers the unknown slot fillers through iterative unbinding
    and cleanup against codebooks.
    """
    
    def __init__(
        self,
        dimension: int = 50000,
        max_iterations: int = 20,
        convergence_threshold: float = 0.001,
        cleanup_candidates: int = 3,
    ):
        """
        Initialize resonator network.
        
        Args:
            dimension: VSA vector dimension
            max_iterations: Maximum iterations before stopping
            convergence_threshold: Stop when estimates change less than this
            cleanup_candidates: Number of candidates to consider during cleanup
        """
        self.dimension = dimension
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.cleanup_candidates = cleanup_candidates
        
        # Role keys (fixed random vectors for binding)
        self.role_keys: Dict[str, torch.Tensor] = {}
        
        # Codebooks for each role
        self.codebooks: Dict[str, Codebook] = {}
        
        # Stats
        self.stats = {
            'decompositions': 0,
            'avg_iterations': 0.0,
            'convergence_rate': 0.0,
        }
    
    def initialize_role_keys(self, roles: List[str], seed: int = 42):
        """
        Initialize fixed random vectors for each role.
        
        Args:
            roles: List of role names (e.g., ["who", "what", "topic", "when"])
            seed: Random seed for reproducibility
        """
        torch.manual_seed(seed)
        for role in roles:
            # Generate sparse random vector
            vec = torch.zeros(self.dimension)
            k = int(self.dimension * 0.01)  # 1% sparsity
            indices = torch.randperm(self.dimension)[:k]
            vec[indices] = torch.randn(k)
            vec = vec / torch.norm(vec)  # Normalize
            self.role_keys[role] = vec
    
    def add_codebook(self, name: str, codebook: Codebook):
        """Add a codebook for a role."""
        self.codebooks[name] = codebook
    
    def bind(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        """Circular convolution binding."""
        # FFT-based circular convolution
        fa = torch.fft.fft(a.to(torch.complex64))
        fb = torch.fft.fft(b.to(torch.complex64))
        result = torch.fft.ifft(fa * fb).real
        return result
    
    def unbind(self, bound: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
        """
        Unbind (approximate inverse of bind).
        
        For circular convolution, unbinding uses correlation (conjugate in freq domain).
        """
        fb = torch.fft.fft(bound.to(torch.complex64))
        fk = torch.fft.fft(key.to(torch.complex64))
        # Correlation = convolution with conjugate
        result = torch.fft.ifft(fb * torch.conj(fk)).real
        return result
    
    def decompose_direct(
        self,
        bound_memory: torch.Tensor,
        known_slots: Optional[Dict[str, str]] = None,
        unknown_slots: Optional[List[str]] = None,
    ) -> ResonatorResult:
        """
        Direct (non-iterative) decomposition via unbinding.
        
        For each unknown slot:
        1. Unbind just the role key from the bound memory
        2. Find nearest concept in codebook
        
        This works well when the bound memory is a clean superposition.
        For noisy memories, use iterative decompose() instead.
        """
        if known_slots is None:
            known_slots = {}
        
        if unknown_slots is None:
            unknown_slots = [r for r in self.role_keys if r not in known_slots]
        
        slots = dict(known_slots)
        confidences = {}
        
        for role in unknown_slots:
            if role not in self.role_keys or role not in self.codebooks:
                continue
            
            # Unbind just the role key
            role_key = self.role_keys[role]
            residual = self.unbind(bound_memory, role_key)
            
            # Find nearest in codebook
            candidates = self.codebooks[role].nearest(residual, 2)
            if candidates:
                slots[role] = candidates[0][0]
                # Confidence = gap between top-1 and top-2
                if len(candidates) >= 2:
                    confidences[role] = candidates[0][1] - candidates[1][1]
                else:
                    confidences[role] = candidates[0][1]
        
        return ResonatorResult(
            converged=True,
            iterations=1,
            slots=slots,
            confidences=confidences,
            trajectory=[slots],
        )
    
    def decompose(
        self,
        bound_memory: torch.Tensor,
        known_slots: Optional[Dict[str, str]] = None,
        unknown_slots: Optional[List[str]] = None,
    ) -> ResonatorResult:
        """
        Decompose a bound memory into its constituent factors.
        
        Args:
            bound_memory: The compositional VSA vector to decompose
            known_slots: Dict of known slot values (e.g., {"what": "asked"})
            unknown_slots: List of slots to recover (e.g., ["who", "topic"])
            
        Returns:
            ResonatorResult with recovered slot values and confidences
        """
        if known_slots is None:
            known_slots = {}
        
        if unknown_slots is None:
            unknown_slots = [r for r in self.role_keys if r not in known_slots]
        
        # Initialize estimates
        estimates: Dict[str, Tuple[str, torch.Tensor]] = {}
        
        # For known slots, use the known value
        for role, label in known_slots.items():
            if role in self.codebooks:
                vec = self.codebooks[role].get(label)
                if vec is not None:
                    estimates[role] = (label, vec)
        
        # For unknown slots, initialize randomly
        for role in unknown_slots:
            if role in self.codebooks and len(self.codebooks[role]) > 0:
                label, vec = self.codebooks[role].random()
                estimates[role] = (label, vec)
        
        # Iteration history
        trajectory = []
        prev_labels = {}
        
        # Iterate
        converged = False
        for iteration in range(self.max_iterations):
            current_labels = {r: e[0] for r, e in estimates.items()}
            trajectory.append(current_labels.copy())
            
            # Check convergence
            if iteration > 0 and current_labels == prev_labels:
                converged = True
                break
            
            prev_labels = current_labels.copy()
            
            # Update each unknown slot
            for role in unknown_slots:
                if role not in self.codebooks:
                    continue
                
                # Unbind all OTHER estimates from the memory
                residual = bound_memory.clone()
                
                for other_role, (_, other_vec) in estimates.items():
                    if other_role != role and other_role in self.role_keys:
                        # Unbind the role key
                        residual = self.unbind(residual, self.role_keys[other_role])
                        # Unbind the filler
                        residual = self.unbind(residual, other_vec)
                
                # Unbind this role's key to get the filler estimate
                if role in self.role_keys:
                    residual = self.unbind(residual, self.role_keys[role])
                
                # Clean up: find nearest in codebook
                candidates = self.codebooks[role].nearest(residual, self.cleanup_candidates)
                if candidates:
                    best_label, best_score = candidates[0]
                    best_vec = self.codebooks[role].get(best_label)
                    if best_vec is not None:
                        estimates[role] = (best_label, best_vec)
        
        # Compute final confidences
        confidences = {}
        for role, (label, vec) in estimates.items():
            if role in self.codebooks:
                # Confidence = similarity to best match
                matches = self.codebooks[role].nearest(vec, 2)
                if len(matches) >= 2:
                    # Confidence = gap between top-1 and top-2
                    confidences[role] = matches[0][1] - matches[1][1]
                elif len(matches) == 1:
                    confidences[role] = matches[0][1]
                else:
                    confidences[role] = 0.0
        
        # Update stats
        self.stats['decompositions'] += 1
        n = self.stats['decompositions']
        self.stats['avg_iterations'] = (
            (self.stats['avg_iterations'] * (n - 1) + (iteration + 1)) / n
        )
        if converged:
            self.stats['convergence_rate'] = (
                (self.stats['convergence_rate'] * (n - 1) + 1) / n
            )
        else:
            self.stats['convergence_rate'] = (
                (self.stats['convergence_rate'] * (n - 1)) / n
            )
        
        return ResonatorResult(
            converged=converged,
            iterations=iteration + 1,
            slots={r: e[0] for r, e in estimates.items()},
            confidences=confidences,
            trajectory=trajectory,
        )
    
    def query_partial(
        self,
        known: Dict[str, str],
        recover: List[str],
        memories: List[Tuple[int, torch.Tensor, Dict]],
    ) -> List[Tuple[int, Dict, ResonatorResult]]:
        """
        Query memories with partial cues and recover unknown slots.
        
        Args:
            known: Known slot values (e.g., {"topic": "CAD"})
            recover: Slots to recover (e.g., ["who", "when"])
            memories: List of (id, vector, metadata) tuples
            
        Returns:
            List of (memory_id, metadata, resonator_result) for matches
        """
        results = []
        
        for mem_id, mem_vec, metadata in memories:
            # Try to decompose this memory
            result = self.decompose(
                bound_memory=mem_vec,
                known_slots=known,
                unknown_slots=recover,
            )
            
            # Check if known slots match the memory's metadata
            matches = True
            for role, expected in known.items():
                actual = metadata.get(role, "").lower()
                if expected.lower() not in actual:
                    matches = False
                    break
            
            if matches and result.converged:
                results.append((mem_id, metadata, result))
        
        return results
    
    def get_stats(self) -> Dict:
        """Get resonator statistics."""
        return self.stats.copy()


class SchemaSlotPredictor:
    """
    Predict unknown slots from activated schemas.
    
    When a schema is activated (e.g., "Alice asks about technical topics"),
    use the resonator to predict likely slot fillers based on the schema
    template.
    
    "Alice is here → she'll probably ask about CAD or VSA"
    """
    
    def __init__(self, resonator: ResonatorNetwork):
        self.resonator = resonator
        self.schema_templates: Dict[str, Dict[str, List[str]]] = {}
    
    def register_schema(self, schema_name: str, slot_patterns: Dict[str, List[str]]):
        """
        Register a schema with its typical slot patterns.
        
        Args:
            schema_name: E.g., "alice_technical"
            slot_patterns: E.g., {"who": ["Alice"], "topic": ["nima", "vsa", "cad"]}
        """
        self.schema_templates[schema_name] = slot_patterns
    
    def predict_slots(
        self,
        activated_schema: str,
        known_slots: Dict[str, str],
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Predict unknown slots based on activated schema.
        
        Args:
            activated_schema: Which schema is active
            known_slots: Already known slot values
            
        Returns:
            Dict of slot -> list of (value, probability) predictions
        """
        if activated_schema not in self.schema_templates:
            return {}
        
        template = self.schema_templates[activated_schema]
        predictions = {}
        
        for slot, typical_values in template.items():
            if slot in known_slots:
                continue  # Already known
            
            # Weight by frequency in schema
            total = len(typical_values)
            value_counts = {}
            for v in typical_values:
                value_counts[v] = value_counts.get(v, 0) + 1
            
            predictions[slot] = [
                (v, count / total) 
                for v, count in sorted(value_counts.items(), key=lambda x: -x[1])
            ]
        
        return predictions
    
    def build_from_memories(
        self,
        memories: List[Dict],
        min_pattern_count: int = 3,
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        Automatically build schema templates from memory patterns.
        
        Finds co-occurrence patterns like:
        - Alice + technical topics
        - Bob + business topics
        """
        # Group memories by WHO
        by_person: Dict[str, List[Dict]] = {}
        for mem in memories:
            who = mem.get("who", "")
            if who:
                if who not in by_person:
                    by_person[who] = []
                by_person[who].append(mem)
        
        # Build templates for each person
        templates = {}
        for person, person_mems in by_person.items():
            if len(person_mems) < min_pattern_count:
                continue
            
            # Extract common topics
            topics = []
            actions = []
            
            for mem in person_mems:
                raw = mem.get("raw_text", "").lower()
                what = mem.get("what", "").lower()
                
                # Check for known topics
                for topic in ["nima", "vsa", "cad", "infrastructure", "heartbeat",
                             "memory", "schema", "binding", "affect", "design"]:
                    if topic in raw or topic in what:
                        topics.append(topic)
                
                # Check for actions
                for action in ["asked", "said", "built", "created", "fixed"]:
                    if action in what:
                        actions.append(action)
            
            if topics:
                schema_name = f"person_{person.lower().replace(' ', '_')}"
                templates[schema_name] = {
                    "who": [person],
                    "topic": topics[:20],  # Top 20
                    "what": actions[:10] if actions else ["said"],
                }
        
        self.schema_templates = templates
        return templates


class CodebookBuilder:
    """
    Builds codebooks from memory corpus.
    
    Extracts unique fillers for each role and creates embeddings.
    """
    
    def __init__(self, embedder=None):
        """
        Initialize builder.
        
        Args:
            embedder: Embedding function (text -> vector)
        """
        self.embedder = embedder
    
    def build_from_memories(
        self,
        memories: List[Dict],
        roles: List[str] = ["who", "what", "topic"],
    ) -> Dict[str, Codebook]:
        """
        Build codebooks from memory corpus.
        
        Args:
            memories: List of memory metadata dicts
            roles: Roles to extract codebooks for
            
        Returns:
            Dict of role -> Codebook
        """
        # Collect unique values for each role
        role_values: Dict[str, Set[str]] = {role: set() for role in roles}
        
        for mem in memories:
            for role in roles:
                value = mem.get(role, "")
                if value and isinstance(value, str):
                    # Normalize
                    value = value.strip()
                    if len(value) > 0:
                        role_values[role].add(value)
                
                # Also check raw_text for topics
                if role == "topic":
                    raw = mem.get("raw_text", "")
                    # Extract simple topics (words > 4 chars, not stopwords)
                    if raw:
                        words = raw.split()
                        for w in words[:20]:  # First 20 words
                            w = w.strip(".,!?()[]{}\"'").lower()
                            if len(w) > 4 and w not in STOPWORDS:
                                role_values[role].add(w)
        
        # Build codebooks
        codebooks = {}
        for role in roles:
            cb = Codebook(name=role)
            values = list(role_values[role])
            
            print(f"   {role}: {len(values)} unique values")
            
            for value in values:
                if self.embedder:
                    vec = self.embedder(value)
                    if vec is not None:
                        cb.add(value, vec)
                else:
                    # Fallback: random vector
                    vec = torch.randn(50000)
                    vec = vec / torch.norm(vec)
                    cb.add(value, vec)
            
            codebooks[role] = cb
        
        return codebooks
    
    def save_codebooks(self, codebooks: Dict[str, Codebook], path: Path):
        """Save codebooks to disk (atomic writes)."""
        from ..utils import atomic_torch_save, atomic_json_save
        path.mkdir(parents=True, exist_ok=True)
        
        for name, cb in codebooks.items():
            # Save vectors
            vectors = {label: vec.numpy() for label, vec in cb.vectors.items()}
            atomic_torch_save(vectors, path / f"codebook_{name}.pt")
        
        # Save metadata
        meta = {
            name: list(cb.vectors.keys())
            for name, cb in codebooks.items()
        }
        atomic_json_save(meta, path / "codebook_meta.json")
    
    def load_codebooks(self, path: Path) -> Dict[str, Codebook]:
        """Load codebooks from disk."""
        codebooks = {}
        
        meta_path = path / "codebook_meta.json"
        if not meta_path.exists():
            return codebooks
        
        with open(meta_path) as f:
            meta = json.load(f)
        
        for name, labels in meta.items():
            cb = Codebook(name=name)
            
            vec_path = path / f"codebook_{name}.pt"
            if vec_path.exists():
                vectors = torch.load(vec_path, weights_only=True)
                for label in labels:
                    if label in vectors:
                        vec = vectors[label]
                        if isinstance(vec, np.ndarray):
                            vec = torch.from_numpy(vec)
                        cb.add(label, vec)
            
            codebooks[name] = cb
        
        return codebooks


# Common stopwords to filter from topic extraction
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
    "from", "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "also", "now", "that",
    "this", "these", "those", "what", "which", "who", "whom", "whose",
    "and", "but", "if", "or", "because", "until", "while", "although",
    "about", "your", "you", "would", "like", "it's", "i'm", "we're",
}


# =============================================================================
# Demo / Testing
# =============================================================================

def test_binding_mechanics():
    """Test that binding/unbinding mechanics work correctly."""
    print("=" * 70)
    print("RESONATOR NETWORK — Frontier 6")
    print("=" * 70)
    
    print("\n🔬 Testing binding/unbinding mechanics...")
    
    DIM = 50000
    
    # Create resonator
    resonator = ResonatorNetwork(dimension=DIM, max_iterations=20)
    resonator.initialize_role_keys(["who", "what", "topic"])
    
    # Create orthogonal-ish vectors for concepts
    torch.manual_seed(42)
    
    def sparse_vec(seed):
        torch.manual_seed(seed)
        v = torch.zeros(DIM)
        k = int(DIM * 0.01)
        indices = torch.randperm(DIM)[:k]
        v[indices] = torch.randn(k)
        return v / torch.norm(v)
    
    # Different seeds = different (quasi-orthogonal) vectors
    alice_vec = sparse_vec(100)
    bob_vec = sparse_vec(200)
    agent_vec = sparse_vec(300)
    asked_vec = sparse_vec(400)
    said_vec = sparse_vec(500)
    cad_vec = sparse_vec(600)
    nima_vec = sparse_vec(700)
    
    who_key = resonator.role_keys["who"]
    what_key = resonator.role_keys["what"]
    topic_key = resonator.role_keys["topic"]
    
    # Create bound memory: Alice asked about CAD
    print("\n🔗 Creating: who=Alice, what=asked, topic=CAD")
    bound = (
        resonator.bind(who_key, alice_vec) +
        resonator.bind(what_key, asked_vec) +
        resonator.bind(topic_key, cad_vec)
    )
    
    # Test direct unbinding (no cleanup, just similarity check)
    print("\n📊 Direct unbinding test (no codebook cleanup):")
    
    # Unbind who_key to recover Alice
    recovered_who = resonator.unbind(bound, who_key)
    sim_alice = float(torch.dot(recovered_who, alice_vec) / (torch.norm(recovered_who) * torch.norm(alice_vec)))
    sim_bob = float(torch.dot(recovered_who, bob_vec) / (torch.norm(recovered_who) * torch.norm(bob_vec)))
    sim_agent = float(torch.dot(recovered_who, agent_vec) / (torch.norm(recovered_who) * torch.norm(agent_vec)))
    
    print(f"   Unbind WHO → Alice sim: {sim_alice:.4f}")
    print(f"   Unbind WHO → Bob sim: {sim_bob:.4f}")
    print(f"   Unbind WHO → Agent sim: {sim_agent:.4f}")
    
    # Alice should be highest
    who_correct = sim_alice > sim_bob and sim_alice > sim_agent
    print(f"   ✅ WHO recovery correct: {who_correct}")
    
    # Unbind what_key to recover asked
    recovered_what = resonator.unbind(bound, what_key)
    sim_asked = float(torch.dot(recovered_what, asked_vec) / (torch.norm(recovered_what) * torch.norm(asked_vec)))
    sim_said = float(torch.dot(recovered_what, said_vec) / (torch.norm(recovered_what) * torch.norm(said_vec)))
    
    print(f"   Unbind WHAT → asked sim: {sim_asked:.4f}")
    print(f"   Unbind WHAT → said sim: {sim_said:.4f}")
    
    what_correct = sim_asked > sim_said
    print(f"   ✅ WHAT recovery correct: {what_correct}")
    
    # Unbind topic_key to recover CAD
    recovered_topic = resonator.unbind(bound, topic_key)
    sim_cad = float(torch.dot(recovered_topic, cad_vec) / (torch.norm(recovered_topic) * torch.norm(cad_vec)))
    sim_nima = float(torch.dot(recovered_topic, nima_vec) / (torch.norm(recovered_topic) * torch.norm(nima_vec)))
    
    print(f"   Unbind TOPIC → CAD sim: {sim_cad:.4f}")
    print(f"   Unbind TOPIC → NIMA sim: {sim_nima:.4f}")
    
    topic_correct = sim_cad > sim_nima
    print(f"   ✅ TOPIC recovery correct: {topic_correct}")
    
    all_correct = who_correct and what_correct and topic_correct
    print(f"\n🎯 All binding/unbinding tests passed: {all_correct}")
    
    # Now test full resonator with codebooks
    print("\n" + "-" * 40)
    print("Testing full resonator decomposition...")
    
    who_cb = Codebook("who")
    who_cb.add("Alice", alice_vec)
    who_cb.add("Bob", bob_vec)
    who_cb.add("Agent", agent_vec)
    
    what_cb = Codebook("what")
    what_cb.add("asked", asked_vec)
    what_cb.add("said", said_vec)
    
    topic_cb = Codebook("topic")
    topic_cb.add("CAD", cad_vec)
    topic_cb.add("NIMA", nima_vec)
    
    resonator.add_codebook("who", who_cb)
    resonator.add_codebook("what", what_cb)
    resonator.add_codebook("topic", topic_cb)
    
    print(f"   who: {len(who_cb)} concepts")
    print(f"   what: {len(what_cb)} concepts")
    print(f"   topic: {len(topic_cb)} concepts")
    
    # Test DIRECT decomposition (non-iterative)
    print("\n🔬 Direct decomposition: topic='CAD', who=?, what=?")
    result = resonator.decompose_direct(
        bound_memory=bound,
        known_slots={"topic": "CAD"},
        unknown_slots=["who", "what"],
    )
    
    print(f"\n📊 Results:")
    print(f"   Converged: {result.converged}")
    print(f"   Iterations: {result.iterations}")
    print(f"   Recovered slots: {result.slots}")
    
    # Check if correct
    expected = {"who": "Alice", "what": "asked", "topic": "CAD"}
    correct = all(result.slots.get(k) == v for k, v in expected.items() if k in result.slots)
    print(f"\n   ✅ Full decomposition correct: {correct}")
    
    print(f"\n📈 Resonator Stats:")
    for k, v in resonator.get_stats().items():
        print(f"   {k}: {v}")
    
    print("\n" + "=" * 70)
    print(f"Resonator Network: {'PASSED' if all_correct and correct else 'NEEDS TUNING'}")
    print("=" * 70)
    
    return all_correct and correct


if __name__ == "__main__":
    test_binding_mechanics()