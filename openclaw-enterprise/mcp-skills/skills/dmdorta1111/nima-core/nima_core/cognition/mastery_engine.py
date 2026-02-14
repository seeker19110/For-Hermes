#!/usr/bin/env python3
"""
MASTERY Engine — Skill Development & Flow State System
======================================================
Integrates with NIMA Core's Affective Layer for variable MASTERY levels.

"MASTERY is not achievement. It is joy in the pursuit of competence."

Architecture:
- Reads from AffectiveCore (Layer 1: Panksepp 7 affects)
- Calculates composite MASTERY level (Layer 2)
- Emphasizes PLAY + challenge + skill growth
- Provides flow-state and skill-building modulation

Author: NIMA Project
Date: 2026
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple, ClassVar
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class ResponseStyle(Enum):
    """MASTERY response styles from 0.0 (avoidant) to 1.0 (flow state)."""
    AVOIDANT = "avoidant"          # 0.0-0.25: "This is too hard..."
    STRUGGLING = "struggling"      # 0.25-0.50: "Keep trying, you'll get it..."
    LEARNING = "learning"          # 0.50-0.70: "Good progress! Let's build on this..."
    GROWING = "growing"            # 0.70-0.90: "You're in the zone! Push further..."
    FLOW_STATE = "flow_state"      # 0.90-1.0: Complete absorption, optimal challenge


@dataclass
class DomainProfile:
    """User-defined domain with learned MASTERY parameters."""
    name: str
    base_threshold: float = 0.50
    triggers: List[str] = field(default_factory=list)
    affect_modifiers: Dict[str, float] = field(default_factory=dict)
    attempts: int = 0
    successes: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.attempts == 0:
            return 0.5
        return self.successes / self.attempts
    
    @property
    def adjusted_threshold(self) -> float:
        adjustment = (self.success_rate - 0.5) * 0.2
        return max(0.1, min(0.9, self.base_threshold - adjustment))


@dataclass
class MasteryAnalysis:
    """Complete MASTERY analysis result."""
    level: float                      # 0.0 to 1.0
    style: ResponseStyle
    domain: str
    confidence: float
    activation_reasons: List[str]
    affect_contributions: Dict[str, float]
    play_level: float                # Joy in process
    challenge_match: float           # Difficulty vs skill balance
    progress_indicator: float        # Growth trajectory
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'level': round(self.level, 3),
            'style': self.style.value,
            'domain': self.domain,
            'confidence': round(self.confidence, 3),
            'activation_reasons': self.activation_reasons,
            'affect_contributions': {k: round(v, 3) for k, v in self.affect_contributions.items()},
            'play_level': round(self.play_level, 3),
            'challenge_match': round(self.challenge_match, 3),
            'progress_indicator': round(self.progress_indicator, 3)
        }


class MasteryEngine:
    """
    Variable MASTERY response system for skill development and flow states.
    
    Key insight: MASTERY requires:
    1. High PLAY (joy in the process)
    2. Optimal challenge (not too easy, not too hard)
    3. Sense of progress (skill growth)
    4. Low PANIC (anxiety blocks flow)
    
    Based on Csikszentmihalyi's Flow Theory + Panksepp's PLAY system.
    
    Usage:
        mastery = MasteryEngine(nima_core.affective_core)
        analysis = mastery.analyze_message("I'm getting better at guitar!")
        # analysis.level = 0.82, analysis.style = ResponseStyle.FLOW_STATE
    """
    
    FOUNDATION_AFFECTS: ClassVar[List[str]] = ['SEEKING', 'RAGE', 'FEAR', 'LUST', 'CARE', 'PANIC', 'PLAY']
    
    # MASTERY Formula (Layer 2 composite)
    # Key: MASTERY = PLAY + optimal_challenge + progress - anxiety
    MASTERY_FORMULA: ClassVar[Dict[str, float]] = {
        'PLAY': 0.40,        # Joy in the process (essential)
        'SEEKING': 0.25,     # Curiosity, wanting to improve
        'LUST': 0.15,        # Desire for competence
        'RAGE': 0.10,        # Frustration can drive improvement (channelled)
        'CARE': 0.10,        # Investment in skill
        'FEAR': -0.15,       # Performance anxiety blocks flow
        'PANIC': -0.30,      # Overwhelm destroys mastery
    }
    
    # Default domains
    DEFAULT_DOMAINS: ClassVar[Dict[str, DomainProfile]] = {
        'skill_practice': DomainProfile(
            name='skill_practice',
            base_threshold=0.50,
            triggers=['practice', 'skill', 'improve', 'better', 'progress', 'training'],
            affect_modifiers={'PLAY': 0.25, 'SEEKING': 0.20, 'PANIC': -0.15}
        ),
        'creative_mastery': DomainProfile(
            name='creative_mastery',
            base_threshold=0.45,
            triggers=['art', 'music', 'write', 'create', 'craft', 'mastery', 'expert'],
            affect_modifiers={'PLAY': 0.30, 'SEEKING': 0.15, 'LUST': 0.10}
        ),
        'athletic_training': DomainProfile(
            name='athletic_training',
            base_threshold=0.55,
            triggers=['workout', 'train', 'fitness', 'strength', 'endurance', 'athletic'],
            affect_modifiers={'PLAY': 0.20, 'RAGE': 0.15, 'SEEKING': 0.15}
        ),
        'professional_development': DomainProfile(
            name='professional_development',
            base_threshold=0.55,
            triggers=['career', 'professional', 'competence', 'expertise', 'certification'],
            affect_modifiers={'SEEKING': 0.25, 'LUST': 0.15, 'PLAY': 0.10}
        ),
        'academic_mastery': DomainProfile(
            name='academic_mastery',
            base_threshold=0.55,
            triggers=['study', 'academic', 'grades', 'exam', 'scholar', 'research'],
            affect_modifiers={'SEEKING': 0.25, 'CARE': 0.15, 'PANIC': -0.10}
        ),
        'default': DomainProfile(name='default', base_threshold=0.50)
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # GENERIC DOMAIN TEMPLATES — 30+ mastery scenarios
    # ═══════════════════════════════════════════════════════════════════
    
    GENERIC_DOMAIN_TEMPLATES: ClassVar[Dict[str, DomainProfile]] = {
        # MUSICAL MASTERY
        'instrument_mastery': DomainProfile(
            name='instrument_mastery',
            base_threshold=0.50,
            triggers=['piano', 'guitar', 'violin', 'drums', 'instrument', 'practice', 'repertoire'],
            affect_modifiers={'PLAY': 0.30, 'SEEKING': 0.20, 'RAGE': 0.10}
        ),
        'vocal_training': DomainProfile(
            name='vocal_training',
            base_threshold=0.50,
            triggers=['sing', 'voice', 'vocal', 'choir', 'opera', 'vocalize'],
            affect_modifiers={'PLAY': 0.25, 'SEEKING': 0.15, 'FEAR': 0.05}
        ),
        'music_theory': DomainProfile(
            name='music_theory',
            base_threshold=0.55,
            triggers=['theory', 'composition', 'harmony', 'counterpoint', 'arrange'],
            affect_modifiers={'SEEKING': 0.25, 'PLAY': 0.15, 'CARE': 0.10}
        ),
        
        # ATHLETIC MASTERY
        'strength_training': DomainProfile(
            name='strength_training',
            base_threshold=0.55,
            triggers=['lift', 'weight', 'strength', 'muscle', 'gym', 'powerlift', 'bodybuild'],
            affect_modifiers={'RAGE': 0.20, 'PLAY': 0.15, 'LUST': 0.15}
        ),
        'endurance_training': DomainProfile(
            name='endurance_training',
            base_threshold=0.55,
            triggers=['run', 'marathon', 'cycling', 'swim', 'triathlon', 'endurance', 'cardio'],
            affect_modifiers={'SEEKING': 0.20, 'PLAY': 0.20, 'RAGE': 0.10}
        ),
        'martial_arts': DomainProfile(
            name='martial_arts',
            base_threshold=0.50,
            triggers=['karate', 'judo', 'bjj', 'boxing', 'martial', 'dojo', 'belt', 'kata'],
            affect_modifiers={'PLAY': 0.25, 'RAGE': 0.15, 'SEEKING': 0.15}
        ),
        'yoga_mindfulness': DomainProfile(
            name='yoga_mindfulness',
            base_threshold=0.50,
            triggers=['yoga', 'meditation', 'mindfulness', 'pose', 'asana', 'breathe'],
            affect_modifiers={'PLAY': 0.25, 'CARE': 0.20, 'PANIC': -0.20}
        ),
        'sports_skill': DomainProfile(
            name='sports_skill',
            base_threshold=0.55,
            triggers=['tennis', 'golf', 'basketball', 'soccer', 'technique', 'form'],
            affect_modifiers={'PLAY': 0.30, 'SEEKING': 0.15, 'RAGE': 0.05}
        ),
        
        # ARTISTIC MASTERY
        'visual_arts': DomainProfile(
            name='visual_arts',
            base_threshold=0.45,
            triggers=['paint', 'draw', 'sketch', 'sculpt', 'artistic', 'portfolio', 'exhibit'],
            affect_modifiers={'PLAY': 0.35, 'SEEKING': 0.15, 'LUST': 0.10}
        ),
        'digital_art': DomainProfile(
            name='digital_art',
            base_threshold=0.50,
            triggers=['digital', 'illustration', 'photoshop', 'procreate', '3d', 'animation'],
            affect_modifiers={'PLAY': 0.30, 'SEEKING': 0.20, 'LUST': 0.10}
        ),
        'photography': DomainProfile(
            name='photography',
            base_threshold=0.50,
            triggers=['photo', 'camera', 'shoot', 'composition', 'lighting', 'lens'],
            affect_modifiers={'PLAY': 0.30, 'SEEKING': 0.15, 'CARE': 0.10}
        ),
        'writing_craft': DomainProfile(
            name='writing_craft',
            base_threshold=0.50,
            triggers=['write', 'novel', 'story', 'draft', 'edit', 'manuscript', 'author'],
            affect_modifiers={'PLAY': 0.25, 'SEEKING': 0.20, 'LUST': 0.15}
        ),
        'crafts_making': DomainProfile(
            name='crafts_making',
            base_threshold=0.45,
            triggers=['knit', 'sew', 'woodwork', 'pottery', 'jewelry', 'maker', 'handmade'],
            affect_modifiers={'PLAY': 0.35, 'CARE': 0.15, 'SEEKING': 0.10}
        ),
        
        # TECHNICAL MASTERY
        'coding_mastery': DomainProfile(
            name='coding_mastery',
            base_threshold=0.55,
            triggers=['code', 'program', 'algorithm', 'debug', 'refactor', 'architecture'],
            affect_modifiers={'SEEKING': 0.30, 'PLAY': 0.15, 'RAGE': 0.10}
        ),
        'data_science': DomainProfile(
            name='data_science',
            base_threshold=0.60,
            triggers=['data', 'ml', 'ai', 'model', 'analysis', 'statistics', 'python'],
            affect_modifiers={'SEEKING': 0.35, 'PLAY': 0.10, 'CARE': 0.10}
        ),
        'language_learning': DomainProfile(
            name='language_learning',
            base_threshold=0.55,
            triggers=['language', 'fluent', 'vocabulary', 'grammar', 'conversation', 'immersion'],
            affect_modifiers={'PLAY': 0.25, 'SEEKING': 0.25, 'LUST': 0.15}
        ),
        'math_mastery': DomainProfile(
            name='math_mastery',
            base_threshold=0.60,
            triggers=['math', 'calculus', 'algebra', 'proof', 'theorem', 'problem', 'equation'],
            affect_modifiers={'SEEKING': 0.35, 'PLAY': 0.15, 'RAGE': 0.05}
        ),
        
        # PROFESSIONAL MASTERY
        'leadership_mastery': DomainProfile(
            name='leadership_mastery',
            base_threshold=0.55,
            triggers=['lead', 'manager', 'executive', 'team', 'influence', 'strategy'],
            affect_modifiers={'SEEKING': 0.25, 'LUST': 0.15, 'CARE': 0.15}
        ),
        'sales_mastery': DomainProfile(
            name='sales_mastery',
            base_threshold=0.55,
            triggers=['sales', 'close', 'pitch', 'prospect', 'negotiate', 'quota'],
            affect_modifiers={'LUST': 0.25, 'PLAY': 0.15, 'SEEKING': 0.10}
        ),
        'public_speaking_mastery': DomainProfile(
            name='public_speaking_mastery',
            base_threshold=0.55,
            triggers=['speak', 'presentation', 'keynote', 'stage', ' TED', 'oratory'],
            affect_modifiers={'SEEKING': 0.25, 'PLAY': 0.20, 'FEAR': -0.10}
        ),
        'negotiation_mastery': DomainProfile(
            name='negotiation_mastery',
            base_threshold=0.55,
            triggers=['negotiate', 'deal', 'contract', 'terms', 'bargain', 'persuade'],
            affect_modifiers={'SEEKING': 0.25, 'RAGE': 0.10, 'LUST': 0.15}
        ),
        
        # ACADEMIC MASTERY
        'research_mastery': DomainProfile(
            name='research_mastery',
            base_threshold=0.60,
            triggers=['research', 'phd', 'dissertation', 'paper', 'academic', 'publish'],
            affect_modifiers={'SEEKING': 0.35, 'CARE': 0.15, 'PLAY': 0.10}
        ),
        'test_preparation': DomainProfile(
            name='test_preparation',
            base_threshold=0.60,
            triggers=['exam', 'test', 'study', 'prep', 'LSAT', 'MCAT', 'GRE', 'bar'],
            affect_modifiers={'SEEKING': 0.30, 'RAGE': 0.10, 'PANIC': -0.15}
        ),
        'teaching_mastery': DomainProfile(
            name='teaching_mastery',
            base_threshold=0.55,
            triggers=['teach', 'educator', 'pedagogy', 'curriculum', 'instruction'],
            affect_modifiers={'CARE': 0.25, 'PLAY': 0.20, 'SEEKING': 0.15}
        ),
        
        # CREATIVE MASTERY
        'design_mastery': DomainProfile(
            name='design_mastery',
            base_threshold=0.50,
            triggers=['design', 'UX', 'UI', 'graphic', 'visual', 'portfolio', 'creative'],
            affect_modifiers={'PLAY': 0.30, 'SEEKING': 0.20, 'LUST': 0.10}
        ),
        'culinary_arts': DomainProfile(
            name='culinary_arts',
            base_threshold=0.50,
            triggers=['cook', 'chef', 'culinary', 'recipe', 'kitchen', 'flavor', 'technique'],
            affect_modifiers={'PLAY': 0.35, 'SEEKING': 0.15, 'LUST': 0.15}
        ),
        'game_mastery': DomainProfile(
            name='game_mastery',
            base_threshold=0.50,
            triggers=['game', 'chess', 'esports', 'strategy', 'competitive', 'rank'],
            affect_modifiers={'PLAY': 0.35, 'SEEKING': 0.20, 'RAGE': 0.10}
        ),
        
        # PERSONAL MASTERY
        'habit_building': DomainProfile(
            name='habit_building',
            base_threshold=0.55,
            triggers=['habit', 'routine', 'discipline', 'consistency', 'ritual', 'system'],
            affect_modifiers={'SEEKING': 0.25, 'CARE': 0.20, 'PLAY': 0.10}
        ),
        'mindset_mastery': DomainProfile(
            name='mindset_mastery',
            base_threshold=0.55,
            triggers=['mindset', 'growth', 'resilience', 'grit', 'mental', 'psychology'],
            affect_modifiers={'SEEKING': 0.25, 'PLAY': 0.20, 'RAGE': 0.10}
        ),
        'memory_training': DomainProfile(
            name='memory_training',
            base_threshold=0.55,
            triggers=['memory', 'mnemonic', 'remember', 'recall', 'brain', 'cognitive'],
            affect_modifiers={'SEEKING': 0.30, 'PLAY': 0.15, 'CARE': 0.10}
        ),
        
        # SOCIAL MASTERY
        'social_skills': DomainProfile(
            name='social_skills',
            base_threshold=0.55,
            triggers=['social', 'charisma', 'network', 'charm', 'conversation', 'etiquette'],
            affect_modifiers={'PLAY': 0.25, 'SEEKING': 0.20, 'LUST': 0.10}
        ),
        'emotional_intelligence': DomainProfile(
            name='emotional_intelligence',
            base_threshold=0.55,
            triggers=['emotional', 'empathy', 'EQ', 'self-aware', 'regulate', 'social'],
            affect_modifiers={'CARE': 0.30, 'SEEKING': 0.20, 'PLAY': 0.10}
        ),
        'dating_mastery': DomainProfile(
            name='dating_mastery',
            base_threshold=0.50,
            triggers=['dating', 'flirt', 'attract', 'romance', 'relationship', 'court'],
            affect_modifiers={'LUST': 0.30, 'PLAY': 0.20, 'SEEKING': 0.15}
        ),
    }
    
    # Activation signals
    ACTIVATION_SIGNALS: ClassVar[Dict[str, str]] = {
        'joy_in_process': r'\b(enjoy|love|fun|passion|joy|flow|absorbed|lose track)\b',
        'improvement': r'\b(better|improve|progress|advance|level up|growth|develop)\b',
        'challenge_optimal': r'\b(challenging|just right|sweet spot|stretch|pushing|edge)\b',
        'practice_regular': r'\b(practice|routine|daily|habit|consistent|discipline)\b',
        'skill_focused': r'\b(skill|technique|craft|mastery|expert|competence)\b',
        'frustration_normal': r'\b(frustrated|stuck|plateau|struggling|hard|difficult)\b',
        'celebration_small': r'\b(milestone|win|success|breakthrough|finally|nailed it)\b',
        'learning_love': r'\b(learn|study|curious|fascinated|discover|understand)\b',
        'feedback_seeking': r'\b(feedback|coach|mentor|critique|advice|guidance)\b',
        'long_term': r'\b(journey|marathon|long game|commitment|dedication|years)\b'
    }
    
    def __init__(self, affective_core=None, data_dir: Optional[str] = None):
        """Initialize MASTERY Engine."""
        self.affective_core = affective_core
        self.data_dir = Path(data_dir) if data_dir else Path.home() / '.nima' / 'mastery_data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.domains: Dict[str, DomainProfile] = {}
        self._load_default_domains()
        
        self.user_preference = 0.5
        self.recent_interactions: List[Dict] = []
        
        self._load_user_data()
        
        logger.info(f"MASTERY Engine initialized with {len(self.domains)} domains")
    
    def _load_default_domains(self):
        """Load default domain configurations (copies to avoid shared state)."""
        for name, profile in self.DEFAULT_DOMAINS.items():
            # Create a copy to avoid shared mutable state across instances
            self.domains[name] = DomainProfile(
                name=profile.name,
                base_threshold=profile.base_threshold,
                triggers=profile.triggers.copy(),
                affect_modifiers=profile.affect_modifiers.copy(),
                attempts=profile.attempts,
                successes=profile.successes
            )
    
    def load_template_domain(self, template_name: str, custom_name: Optional[str] = None):
        """Load a generic domain template."""
        if template_name not in self.GENERIC_DOMAIN_TEMPLATES:
            available = list(self.GENERIC_DOMAIN_TEMPLATES.keys())
            raise ValueError(f"Unknown template '{template_name}'. Available: {available}")
        
        template = self.GENERIC_DOMAIN_TEMPLATES[template_name]
        name = custom_name or template_name
        
        profile = DomainProfile(
            name=name,
            base_threshold=template.base_threshold,
            triggers=template.triggers.copy(),
            affect_modifiers=template.affect_modifiers.copy()
        )
        
        self.domains[name] = profile
        logger.info(f"Loaded MASTERY domain template: {template_name} as '{name}'")
        return profile
    
    def detect_domain(self, message: str, context: Optional[Dict] = None) -> str:
        """Detect which domain a message belongs to."""
        message_lower = message.lower()
        context = context or {}
        
        for domain_name, profile in self.domains.items():
            if domain_name == 'default':
                continue
            
            for trigger in profile.triggers:
                if trigger.lower() in message_lower:
                    return domain_name
        
        return context.get('last_domain', 'default')
    
    def get_affect_state(self) -> Dict[str, float]:
        """Get current affective state."""
        if self.affective_core is None:
            return {affect: 0.3 for affect in self.FOUNDATION_AFFECTS}
        
        try:
            if hasattr(self.affective_core, 'current_state'):
                state = self.affective_core.current_state
                if hasattr(state, 'affects'):
                    return state.affects
            
            if hasattr(self.affective_core, 'get_current_affect'):
                current = self.affective_core.get_current_affect()
                if isinstance(current, dict):
                    return current
                return {affect: 0.3 for affect in self.FOUNDATION_AFFECTS}
            
            return {affect: 0.3 for affect in self.FOUNDATION_AFFECTS}
            
        except (AttributeError, TypeError) as e:
            logger.warning("Could not read affective state: %s", e, exc_info=True)
            return {affect: 0.3 for affect in self.FOUNDATION_AFFECTS}
    
    def calculate_activation_score(self, message: str) -> Tuple[float, List[str]]:
        """Calculate activation score from message signals."""
        import re
        
        score = 0.0
        reasons = []
        
        for signal_name, pattern in self.ACTIVATION_SIGNALS.items():
            if re.search(pattern, message, re.IGNORECASE):
                weights = {
                    'joy_in_process': 0.35,
                    'improvement': 0.30,
                    'practice_regular': 0.25,
                    'skill_focused': 0.30,
                    'challenge_optimal': 0.25,
                    'learning_love': 0.25,
                    'celebration_small': 0.20,
                    'feedback_seeking': 0.20,
                    'long_term': 0.20,
                    'frustration_normal': 0.15
                }
                score += weights.get(signal_name, 0.15)
                reasons.append(signal_name)
        
        if self.user_preference > 0.6:
            score += 0.15
            reasons.append('historical_preference')
        
        return min(1.0, score), reasons
    
    def analyze_message(self, message: str, context: Optional[Dict] = None) -> MasteryAnalysis:
        """Main entry point: Analyze message and calculate MASTERY level."""
        # Input validation
        if not message or not isinstance(message, str):
            logger.warning(f"Invalid message provided to MASTERY engine: {message}")
            return self._default_analysis()
        
        if len(message.strip()) == 0:
            logger.warning("Empty message provided to MASTERY engine")
            return self._default_analysis()
        
        context = context or {}
        
        domain = self.detect_domain(message, context)
        domain_profile = self.domains.get(domain, self.domains['default'])
        
        affect_state = self.get_affect_state()
        
        # Extract key levels
        play_level = affect_state.get('PLAY', 0.3)
        seeking_level = affect_state.get('SEEKING', 0.3)
        panic_level = affect_state.get('PANIC', 0.0)
        
        # Calculate challenge match (optimal difficulty)
        # High play + moderate rage = good challenge
        rage_level = affect_state.get('RAGE', 0.3)
        challenge_match = (play_level * 0.6 + rage_level * 0.4)
        
        # Calculate mastery from formula
        mastery_level = 0.0
        affect_contributions = {}
        
        for affect, weight in self.MASTERY_FORMULA.items():
            intensity = affect_state.get(affect, 0.3)
            contribution = intensity * weight
            mastery_level += contribution
            affect_contributions[affect] = contribution
        
        # Normalize
        mastery_level = (mastery_level + 0.5) / 1.5
        mastery_level = max(0.0, min(1.0, mastery_level))
        
        # Apply domain threshold
        base_threshold = domain_profile.adjusted_threshold
        
        if mastery_level < base_threshold:
            mastery_level = mastery_level * 0.8
        else:
            mastery_level = mastery_level * 1.1
            mastery_level = min(1.0, mastery_level)
        
        # Apply domain modifiers
        for affect, modifier in domain_profile.affect_modifiers.items():
            if affect in affect_state:
                mastery_level += affect_state[affect] * modifier * 0.2
        
        # Calculate activation
        activation_score, activation_reasons = self.calculate_activation_score(message)
        mastery_level += activation_score * 0.3
        
        # Apply user preference
        mastery_level += (self.user_preference - 0.5) * 0.2
        
        mastery_level = max(0.0, min(1.0, mastery_level))
        
        # Determine style
        if mastery_level < 0.25:
            style = ResponseStyle.AVOIDANT
        elif mastery_level < 0.50:
            style = ResponseStyle.STRUGGLING
        elif mastery_level < 0.70:
            style = ResponseStyle.LEARNING
        elif mastery_level < 0.90:
            style = ResponseStyle.GROWING
        else:
            style = ResponseStyle.FLOW_STATE
        
        # Calculate confidence
        if domain_profile.attempts < 3:
            confidence = 0.6
        else:
            confidence = max(0.3, min(0.95, domain_profile.success_rate))
        
        # Progress indicator (seeking + care - panic)
        care_level = affect_state.get('CARE', 0.3)
        progress = (seeking_level * 0.4 + care_level * 0.3 - panic_level * 0.3)
        
        return MasteryAnalysis(
            level=mastery_level,
            style=style,
            domain=domain,
            confidence=confidence,
            activation_reasons=activation_reasons,
            affect_contributions=affect_contributions,
            play_level=play_level,
            challenge_match=challenge_match,
            progress_indicator=progress
        )
    
    def record_outcome(self, analysis: MasteryAnalysis, success: bool,
                      user_feedback: Optional[str] = None):
        """Record outcome for learning."""
        domain = analysis.domain
        
        if domain in self.domains:
            self.domains[domain].attempts += 1
            if success:
                self.domains[domain].successes += 1
        
        adjustment = 0.03 if success else -0.02
        if analysis.level > 0.5:
            self.user_preference = max(0.2, min(0.9, self.user_preference + adjustment))
        else:
            self.user_preference = max(0.2, min(0.9, self.user_preference - adjustment))
        
        self.recent_interactions.append({
            'timestamp': time.time(),
            'domain': domain,
            'level': analysis.level,
            'success': success,
            'feedback': user_feedback
        })
        
        if len(self.recent_interactions) > 100:
            self.recent_interactions = self.recent_interactions[-100:]
        
        self._save_user_data()
    
    def _load_user_data(self):
        """Load user learning data."""
        user_data_path = self.data_dir / 'user_mastery_profile.json'
        if user_data_path.exists():
            try:
                with open(user_data_path, 'r') as f:
                    data = json.load(f)
                
                self.user_preference = data.get('user_preference', 0.5)
                
                for domain_name, domain_data in data.get('domains', {}).items():
                    if domain_name in self.domains:
                        self.domains[domain_name].attempts = domain_data.get('attempts', 0)
                        self.domains[domain_name].successes = domain_data.get('successes', 0)
                
            except (OSError, json.JSONDecodeError) as e:
                logger.warning("Could not load user MASTERY data: %s", e, exc_info=True)
    
    def _save_user_data(self):
        """Persist user learning data."""
        try:
            data = {
                'user_preference': self.user_preference,
                'domains': {
                    name: {
                        'attempts': profile.attempts,
                        'successes': profile.successes
                    }
                    for name, profile in self.domains.items()
                }
            }
            
            user_data_path = self.data_dir / 'user_mastery_profile.json'
            with open(user_data_path, 'w') as f:
                json.dump(data, f, indent=2)
        except (OSError, TypeError) as e:
            logger.warning("Could not save user MASTERY data: %s", e, exc_info=True)
    
    def _default_analysis(self) -> MasteryAnalysis:
        """Return default analysis for invalid/empty messages."""
        return MasteryAnalysis(
            level=0.0,
            style=ResponseStyle.AVOIDANT,
            domain='default',
            confidence=0.0,
            activation_reasons=[],
            affect_contributions={affect: 0.0 for affect in self.MASTERY_FORMULA.keys()},
            play_level=0.0,
            challenge_match=0.0,
            progress_indicator=0.0
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get MASTERY statistics."""
        return {
            'user_preference': round(self.user_preference, 3),
            'domains_registered': len(self.domains),
            'domains': {
                name: {
                    'attempts': profile.attempts,
                    'successes': profile.successes,
                    'success_rate': round(profile.success_rate, 3)
                }
                for name, profile in self.domains.items()
            }
        }