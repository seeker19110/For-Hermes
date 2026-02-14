#!/usr/bin/env python3
"""
COURAGE Engine — Fear-Overcoming Response System
=================================================
Integrates with NIMA Core's Affective Layer to provide variable COURAGE levels.

"COURAGE is not absence of fear. It is action despite fear because something matters."

Architecture:
- Reads from AffectiveCore (Layer 1: Panksepp 7 affects)
- Calculates composite COURAGE level (Layer 2)
- Adjusts based on domain-specific success history
- Provides real-time response style modulation for feared-but-important tasks

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
    """COURAGE response styles from 0.0 (avoidant) to 1.0 (fearless action)."""
    AVOIDANT = "avoidant"          # 0.0-0.25: "Maybe we shouldn't..."
    CAUTIOUS = "cautious"          # 0.25-0.50: "Let's think about this carefully..."
    ENCOURAGING = "encouraging"    # 0.50-0.70: "You can do this. Here's how..."
    BOLD = "bold"                  # 0.70-0.90: "Face it. Now."
    FEARLESS = "fearless"          # 0.90-1.0: Absolute commitment to action


@dataclass
class DomainProfile:
    """User-defined domain with learned COURAGE parameters."""
    name: str
    base_threshold: float = 0.50
    triggers: List[str] = field(default_factory=list)
    affect_modifiers: Dict[str, float] = field(default_factory=dict)
    attempts: int = 0
    successes: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.attempts == 0:
            return 0.5  # Neutral default
        return self.successes / self.attempts
    
    @property
    def adjusted_threshold(self) -> float:
        """Adjust threshold based on success rate."""
        # Success pushes threshold down (more courage)
        # Failure pushes threshold up (more caution)
        adjustment = (self.success_rate - 0.5) * 0.2
        return max(0.1, min(0.9, self.base_threshold - adjustment))


@dataclass
class CourageAnalysis:
    """Complete COURAGE analysis result."""
    level: float                      # 0.0 to 1.0
    style: ResponseStyle
    domain: str
    confidence: float
    activation_reasons: List[str]
    affect_contributions: Dict[str, float]
    fear_level: float                 # Tracked separately
    importance_level: float           # Why this matters
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'level': round(self.level, 3),
            'style': self.style.value,
            'domain': self.domain,
            'confidence': round(self.confidence, 3),
            'activation_reasons': self.activation_reasons,
            'affect_contributions': {k: round(v, 3) for k, v in self.affect_contributions.items()},
            'fear_level': round(self.fear_level, 3),
            'importance_level': round(self.importance_level, 3)
        }


class CourageEngine:
    """
    Variable COURAGE response system integrated with NIMA Core.
    
    Reads real-time affective state and calculates appropriate
    COURAGE level for fear-overcoming response generation.
    
    Key insight: COURAGE requires:
    1. Fear present (otherwise it's not courage, it's just action)
    2. Something important at stake (CARE, LUST, SEEKING)
    3. Possibility of success (not PANIC)
    
    Usage:
        courage = CourageEngine(nima_core.affective_core)
        analysis = courage.analyze_message("I need to confront my boss about this")
        # analysis.level = 0.72, analysis.style = ResponseStyle.BOLD
    """
    
    # Layer 1: Foundation affects (Panksepp 7)
    FOUNDATION_AFFECTS: ClassVar[List[str]] = ['SEEKING', 'RAGE', 'FEAR', 'LUST', 'CARE', 'PANIC', 'PLAY']
    
    # COURAGE Formula (Layer 2 composite)
    # Key: COURAGE requires fear + importance - panic
    COURAGE_FORMULA: ClassVar[Dict[str, float]] = {
        'FEAR': 0.40,        # REQUIRED: Must have fear for courage
        'CARE': 0.35,        # Why it matters (someone/something important)
        'SEEKING': 0.20,     # Curiosity about outcome
        'LUST': 0.15,        # Desire for result
        'RAGE': 0.10,        # Frustration with status quo
        'PLAY': 0.05,        # Joy of challenge
        'PANIC': -0.50,      # Too much panic = paralysis, not courage
    }
    
    # Default domain configurations
    DEFAULT_DOMAINS: ClassVar[Dict[str, DomainProfile]] = {
        # Difficult conversations (high stakes, interpersonal)
        'difficult_conversations': DomainProfile(
            name='difficult_conversations',
            base_threshold=0.45,
            triggers=['confront', 'difficult', 'conversation', 'tell', 'truth', 'honest', 'confess'],
            affect_modifiers={'CARE': 0.25, 'FEAR': 0.15, 'RAGE': 0.10}
        ),
        # Moral stands (ethics, values)
        'moral_stands': DomainProfile(
            name='moral_stands',
            base_threshold=0.40,
            triggers=['wrong', 'unethical', 'principle', 'stand up', 'defend', 'justice'],
            affect_modifiers={'CARE': 0.30, 'RAGE': 0.20, 'FEAR': 0.10}
        ),
        # Vulnerability (emotional risk)
        'vulnerability': DomainProfile(
            name='vulnerability',
            base_threshold=0.50,
            triggers=['vulnerable', 'open up', 'share', 'admit', 'apologize', 'feelings'],
            affect_modifiers={'CARE': 0.25, 'FEAR': 0.20, 'PANIC': -0.10}
        ),
        # Risk taking (calculated risks)
        'risk_taking': DomainProfile(
            name='risk_taking',
            base_threshold=0.55,
            triggers=['risk', 'gamble', 'bet', 'chance', 'leap', 'uncertain'],
            affect_modifiers={'SEEKING': 0.20, 'FEAR': 0.15, 'LUST': 0.10}
        ),
        # Leadership challenges (leading despite fear)
        'leadership_challenges': DomainProfile(
            name='leadership_challenges',
            base_threshold=0.50,
            triggers=['lead', 'team', 'decide', 'responsibility', 'blame', 'fire'],
            affect_modifiers={'CARE': 0.25, 'FEAR': 0.15, 'RAGE': 0.10}
        ),
        'default': DomainProfile(name='default', base_threshold=0.50)
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # GENERIC DOMAIN TEMPLATES - Framework for Customization
    # ═══════════════════════════════════════════════════════════════════
    
    GENERIC_DOMAIN_TEMPLATES: ClassVar[Dict[str, DomainProfile]] = {
        # CONFRONTATION & CONFLICT
        'confronting_someone': DomainProfile(
            name='confronting_someone',
            base_threshold=0.45,
            triggers=['confront', 'call out', 'challenge', 'disagree', 'oppose'],
            affect_modifiers={'RAGE': 0.20, 'CARE': 0.15, 'FEAR': 0.15}
        ),
        'admitting_mistakes': DomainProfile(
            name='admitting_mistakes',
            base_threshold=0.55,
            triggers=['admit', 'mistake', 'wrong', 'fault', 'responsible', 'sorry'],
            affect_modifiers={'CARE': 0.25, 'FEAR': 0.20, 'PANIC': -0.15}
        ),
        'asking_for_help': DomainProfile(
            name='asking_for_help',
            base_threshold=0.50,
            triggers=['help', 'need', 'ask', 'support', 'cant do', 'struggling'],
            affect_modifiers={'CARE': 0.20, 'FEAR': 0.15, 'PANIC': -0.10}
        ),
        'saying_no': DomainProfile(
            name='saying_no',
            base_threshold=0.50,
            triggers=['no', 'decline', 'refuse', 'reject', 'boundary', 'turn down'],
            affect_modifiers={'RAGE': 0.15, 'CARE': 0.15, 'FEAR': 0.10}
        ),
        
        # EMOTIONAL RISK
        'expressing_love': DomainProfile(
            name='expressing_love',
            base_threshold=0.45,
            triggers=['love', 'feelings', 'like', 'crush', 'romantic', 'heart'],
            affect_modifiers={'LUST': 0.25, 'CARE': 0.20, 'FEAR': 0.20, 'PANIC': -0.20}
        ),
        'sharing_insecurities': DomainProfile(
            name='sharing_insecurities',
            base_threshold=0.55,
            triggers=['insecure', 'doubt', 'not good enough', 'failure', 'imposter'],
            affect_modifiers={'CARE': 0.25, 'FEAR': 0.25, 'PANIC': -0.15}
        ),
        'grief_expression': DomainProfile(
            name='grief_expression',
            base_threshold=0.60,
            triggers=['grief', 'loss', 'died', 'miss', 'sad', 'cry', 'mourning'],
            affect_modifiers={'PANIC': 0.20, 'CARE': 0.25, 'FEAR': 0.10}
        ),
        
        # MORAL & ETHICAL
        'whistleblowing': DomainProfile(
            name='whistleblowing',
            base_threshold=0.35,
            triggers=['whistleblow', 'report', 'illegal', 'corruption', 'fraud'],
            affect_modifiers={'CARE': 0.30, 'RAGE': 0.25, 'FEAR': 0.20, 'PANIC': -0.20}
        ),
        'defending_others': DomainProfile(
            name='defending_others',
            base_threshold=0.40,
            triggers=['defend', 'protect', 'bully', 'stand up for', 'advocate'],
            affect_modifiers={'CARE': 0.35, 'RAGE': 0.20, 'FEAR': 0.10}
        ),
        'admitting_ignorance': DomainProfile(
            name='admitting_ignorance',
            base_threshold=0.50,
            triggers=['dont know', 'learn', 'understand', 'explain', 'teach'],
            affect_modifiers={'SEEKING': 0.20, 'CARE': 0.15, 'FEAR': 0.10}
        ),
        
        # CAREER & PROFESSIONAL
        'career_changes': DomainProfile(
            name='career_changes',
            base_threshold=0.50,
            triggers=['quit', 'job', 'career', 'change', 'resign', 'new work'],
            affect_modifiers={'SEEKING': 0.20, 'FEAR': 0.20, 'LUST': 0.10}
        ),
        'salary_negotiation': DomainProfile(
            name='salary_negotiation',
            base_threshold=0.55,
            triggers=['salary', 'raise', 'pay', 'negotiate', 'worth', 'money'],
            affect_modifiers={'RAGE': 0.15, 'FEAR': 0.15, 'CARE': 0.10}
        ),
        'public_speaking_courage': DomainProfile(
            name='public_speaking_courage',
            base_threshold=0.50,
            triggers=['speak', 'presentation', 'audience', 'stage', 'talk', 'speech'],
            affect_modifiers={'FEAR': 0.25, 'SEEKING': 0.15, 'PLAY': 0.10}
        ),
        'starting_business': DomainProfile(
            name='starting_business',
            base_threshold=0.45,
            triggers=['startup', 'business', 'entrepreneur', 'founder', 'risk'],
            affect_modifiers={'SEEKING': 0.25, 'LUST': 0.20, 'FEAR': 0.15}
        ),
        
        # PERSONAL GROWTH
        'ending_relationships': DomainProfile(
            name='ending_relationships',
            base_threshold=0.45,
            triggers=['break up', 'end', 'leave', 'divorce', 'split', 'move on'],
            affect_modifiers={'CARE': 0.25, 'FEAR': 0.20, 'RAGE': 0.15}
        ),
        'setting_boundaries': DomainProfile(
            name='setting_boundaries',
            base_threshold=0.50,
            triggers=['boundary', 'limit', 'space', 'respect', 'unacceptable'],
            affect_modifiers={'RAGE': 0.20, 'CARE': 0.20, 'FEAR': 0.10}
        ),
        'therapy_counseling': DomainProfile(
            name='therapy_counseling',
            base_threshold=0.55,
            triggers=['therapy', 'counselor', 'mental health', 'psychologist', 'help'],
            affect_modifiers={'CARE': 0.25, 'FEAR': 0.20, 'PANIC': -0.10}
        ),
        
        # HEALTH & SAFETY
        'medical_procedures': DomainProfile(
            name='medical_procedures',
            base_threshold=0.60,
            triggers=['surgery', 'procedure', 'hospital', 'doctor', 'treatment'],
            affect_modifiers={'FEAR': 0.30, 'CARE': 0.20, 'PANIC': -0.15}
        ),
        'addiction_recovery': DomainProfile(
            name='addiction_recovery',
            base_threshold=0.55,
            triggers=['sober', 'addiction', 'recovery', 'habit', 'substance', 'quit'],
            affect_modifiers={'CARE': 0.30, 'FEAR': 0.15, 'RAGE': 0.15}
        ),
        
        # CREATIVE RISK
        'publishing_work': DomainProfile(
            name='publishing_work',
            base_threshold=0.50,
            triggers=['publish', 'release', 'share work', 'post', 'submit', 'launch'],
            affect_modifiers={'FEAR': 0.25, 'SEEKING': 0.15, 'PLAY': 0.10}
        ),
        'artistic_expression': DomainProfile(
            name='artistic_expression',
            base_threshold=0.45,
            triggers=['art', 'create', 'show', 'exhibit', 'perform', 'dance'],
            affect_modifiers={'PLAY': 0.20, 'FEAR': 0.20, 'LUST': 0.15}
        ),
        
        # SOCIAL RISK
        'meeting_new_people': DomainProfile(
            name='meeting_new_people',
            base_threshold=0.50,
            triggers=['stranger', 'new people', 'introduce', 'network', 'party'],
            affect_modifiers={'FEAR': 0.20, 'SEEKING': 0.15, 'PLAY': 0.15}
        ),
        'apologizing': DomainProfile(
            name='apologizing',
            base_threshold=0.55,
            triggers=['apologize', 'sorry', 'forgive', 'make amends', 'regret'],
            affect_modifiers={'CARE': 0.30, 'FEAR': 0.20, 'RAGE': -0.10}
        ),
        'forgiving': DomainProfile(
            name='forgiving',
            base_threshold=0.60,
            triggers=['forgive', 'let go', 'resentment', 'grudge', 'move on'],
            affect_modifiers={'CARE': 0.35, 'RAGE': -0.20, 'FEAR': 0.10}
        ),
    }
    
    # Activation signals for auto-detection
    ACTIVATION_SIGNALS: ClassVar[Dict[str, str]] = {
        'fear_language': r'\b(scared|afraid|nervous|anxious|worried|terrified)\b',
        'avoidance': r'\b(avoid|hide|ignore|pretend|not think about)\b',
        'should_do': r'\b(should|need to|have to|must|supposed to)\b',
        'importance': r'\b(matter|important|care|love|value|worth)\b',
        'difficulty': r'\b(hard|difficult|tough|challenging|scary)\b',
        'procrastination': r'\b(put off|delay|later|someday|eventually)\b',
        'regret': r'\b(regret|wish I had|if only|missed chance)\b',
        'peer_pressure': r'\b(everyone else|they want|expectation|disappoint)\b'
    }
    
    def __init__(self, affective_core=None, data_dir: Optional[str] = None):
        """Initialize COURAGE Engine."""
        self.affective_core = affective_core
        self.data_dir = Path(data_dir) if data_dir else Path.home() / '.nima' / 'courage_data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.domains: Dict[str, DomainProfile] = {}
        self._load_default_domains()
        
        self.user_preference = 0.5
        self.recent_interactions: List[Dict] = []
        
        self._load_user_data()
        
        logger.info(f"COURAGE Engine initialized with {len(self.domains)} domains")
    
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
        logger.info(f"Loaded COURAGE domain template: {template_name} as '{name}'")
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
        """Get current affective state from AffectiveCore."""
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
                    'fear_language': 0.35,
                    'importance': 0.30,
                    'avoidance': 0.25,
                    'difficulty': 0.20,
                    'should_do': 0.25,
                    'procrastination': 0.20,
                    'regret': 0.30,
                    'peer_pressure': 0.15
                }
                score += weights.get(signal_name, 0.15)
                reasons.append(signal_name)
        
        if self.user_preference > 0.6:
            score += 0.15
            reasons.append('historical_preference')
        
        return min(1.0, score), reasons
    
    def analyze_message(self, message: str, context: Optional[Dict] = None) -> CourageAnalysis:
        """Main entry point: Analyze message and calculate COURAGE level."""
        # Input validation
        if not message or not isinstance(message, str):
            logger.warning(f"Invalid message provided to COURAGE engine: {message}")
            return self._default_analysis()
        
        if len(message.strip()) == 0:
            logger.warning("Empty message provided to COURAGE engine")
            return self._default_analysis()
        
        context = context or {}
        
        domain = self.detect_domain(message, context)
        domain_profile = self.domains.get(domain, self.domains['default'])
        
        affect_state = self.get_affect_state()
        
        # Extract key levels
        fear_level = affect_state.get('FEAR', 0.3)
        care_level = affect_state.get('CARE', 0.3)
        panic_level = affect_state.get('PANIC', 0.0)
        
        # COURAGE requires fear (otherwise it's not courage)
        # No fear = 0 courage (it's just action)
        if fear_level < 0.2:
            return CourageAnalysis(
                level=0.0,
                style=ResponseStyle.AVOIDANT,
                domain=domain,
                confidence=0.5,
                activation_reasons=['no_fear_detected'],
                affect_contributions={'FEAR': fear_level},
                fear_level=fear_level,
                importance_level=care_level
            )
        
        # Calculate importance (why it matters despite fear)
        importance = (care_level * 0.5 + 
                     affect_state.get('SEEKING', 0.3) * 0.3 +
                     affect_state.get('LUST', 0.3) * 0.2)
        
        # Calculate base courage from formula
        courage_level = 0.0
        affect_contributions = {}
        
        for affect, weight in self.COURAGE_FORMULA.items():
            intensity = affect_state.get(affect, 0.3)
            contribution = intensity * weight
            courage_level += contribution
            affect_contributions[affect] = contribution
        
        # Normalize
        courage_level = (courage_level + 0.5) / 1.5
        courage_level = max(0.0, min(1.0, courage_level))
        
        # Apply domain threshold
        base_threshold = domain_profile.adjusted_threshold
        
        if courage_level < base_threshold:
            courage_level = courage_level * 0.8
        else:
            courage_level = courage_level * 1.1
            courage_level = min(1.0, courage_level)
        
        # Apply domain modifiers
        for affect, modifier in domain_profile.affect_modifiers.items():
            if affect in affect_state:
                courage_level += affect_state[affect] * modifier * 0.2
        
        # Calculate activation
        activation_score, activation_reasons = self.calculate_activation_score(message)
        courage_level += activation_score * 0.3
        
        # Apply user preference
        courage_level += (self.user_preference - 0.5) * 0.2
        
        courage_level = max(0.0, min(1.0, courage_level))
        
        # Determine style
        if courage_level < 0.25:
            style = ResponseStyle.AVOIDANT
        elif courage_level < 0.50:
            style = ResponseStyle.CAUTIOUS
        elif courage_level < 0.70:
            style = ResponseStyle.ENCOURAGING
        elif courage_level < 0.90:
            style = ResponseStyle.BOLD
        else:
            style = ResponseStyle.FEARLESS
        
        # Calculate confidence
        if domain_profile.attempts < 3:
            confidence = 0.6
        else:
            confidence = max(0.3, min(0.95, domain_profile.success_rate))
        
        return CourageAnalysis(
            level=courage_level,
            style=style,
            domain=domain,
            confidence=confidence,
            activation_reasons=activation_reasons,
            affect_contributions=affect_contributions,
            fear_level=fear_level,
            importance_level=importance
        )
    
    def record_outcome(self, analysis: CourageAnalysis, success: bool,
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
        user_data_path = self.data_dir / 'user_courage_profile.json'
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
                logger.warning("Could not load user COURAGE data: %s", e, exc_info=True)
    
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
            
            user_data_path = self.data_dir / 'user_courage_profile.json'
            with open(user_data_path, 'w') as f:
                json.dump(data, f, indent=2)
        except (OSError, TypeError) as e:
            logger.warning("Could not save user COURAGE data: %s", e, exc_info=True)
    
    def _default_analysis(self) -> CourageAnalysis:
        """Return default analysis for invalid/empty messages."""
        return CourageAnalysis(
            level=0.0,
            style=ResponseStyle.AVOIDANT,
            domain='default',
            confidence=0.0,
            activation_reasons=[],
            affect_contributions={affect: 0.0 for affect in self.COURAGE_FORMULA.keys()},
            fear_level=0.0,
            importance_level=0.0
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get COURAGE statistics."""
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