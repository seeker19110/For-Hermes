#!/usr/bin/env python3
"""
Subcortical Affective Core — NIMA Layer 1
==========================================
Foundation layer implementing Panksepp's 7 core affects.

"Affect precedes cognition" — memory without emotion cannot determine what matters.

Based on research:
- Panksepp's Affective Neuroscience (1998)
- Damasio's Somatic Marker Hypothesis

Author: NIMA Project
Date: 2026
"""

import threading
import re
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)


class CoreAffect(Enum):
    """Panksepp's 7 primary-process emotional systems."""
    SEEKING = "seeking"     # Curiosity, anticipation, enthusiasm
    RAGE = "rage"           # Frustration, anger, irritation
    FEAR = "fear"           # Anxiety, dread, apprehension
    LUST = "lust"           # Desire, attraction, passion
    CARE = "care"           # Nurturing, tenderness, love
    PANIC = "panic"         # Separation distress, loneliness, grief
    PLAY = "play"           # Joy, excitement, social bonding


@dataclass
class AffectState:
    """Current affective state with circumplex mapping."""
    # Panksepp's 7 affects (0-1 activation)
    affects: Dict[str, float]
    
    # Russell's circumplex (derived)
    valence: float          # -1 (negative) to +1 (positive)
    arousal: float          # 0 (calm) to 1 (activated)
    
    # Extended dimensions
    urgency: float = 0.5    # How time-critical
    dominance: float = 0.0  # -1 (submissive) to +1 (dominant)
    
    # Attention modulation
    attention_weight: float = 1.0
    
    # Somatic marker (gut feeling)
    somatic_marker: Optional[str] = None
    
    # Dominant affect
    dominant: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'affects': self.affects,
            'valence': self.valence,
            'arousal': self.arousal,
            'urgency': self.urgency,
            'dominance': self.dominance,
            'attention_weight': self.attention_weight,
            'somatic_marker': self.somatic_marker,
            'dominant': self.dominant,
        }


class SubcorticalAffectiveCore:
    """
    Layer 1: Affective processing before cognition.
    
    Implements:
    - Panksepp's 7 core affects with proper dynamics
    - Russell's circumplex mapping
    - Damasio's somatic markers
    - Attention modulation based on affect
    """
    
    # Affect definitions with valence/arousal contributions
    CORE_AFFECTS = {
        'SEEKING': {
            'valence': 0.6,    # Positive (anticipation)
            'arousal': 0.7,    # High (energized)
            'baseline': 0.3,   # Default activation
            'decay': 0.1,      # Per-second decay rate
            'keywords': ['curious', 'explore', 'wonder', 'discover', 'learn', 
                        'investigate', 'search', 'find', 'want', 'excited'],
        },
        'RAGE': {
            'valence': -0.8,   # Negative
            'arousal': 0.9,    # Very high
            'baseline': 0.1,
            'decay': 0.05,     # Slow decay (lingers)
            'keywords': ['angry', 'frustrated', 'furious', 'annoyed', 'irritated',
                        'mad', 'hate', 'rage', 'unfair', 'wrong'],
        },
        'FEAR': {
            'valence': -0.7,
            'arousal': 0.8,
            'baseline': 0.15,
            'decay': 0.08,
            'keywords': ['afraid', 'scared', 'anxious', 'worried', 'nervous',
                        'terrified', 'dread', 'threat', 'danger', 'risk'],
        },
        'LUST': {
            'valence': 0.7,
            'arousal': 0.8,
            'baseline': 0.1,
            'decay': 0.15,
            'keywords': ['desire', 'want', 'attraction', 'passion', 'longing',
                        'craving', 'yearning', 'need'],
        },
        'CARE': {
            'valence': 0.8,
            'arousal': 0.4,     # Calm, nurturing
            'baseline': 0.25,
            'decay': 0.02,      # Very slow decay (stable)
            'keywords': ['love', 'care', 'nurture', 'protect', 'help', 'support',
                        'gentle', 'kind', 'tender', 'family', 'children'],
        },
        'PANIC': {
            'valence': -0.9,
            'arousal': 0.85,
            'baseline': 0.1,
            'decay': 0.12,
            'keywords': ['lonely', 'alone', 'abandoned', 'lost', 'miss', 'grief',
                        'sad', 'isolated', 'separated', 'gone'],
        },
        'PLAY': {
            'valence': 0.9,     # Very positive
            'arousal': 0.75,
            'baseline': 0.2,
            'decay': 0.1,
            'keywords': ['fun', 'play', 'joy', 'laugh', 'game', 'silly', 'joke',
                        'enjoy', 'delight', 'happy', 'excited'],
        },
    }
    
    def __init__(self, dimension: int = 128, storage_path: Optional[Path] = None,
                 care_people: Optional[List[str]] = None):
        """
        Initialize affective core.
        
        Args:
            dimension: VSA dimension for affect vectors
            storage_path: Where to persist somatic markers
            care_people: List of names that trigger CARE boost (optional, default empty)
        """
        self.dimension = dimension
        
        # Use environment or default for storage path
        if storage_path is None:
            from ..config import NIMA_DATA_DIR
            storage_path = NIMA_DATA_DIR / "affect"
        
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Configurable care people list (default empty - identity agnostic)
        self.care_people = care_people or []
        
        # Threading lock for mutable state
        self._lock = threading.RLock()
        
        # Current affect activations
        self.affects = {name: info['baseline'] for name, info in self.CORE_AFFECTS.items()}
        
        # Somatic markers: situation_hash → (valence, arousal, description)
        self.somatic_markers: Dict[str, Dict] = {}
        self._load_somatic_markers()
        
        # Affect history (for trajectory analysis)
        self.history: List[Dict] = []
        self.max_history = 100
        
        # Create affect vectors for binding
        self._init_affect_vectors()
        
        # Pre-compile regex patterns for O(n) keyword matching (performance fix)
        self._keyword_patterns = {
            name: re.compile(r'\b(' + '|'.join(re.escape(kw) for kw in info['keywords']) + r')\b', re.IGNORECASE)
            for name, info in self.CORE_AFFECTS.items()
        }
    
    def _init_affect_vectors(self):
        """Create orthogonal(ish) vectors for each affect."""
        np.random.seed(42)  # Reproducible
        self.affect_vectors = {}
        for name in self.CORE_AFFECTS:
            vec = np.random.randn(self.dimension)
            vec = vec / np.linalg.norm(vec)
            self.affect_vectors[name] = vec
    
    def process(self, stimulus: np.ndarray, context: Dict[str, Any]) -> AffectState:
        """
        Process a stimulus through the affective core.
        
        This happens BEFORE semantic processing — affect colors perception.
        
        Args:
            stimulus: Raw input vector (or zeros if text-only)
            context: Dict with 'text', 'who', 'when', etc.
        
        Returns:
            AffectState with full affective annotation
        """
        with self._lock:
            text = context.get('text', '')
            
            # Step 1: Detect affects from text
            self._detect_affects_from_text(text)
            
            # Step 2: Check somatic markers (learned gut feelings)
            somatic = self._check_somatic_markers(stimulus, context)
            
            # Step 3: Apply context modulation
            self._apply_context_modulation(context)
            
            # Step 4: Compute circumplex
            valence, arousal, urgency, dominance = self._compute_circumplex()
            
            # Step 5: Compute attention weight
            attention = self._compute_attention_weight()
            
            # Step 6: Find dominant affect
            dominant = max(self.affects.items(), key=lambda x: x[1])
            dominant_name = dominant[0] if dominant[1] > 0.3 else None
            
            # Step 7: Record in history
            state = AffectState(
                affects=self.affects.copy(),
                valence=valence,
                arousal=arousal,
                urgency=urgency,
                dominance=dominance,
                attention_weight=attention,
                somatic_marker=somatic,
                dominant=dominant_name,
            )
            
            self._record_history(state)
            
            return state
    
    def _detect_affects_from_text(self, text: str):
        """Detect affect activations from text content using compiled regex (O(n))."""
        for affect_name, info in self.CORE_AFFECTS.items():
            # Use pre-compiled regex for O(n) matching instead of O(n*k)
            pattern = self._keyword_patterns[affect_name]
            matches = len(pattern.findall(text))
            
            if matches > 0:
                # Boost activation (sigmoid-like capping)
                boost = min(0.3 * matches, 0.5)
                current = self.affects[affect_name]
                self.affects[affect_name] = min(1.0, current + boost)
            else:
                # Gentle decay toward baseline
                self._decay_single_affect(affect_name, dt=0.5)
    
    def _decay_single_affect(self, affect_name: str, dt: float = 1.0):
        """Decay a single affect toward baseline."""
        info = self.CORE_AFFECTS[affect_name]
        baseline = info['baseline']
        decay_rate = info['decay']
        
        current = self.affects[affect_name]
        diff = current - baseline
        self.affects[affect_name] = baseline + diff * np.exp(-decay_rate * dt)
    
    def _check_somatic_markers(self, stimulus: np.ndarray, context: Dict) -> Optional[str]:
        """Check for learned somatic markers (gut feelings)."""
        text = context.get('text', '')
        
        # Generate situation hash
        situation_key = self._hash_situation(text, context)
        
        if situation_key in self.somatic_markers:
            marker = self.somatic_markers[situation_key]
            
            # Apply marker influence
            if marker['valence'] > 0:
                self.affects['SEEKING'] += 0.1
                self.affects['CARE'] += 0.1
            else:
                self.affects['FEAR'] += 0.1
                self.affects['PANIC'] += 0.05
            
            return marker.get('description', 'gut_feeling')
        
        return None
    
    def _hash_situation(self, text: str, context: Dict) -> str:
        """Create a hash for situation matching."""
        # Use key elements for matching
        elements = [
            text[:100],  # First 100 chars
            context.get('who', ''),
            context.get('where', ''),
        ]
        combined = '|'.join(str(e) for e in elements)
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def update_somatic_marker(self, situation_text: str, 
                              outcome_valence: float,
                              outcome_arousal: float = 0.5,
                              description: str = None):
        """
        Learn a somatic marker from experience outcome.
        
        This is how "gut feelings" are formed — associating situations
        with their outcomes.
        """
        with self._lock:
            situation_key = self._hash_situation(situation_text, {})
            
            self.somatic_markers[situation_key] = {
                'valence': outcome_valence,
                'arousal': outcome_arousal,
                'description': description or ('favorable' if outcome_valence > 0 else 'unfavorable'),
                'text_preview': situation_text[:50],
                'learned_at': str(np.datetime64('now')),
            }
            
            self._save_somatic_markers()
    
    def _apply_context_modulation(self, context: Dict):
        """Apply context-specific affect modulation."""
        who = context.get('who', '').lower()
        
        # People we care about boost CARE (configurable, default empty)
        if self.care_people and any(p.lower() in who for p in self.care_people):
            self.affects['CARE'] = min(1.0, self.affects['CARE'] + 0.15)
        
        # Technical discussions boost SEEKING
        if context.get('domain') == 'technical':
            self.affects['SEEKING'] = min(1.0, self.affects['SEEKING'] + 0.1)
    
    def _compute_circumplex(self) -> Tuple[float, float, float, float]:
        """Compute Russell's circumplex from Panksepp affects."""
        total_activation = sum(self.affects.values())
        if total_activation < 0.01:
            return 0.0, 0.3, 0.5, 0.0
        
        # Weighted average of valence/arousal contributions
        valence = 0.0
        arousal = 0.0
        
        for name, activation in self.affects.items():
            info = self.CORE_AFFECTS[name]
            weight = activation / total_activation
            valence += info['valence'] * weight * activation
            arousal += info['arousal'] * weight * activation
        
        # Normalize to ranges
        valence = np.clip(valence, -1.0, 1.0)
        arousal = np.clip(arousal, 0.0, 1.0)
        
        # Urgency: high arousal + negative valence = urgent
        urgency = arousal * (1 - valence) / 2
        
        # Dominance: RAGE increases, FEAR/PANIC decrease
        dominance = (self.affects['RAGE'] * 0.8 - 
                    self.affects['FEAR'] * 0.5 - 
                    self.affects['PANIC'] * 0.3)
        dominance = np.clip(dominance, -1.0, 1.0)
        
        return valence, arousal, urgency, dominance
    
    def _compute_attention_weight(self) -> float:
        """Compute attention modulation weight."""
        _, arousal, _, _ = self._compute_circumplex()
        valence_magnitude = abs(self._compute_circumplex()[0])
        
        # Base attention
        attention = 1.0
        
        # Arousal boosts attention
        attention += arousal * 0.5
        
        # Strong valence (positive or negative) boosts attention
        attention += valence_magnitude * 0.3
        
        # FEAR especially grabs attention
        attention += self.affects['FEAR'] * 0.2
        
        return min(2.0, attention)
    
    def _record_history(self, state: AffectState):
        """Record state in history."""
        self.history.append({
            'affects': state.affects.copy(),
            'valence': state.valence,
            'arousal': state.arousal,
            'timestamp': str(np.datetime64('now')),
        })
        
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_affect_vector(self) -> np.ndarray:
        """Get current affect as a VSA-compatible vector."""
        with self._lock:
            result = np.zeros(self.dimension)
            
            for name, activation in self.affects.items():
                if activation > 0.1:  # Only include active affects
                    result += self.affect_vectors[name] * activation
            
            # Normalize
            norm = np.linalg.norm(result)
            if norm > 0:
                result = result / norm
            
            return result
    
    def get_trajectory(self, window: int = 10) -> Dict:
        """Get recent affect trajectory."""
        with self._lock:
            recent = self.history[-window:] if len(self.history) >= window else self.history
            
            if not recent:
                return {'trend': 'neutral', 'stability': 1.0}
            
            valences = [h['valence'] for h in recent]
            arousals = [h['arousal'] for h in recent]
            
            # Trend: are we getting happier or sadder?
            if len(valences) >= 2:
                trend = valences[-1] - valences[0]
                if trend > 0.1:
                    trend_label = 'improving'
                elif trend < -0.1:
                    trend_label = 'declining'
                else:
                    trend_label = 'stable'
            else:
                trend_label = 'neutral'
            
            # Stability: variance in arousal
            stability = 1.0 - np.std(arousals) if len(arousals) > 1 else 1.0
            
            return {
                'trend': trend_label,
                'stability': stability,
                'avg_valence': np.mean(valences),
                'avg_arousal': np.mean(arousals),
            }
    
    def _load_somatic_markers(self):
        """Load persisted somatic markers."""
        path = self.storage_path / "somatic_markers.json"
        if path.exists():
            try:
                with open(path) as f:
                    self.somatic_markers = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load somatic markers: {e}")
                self.somatic_markers = {}
    
    def _save_somatic_markers(self):
        """Persist somatic markers (atomic write)."""
        path = self.storage_path / "somatic_markers.json"
        try:
            from ..utils import atomic_json_save
            atomic_json_save(self.somatic_markers, path)
        except Exception as e:
            logger.warning(f"Failed to save somatic markers: {e}")
    
    def get_stats(self) -> Dict:
        """Get affective core statistics."""
        valence, arousal, urgency, dominance = self._compute_circumplex()
        trajectory = self.get_trajectory()
        
        return {
            'current_affects': self.affects.copy(),
            'valence': valence,
            'arousal': arousal,
            'urgency': urgency,
            'dominance': dominance,
            'trajectory': trajectory,
            'somatic_markers_count': len(self.somatic_markers),
            'history_length': len(self.history),
        }


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Testing SubcorticalAffectiveCore...")
    
    core = SubcorticalAffectiveCore()
    
    # Test with different inputs
    tests = [
        "I am so curious about how this works!",
        "This is frustrating, nothing works.",
        "I love spending time with my family.",
        "That joke was hilarious, I can't stop laughing!",
        "I'm worried about the deadline.",
    ]
    
    for text in tests:
        stimulus = np.random.randn(128)
        state = core.process(stimulus, {'text': text})
        logger.debug(f"'{text[:40]}...'")
        logger.debug(f"  Dominant: {state.dominant}")
        logger.debug(f"  Valence: {state.valence:.2f}, Arousal: {state.arousal:.2f}")
        logger.debug(f"  Attention: {state.attention_weight:.2f}")
    
    logger.info("Affective core working!")
