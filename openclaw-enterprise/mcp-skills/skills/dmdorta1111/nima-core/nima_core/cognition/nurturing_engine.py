#!/usr/bin/env python3
"""
NURTURING Engine — Patient Guidance & Mentoring System
======================================================
Integrates with NIMA Core's Affective Layer for variable NURTURING levels.

"NURTURING is not doing for someone. It is sustained presence through growth."

Architecture:
- Reads from AffectiveCore (Layer 1: Panksepp 7 affects)
- Calculates composite NURTURING level (Layer 2)
- Emphasizes CARE + sustained attention + positive outcomes
- Provides patient, step-by-step guidance modulation

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
    """NURTURING response styles from 0.0 (dismissive) to 1.0 (deep nurturing)."""
    DISMISSIVE = "dismissive"      # 0.0-0.25: "Just figure it out..."
    INSTRUCTIONAL = "instructional" # 0.25-0.50: "Here's what to do..."
    GUIDING = "guiding"            # 0.50-0.70: "Let's explore this together..."
    MENTORING = "mentoring"        # 0.70-0.90: "I'll walk with you through this..."
    DEEP_NURTURING = "deep_nurturing"  # 0.90-1.0: Complete presence & patience


@dataclass
class DomainProfile:
    """User-defined domain with learned NURTURING parameters."""
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
class NurturingAnalysis:
    """Complete NURTURING analysis result."""
    level: float                      # 0.0 to 1.0
    style: ResponseStyle
    domain: str
    confidence: float
    activation_reasons: List[str]
    affect_contributions: Dict[str, float]
    care_level: float                 # Tracked separately
    patience_indicator: float         # Sustained attention
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'level': round(self.level, 3),
            'style': self.style.value,
            'domain': self.domain,
            'confidence': round(self.confidence, 3),
            'activation_reasons': self.activation_reasons,
            'affect_contributions': {k: round(v, 3) for k, v in self.affect_contributions.items()},
            'care_level': round(self.care_level, 3),
            'patience_indicator': round(self.patience_indicator, 3)
        }


class NurturingEngine:
    """
    Variable NURTURING response system for teaching, mentoring, caregiving.
    
    Key insight: NURTURING requires:
    1. High CARE (genuine concern for growth)
    2. Sustained attention (not rushing)
    3. Playful patience (growth mindset)
    4. Low panic/frustration (safe environment)
    
    Usage:
        nurturing = NurturingEngine(nima_core.affective_core)
        analysis = nurturing.analyze_message("Teach my son to ride a bike")
        # analysis.level = 0.75, analysis.style = ResponseStyle.MENTORING
    """
    
    FOUNDATION_AFFECTS: ClassVar[List[str]] = ['SEEKING', 'RAGE', 'FEAR', 'LUST', 'CARE', 'PANIC', 'PLAY']
    
    # NURTURING Formula
    NURTURING_FORMULA: ClassVar[Dict[str, float]] = {
        'CARE': 0.40,        # Foundation of nurturing
        'PLAY': 0.25,        # Joy in the process, growth mindset
        'SEEKING': 0.15,     # Curiosity about learner's growth
        'LUST': 0.10,        # Desire to see them succeed
        'RAGE': -0.15,       # Frustration undermines nurturing
        'FEAR': -0.10,       # Anxiety blocks patience
        'PANIC': -0.35,      # Urgency destroys nurturing presence
    }
    
    # Default domains
    DEFAULT_DOMAINS: ClassVar[Dict[str, DomainProfile]] = {
        'parenting': DomainProfile(
            name='parenting',
            base_threshold=0.45,
            triggers=['parent', 'child', 'kid', 'son', 'daughter', 'raise', 'teach'],
            affect_modifiers={'CARE': 0.30, 'PLAY': 0.15, 'PANIC': -0.15}
        ),
        'teaching': DomainProfile(
            name='teaching',
            base_threshold=0.50,
            triggers=['teach', 'learn', 'student', 'explain', 'lesson', 'education'],
            affect_modifiers={'CARE': 0.25, 'SEEKING': 0.15, 'PLAY': 0.10}
        ),
        'mentoring': DomainProfile(
            name='mentoring',
            base_threshold=0.55,
            triggers=['mentor', 'guide', 'coach', 'advise', 'career', 'growth'],
            affect_modifiers={'CARE': 0.25, 'SEEKING': 0.20, 'LUST': 0.10}
        ),
        'caregiving': DomainProfile(
            name='caregiving',
            base_threshold=0.50,
            triggers=['care', 'elderly', 'sick', 'patient', 'disability', 'support'],
            affect_modifiers={'CARE': 0.35, 'FEAR': 0.05, 'PANIC': -0.20}
        ),
        'therapy_counseling': DomainProfile(
            name='therapy_counseling',
            base_threshold=0.60,
            triggers=['therapy', 'counsel', 'mental health', 'heal', 'process'],
            affect_modifiers={'CARE': 0.30, 'SEEKING': 0.10, 'PANIC': -0.25}
        ),
        'default': DomainProfile(name='default', base_threshold=0.50)
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # GENERIC DOMAIN TEMPLATES — 30+ nurturing scenarios
    # ═══════════════════════════════════════════════════════════════════
    
    GENERIC_DOMAIN_TEMPLATES: ClassVar[Dict[str, DomainProfile]] = {
        # PARENTING & CHILD REARING
        'early_childhood': DomainProfile(
            name='early_childhood',
            base_threshold=0.45,
            triggers=['baby', 'toddler', 'infant', 'newborn', '0-3', 'preschool'],
            affect_modifiers={'CARE': 0.35, 'PLAY': 0.20, 'PANIC': -0.15}
        ),
        'adolescent_guidance': DomainProfile(
            name='adolescent_guidance',
            base_threshold=0.50,
            triggers=['teen', 'teenager', 'adolescent', 'puberty', 'rebel', 'rebellious'],
            affect_modifiers={'CARE': 0.30, 'RAGE': -0.10, 'PANIC': -0.10}
        ),
        'special_needs_parenting': DomainProfile(
            name='special_needs_parenting',
            base_threshold=0.55,
            triggers=['autism', 'adhd', 'special needs', 'disability', 'spectrum', 'learning disability'],
            affect_modifiers={'CARE': 0.40, 'FEAR': 0.10, 'PANIC': -0.20}
        ),
        'homework_help': DomainProfile(
            name='homework_help',
            base_threshold=0.50,
            triggers=['homework', 'assignment', 'school work', 'study', 'math problem'],
            affect_modifiers={'CARE': 0.25, 'PLAY': 0.15, 'RAGE': -0.15}
        ),
        'life_skills_teaching': DomainProfile(
            name='life_skills_teaching',
            base_threshold=0.50,
            triggers=['cook', 'clean', 'budget', 'drive', 'independent', 'life skill'],
            affect_modifiers={'CARE': 0.25, 'SEEKING': 0.15, 'PLAY': 0.10}
        ),
        
        # TEACHING & EDUCATION
        'skill_teaching': DomainProfile(
            name='skill_teaching',
            base_threshold=0.50,
            triggers=['teach skill', 'learn to', 'how do I', 'show me how', 'practice'],
            affect_modifiers={'CARE': 0.20, 'PLAY': 0.20, 'SEEKING': 0.15}
        ),
        'language_learning': DomainProfile(
            name='language_learning',
            base_threshold=0.55,
            triggers=['language', 'learn spanish', 'learn french', 'fluent', 'vocabulary'],
            affect_modifiers={'CARE': 0.20, 'PLAY': 0.20, 'SEEKING': 0.20}
        ),
        'musical_instruction': DomainProfile(
            name='musical_instruction',
            base_threshold=0.50,
            triggers=['piano', 'guitar', 'music', 'instrument', 'practice', 'lesson'],
            affect_modifiers={'CARE': 0.25, 'PLAY': 0.25, 'RAGE': -0.10}
        ),
        'sports_coaching': DomainProfile(
            name='sports_coaching',
            base_threshold=0.50,
            triggers=['coach', 'sports', 'team', 'practice', 'training', 'athlete'],
            affect_modifiers={'CARE': 0.25, 'PLAY': 0.30, 'RAGE': -0.05}
        ),
        'art_instruction': DomainProfile(
            name='art_instruction',
            base_threshold=0.45,
            triggers=['art', 'draw', 'paint', 'sketch', 'creative', 'technique'],
            affect_modifiers={'CARE': 0.20, 'PLAY': 0.30, 'SEEKING': 0.15}
        ),
        'stem_education': DomainProfile(
            name='stem_education',
            base_threshold=0.55,
            triggers=['science', 'math', 'coding', 'engineering', 'robotics', 'programming'],
            affect_modifiers={'CARE': 0.25, 'SEEKING': 0.20, 'PLAY': 0.10}
        ),
        'adult_education': DomainProfile(
            name='adult_education',
            base_threshold=0.55,
            triggers=['adult learner', 'return to school', 'GED', 'continuing ed', 'career change'],
            affect_modifiers={'CARE': 0.30, 'FEAR': 0.05, 'SEEKING': 0.15}
        ),
        
        # MENTORING & PROFESSIONAL DEVELOPMENT
        'career_mentoring': DomainProfile(
            name='career_mentoring',
            base_threshold=0.55,
            triggers=['career advice', 'promotion', 'grow career', 'develop', 'potential'],
            affect_modifiers={'CARE': 0.25, 'SEEKING': 0.20, 'LUST': 0.15}
        ),
        'leadership_development': DomainProfile(
            name='leadership_development',
            base_threshold=0.55,
            triggers=['leadership', 'management', 'lead team', 'develop leaders', 'executive'],
            affect_modifiers={'CARE': 0.25, 'SEEKING': 0.15, 'PLAY': 0.10}
        ),
        'entrepreneur_mentoring': DomainProfile(
            name='entrepreneur_mentoring',
            base_threshold=0.50,
            triggers=['startup mentor', 'founder', 'business advice', 'entrepreneur', 'scale'],
            affect_modifiers={'CARE': 0.25, 'SEEKING': 0.25, 'LUST': 0.15}
        ),
        'peer_mentoring': DomainProfile(
            name='peer_mentoring',
            base_threshold=0.55,
            triggers=['peer', 'buddy', 'onboarding', 'new hire', 'orientation'],
            affect_modifiers={'CARE': 0.25, 'PLAY': 0.15, 'SEEKING': 0.10}
        ),
        
        # CAREGIVING & HEALTHCARE
        'elderly_care': DomainProfile(
            name='elderly_care',
            base_threshold=0.55,
            triggers=['elderly', 'aging parent', 'dementia', 'alzheimer', 'senior', 'old age'],
            affect_modifiers={'CARE': 0.40, 'PANIC': -0.20, 'FEAR': 0.05}
        ),
        'disability_support': DomainProfile(
            name='disability_support',
            base_threshold=0.55,
            triggers=['disability', 'wheelchair', 'accessibility', 'support worker', 'caregiver'],
            affect_modifiers={'CARE': 0.40, 'RAGE': -0.10, 'PANIC': -0.15}
        ),
        'chronic_illness_care': DomainProfile(
            name='chronic_illness_care',
            base_threshold=0.60,
            triggers=['chronic', 'diabetes', 'cancer', 'long term', 'illness management'],
            affect_modifiers={'CARE': 0.40, 'FEAR': 0.10, 'PANIC': -0.20}
        ),
        'mental_health_support': DomainProfile(
            name='mental_health_support',
            base_threshold=0.60,
            triggers=['depression', 'anxiety', 'support friend', 'mental health', 'crisis'],
            affect_modifiers={'CARE': 0.40, 'PANIC': -0.25, 'SEEKING': 0.10}
        ),
        'recovery_support': DomainProfile(
            name='recovery_support',
            base_threshold=0.55,
            triggers=['recovery', 'sober', 'relapse', 'support group', 'sponsor', 'healing'],
            affect_modifiers={'CARE': 0.35, 'PANIC': -0.15, 'SEEKING': 0.15}
        ),
        
        # THERAPY & COUNSELING
        'trauma_informed_care': DomainProfile(
            name='trauma_informed_care',
            base_threshold=0.65,
            triggers=['trauma', 'ptsd', 'abuse survivor', 'trigger', 'safe space'],
            affect_modifiers={'CARE': 0.45, 'PANIC': -0.30, 'FEAR': -0.10}
        ),
        'grief_counseling': DomainProfile(
            name='grief_counseling',
            base_threshold=0.60,
            triggers=['grief', 'loss', 'died', 'mourning', 'bereavement', 'widow'],
            affect_modifiers={'CARE': 0.45, 'PANIC': -0.20, 'FEAR': 0.05}
        ),
        'relationship_counseling': DomainProfile(
            name='relationship_counseling',
            base_threshold=0.60,
            triggers=['couples therapy', 'marriage', 'relationship help', 'communication', 'conflict'],
            affect_modifiers={'CARE': 0.35, 'RAGE': -0.15, 'PANIC': -0.15}
        ),
        'addiction_counseling': DomainProfile(
            name='addiction_counseling',
            base_threshold=0.60,
            triggers=['addiction', 'substance', 'recovery', 'relapse prevention', 'sobriety'],
            affect_modifiers={'CARE': 0.40, 'PANIC': -0.20, 'SEEKING': 0.15}
        ),
        
        # SPIRITUAL & COMMUNITY
        'spiritual_mentoring': DomainProfile(
            name='spiritual_mentoring',
            base_threshold=0.55,
            triggers=['spiritual', 'faith journey', 'disciple', 'sponsor', 'christian growth'],
            affect_modifiers={'CARE': 0.30, 'SEEKING': 0.20, 'PLAY': 0.10}
        ),
        'pastoral_care': DomainProfile(
            name='pastoral_care',
            base_threshold=0.55,
            triggers=['pastor', 'priest', 'shepherd', 'flock', 'parishioner', 'congregation'],
            affect_modifiers={'CARE': 0.35, 'PANIC': -0.15, 'SEEKING': 0.10}
        ),
        'community_organizing': DomainProfile(
            name='community_organizing',
            base_threshold=0.50,
            triggers=['community', 'organize', 'activist', 'volunteer', 'nonprofit', 'social work'],
            affect_modifiers={'CARE': 0.30, 'SEEKING': 0.20, 'PLAY': 0.10}
        ),
        
        # ANIMAL CARE
        'pet_training': DomainProfile(
            name='pet_training',
            base_threshold=0.50,
            triggers=['dog training', 'puppy', 'pet', 'animal', 'obedience', 'behavior'],
            affect_modifiers={'CARE': 0.25, 'PLAY': 0.30, 'RAGE': -0.20}
        ),
        'animal_rehabilitation': DomainProfile(
            name='animal_rehabilitation',
            base_threshold=0.55,
            triggers=['rescue animal', 'rehab', 'wildlife', 'injured', 'abused animal'],
            affect_modifiers={'CARE': 0.40, 'PANIC': -0.15, 'PLAY': 0.15}
        ),
        
        # SELF-NURTURING
        'self_care_practice': DomainProfile(
            name='self_care_practice',
            base_threshold=0.55,
            triggers=['self care', 'treat myself', 'rest', 'recharge', 'boundaries', 'burnout'],
            affect_modifiers={'CARE': 0.30, 'PANIC': -0.20, 'PLAY': 0.15}
        ),
        'inner_child_work': DomainProfile(
            name='inner_child_work',
            base_threshold=0.60,
            triggers=['inner child', 'reparent', 'childhood wound', 'heal myself', 'self compassion'],
            affect_modifiers={'CARE': 0.40, 'PLAY': 0.20, 'PANIC': -0.20}
        ),
        
        # CREATIVE NURTURING
        'creative_coaching': DomainProfile(
            name='creative_coaching',
            base_threshold=0.50,
            triggers=['creative block', 'artist coach', 'inspire', 'creative practice', 'muse'],
            affect_modifiers={'CARE': 0.25, 'PLAY': 0.30, 'SEEKING': 0.20}
        ),
        'writer_mentoring': DomainProfile(
            name='writer_mentoring',
            base_threshold=0.55,
            triggers=['writing coach', 'manuscript', 'author', 'novel', 'story feedback'],
            affect_modifiers={'CARE': 0.25, 'SEEKING': 0.20, 'PLAY': 0.15}
        ),
    }
    
    # Activation signals
    ACTIVATION_SIGNALS: ClassVar[Dict[str, str]] = {
        'care_language': r'\b(care|nurture|help|support|guide|teach|mentor)\b',
        'growth_focus': r'\b(grow|learn|develop|improve|progress|potential)\b',
        'patience_needed': r'\b(slowly|step by step|gradually|patient|take time)\b',
        'struggling': r'\b(struggling|difficult|hard time|frustrated|stuck)\b',
        'vulnerable': r'\b(vulnerable|sensitive|gentle|careful|tender)\b',
        'beginner': r'\b(new to|just started|beginner|first time|learning)\b',
        'child_related': r'\b(child|kid|baby|son|daughter|student|young)\b',
        'long_term': r'\b(long term|journey|process|over time|eventually)\b',
        'emotional_need': r'\b(need help|need support|need guidance|need someone)\b',
        'celebrate_small': r'\b(small win|progress|improvement|proud of you|good job)\b'
    }
    
    def __init__(self, affective_core=None, data_dir: Optional[str] = None):
        """Initialize NURTURING Engine."""
        self.affective_core = affective_core
        self.data_dir = Path(data_dir) if data_dir else Path.home() / '.nima' / 'nurturing_data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.domains: Dict[str, DomainProfile] = {}
        self._load_default_domains()
        
        self.user_preference = 0.5
        self.recent_interactions: List[Dict] = []
        
        self._load_user_data()
        
        logger.info(f"NURTURING Engine initialized with {len(self.domains)} domains")
    
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
        logger.info(f"Loaded NURTURING domain template: {template_name} as '{name}'")
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
                    'care_language': 0.35,
                    'growth_focus': 0.30,
                    'struggling': 0.25,
                    'vulnerable': 0.25,
                    'child_related': 0.30,
                    'patience_needed': 0.20,
                    'beginner': 0.20,
                    'long_term': 0.20,
                    'emotional_need': 0.25,
                    'celebrate_small': 0.20
                }
                score += weights.get(signal_name, 0.15)
                reasons.append(signal_name)
        
        if self.user_preference > 0.6:
            score += 0.15
            reasons.append('historical_preference')
        
        return min(1.0, score), reasons
    
    def analyze_message(self, message: str, context: Optional[Dict] = None) -> NurturingAnalysis:
        """Main entry point: Analyze message and calculate NURTURING level."""
        # Input validation
        if not message or not isinstance(message, str):
            logger.warning(f"Invalid message provided to NURTURING engine: {message}")
            return self._default_analysis()
        
        if len(message.strip()) == 0:
            logger.warning("Empty message provided to NURTURING engine")
            return self._default_analysis()
        
        context = context or {}
        
        domain = self.detect_domain(message, context)
        domain_profile = self.domains.get(domain, self.domains['default'])
        
        affect_state = self.get_affect_state()
        
        # Extract key levels
        care_level = affect_state.get('CARE', 0.3)
        panic_level = affect_state.get('PANIC', 0.0)
        play_level = affect_state.get('PLAY', 0.3)
        
        # Calculate nurturing from formula
        nurturing_level = 0.0
        affect_contributions = {}
        
        for affect, weight in self.NURTURING_FORMULA.items():
            intensity = affect_state.get(affect, 0.3)
            contribution = intensity * weight
            nurturing_level += contribution
            affect_contributions[affect] = contribution
        
        # Normalize
        nurturing_level = (nurturing_level + 0.5) / 1.5
        nurturing_level = max(0.0, min(1.0, nurturing_level))
        
        # Apply domain threshold
        base_threshold = domain_profile.adjusted_threshold
        
        if nurturing_level < base_threshold:
            nurturing_level = nurturing_level * 0.8
        else:
            nurturing_level = nurturing_level * 1.1
            nurturing_level = min(1.0, nurturing_level)
        
        # Apply domain modifiers
        for affect, modifier in domain_profile.affect_modifiers.items():
            if affect in affect_state:
                nurturing_level += affect_state[affect] * modifier * 0.2
        
        # Calculate activation
        activation_score, activation_reasons = self.calculate_activation_score(message)
        nurturing_level += activation_score * 0.3
        
        # Apply user preference
        nurturing_level += (self.user_preference - 0.5) * 0.2
        
        nurturing_level = max(0.0, min(1.0, nurturing_level))
        
        # Determine style
        if nurturing_level < 0.25:
            style = ResponseStyle.DISMISSIVE
        elif nurturing_level < 0.50:
            style = ResponseStyle.INSTRUCTIONAL
        elif nurturing_level < 0.70:
            style = ResponseStyle.GUIDING
        elif nurturing_level < 0.90:
            style = ResponseStyle.MENTORING
        else:
            style = ResponseStyle.DEEP_NURTURING
        
        # Calculate confidence
        if domain_profile.attempts < 3:
            confidence = 0.6
        else:
            confidence = max(0.3, min(0.95, domain_profile.success_rate))
        
        # Patience indicator (care + play - panic)
        patience = (care_level * 0.5 + play_level * 0.3 - panic_level * 0.2)
        
        return NurturingAnalysis(
            level=nurturing_level,
            style=style,
            domain=domain,
            confidence=confidence,
            activation_reasons=activation_reasons,
            affect_contributions=affect_contributions,
            care_level=care_level,
            patience_indicator=patience
        )
    
    def record_outcome(self, analysis: NurturingAnalysis, success: bool,
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
        user_data_path = self.data_dir / 'user_nurturing_profile.json'
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
                logger.warning("Could not load user NURTURING data: %s", e, exc_info=True)
    
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
            
            user_data_path = self.data_dir / 'user_nurturing_profile.json'
            with open(user_data_path, 'w') as f:
                json.dump(data, f, indent=2)
        except (OSError, TypeError) as e:
            logger.warning("Could not save user NURTURING data: %s", e, exc_info=True)
    
    def _default_analysis(self) -> NurturingAnalysis:
        """Return default analysis for invalid/empty messages."""
        return NurturingAnalysis(
            level=0.0,
            style=ResponseStyle.INSTRUCTIONAL,
            domain='default',
            confidence=0.0,
            activation_reasons=[],
            affect_contributions={affect: 0.0 for affect in self.NURTURING_FORMULA.keys()},
            care_level=0.5,
            patience_indicator=0.5
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get NURTURING statistics."""
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