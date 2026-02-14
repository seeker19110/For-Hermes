#!/usr/bin/env python3
"""
DARING Engine — Variable Response Modulation System
====================================================
Integrates with NIMA Core's Affective Layer to provide variable DARING levels.

"DARING is not recklessness. It is confident directness based on learned patterns."

Architecture:
- Reads from AffectiveCore (Layer 1: Panksepp 7 affects)
- Calculates composite DARING level (Layer 2)
- Adjusts based on domain-specific success history
- Provides real-time response style modulation

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
    """DARING response styles from 0.0 (suggestive) to 1.0 (absolute)."""
    SUGGESTIVE = "suggestive"      # 0.0-0.25: "Here are options..."
    BALANCED = "balanced"          # 0.25-0.50: "I recommend..."
    DARING = "daring"              # 0.50-0.70: "Here's what we're doing..."
    HIGH_DARING = "high_daring"    # 0.70-0.90: "YES. Executing..."
    FULL_DARING = "full_daring"    # 0.90-1.0: Pure execution


@dataclass
class DomainProfile:
    """User-defined domain with learned DARING parameters."""
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
        # Success pushes threshold down (more daring)
        # Failure pushes threshold up (more cautious)
        adjustment = (self.success_rate - 0.5) * 0.2
        return max(0.1, min(0.9, self.base_threshold - adjustment))


@dataclass
class DaringAnalysis:
    """Complete DARING analysis result."""
    level: float                      # 0.0 to 1.0
    style: ResponseStyle
    domain: str
    confidence: float
    activation_reasons: List[str]
    affect_contributions: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'level': round(self.level, 3),
            'style': self.style.value,
            'domain': self.domain,
            'confidence': round(self.confidence, 3),
            'activation_reasons': self.activation_reasons,
            'affect_contributions': {k: round(v, 3) for k, v in self.affect_contributions.items()}
        }


class DaringEngine:
    """
    Variable DARING response system integrated with NIMA Core.
    
    Reads real-time affective state and calculates appropriate
    DARING level for response generation.
    
    Usage:
        daring = DaringEngine(nima_core.affective_core)
        analysis = daring.analyze_message("Go full blast!", context)
        # analysis.level = 0.85, analysis.style = ResponseStyle.HIGH_DARING
    """
    
    # Layer 1: Foundation affects (Panksepp 7)
    FOUNDATION_AFFECTS: ClassVar[List[str]] = ['SEEKING', 'RAGE', 'FEAR', 'LUST', 'CARE', 'PANIC', 'PLAY']
    
    # Affect contributions to DARING (Layer 2 composite formula)
    DARING_FORMULA: ClassVar[Dict[str, float]] = {
        'SEEKING': 0.35,      # High seeking = more daring
        'PLAY': 0.25,         # Playful mood = experimental
        'RAGE': 0.15,         # Frustration = decisive action
        'CARE': 0.15,         # Protective = domain-dependent
        'LUST': 0.10,         # Desire = pursuit
        'FEAR': -0.30,        # Fear = risk aversion
        'PANIC': -0.45,       # Panic = emergency caution
    }
    
    # Default domain configurations (built-in)
    DEFAULT_DOMAINS: ClassVar[Dict[str, DomainProfile]] = {
        'family_protection': DomainProfile(
            name='family_protection',
            base_threshold=0.36,
            triggers=['family', 'kids', 'children', 'spouse', 'protect', 'safety', 'loved ones'],
            affect_modifiers={'CARE': 0.25, 'FEAR': 0.10}
        ),
        'theological_synthesis': DomainProfile(
            name='theological_synthesis',
            base_threshold=0.40,
            triggers=['theology', 'bible', 'faith', 'spiritual', 'church', 'scripture', 'god', 'religion'],
            affect_modifiers={'SEEKING': 0.15, 'CARE': 0.10}
        ),
        'creative_building': DomainProfile(
            name='creative_building',
            base_threshold=0.45,
            triggers=['create', 'build', 'design', 'make', 'implement', 'enhance', 'creative'],
            affect_modifiers={'PLAY': 0.20, 'SEEKING': 0.15}
        ),
        'research_deep_dives': DomainProfile(
            name='research_deep_dives',
            base_threshold=0.55,
            triggers=['research', 'analyze', 'investigate', 'study', 'deep dive', 'explore'],
            affect_modifiers={'SEEKING': 0.20}
        ),
        'code_architecture': DomainProfile(
            name='code_architecture',
            base_threshold=0.65,
            triggers=['code', 'architect', 'system', 'structure', 'refactor', 'debug'],
            affect_modifiers={'RAGE': -0.05}  # Frustration makes code more cautious
        ),
        'default': DomainProfile(name='default', base_threshold=0.50)
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # GENERIC DOMAIN TEMPLATES - Framework for Customization
    # ═══════════════════════════════════════════════════════════════════
    #
    # Use these templates as starting points for your own domains.
    # Copy, modify thresholds and modifiers to match your needs.
    #
    # Threshold Guidelines:
    #   0.30-0.40: High-stakes protection (family, crisis, safety)
    #   0.40-0.50: Creative/exploratory work (building, brainstorming)
    #   0.50-0.60: Analytical/research tasks (analysis, planning)
    #   0.60-0.70: Technical precision (code, architecture)
    #   0.70-0.80: High-risk operations (production, financial)
    #
    # Modifier Guidelines:
    #   Positive (+): Increase DARING when affect is high
    #   Negative (-): Decrease DARING when affect is high
    #   Range: -0.30 to +0.30 per affect
    
    GENERIC_DOMAIN_TEMPLATES: ClassVar[Dict[str, DomainProfile]] = {
        # SAFETY & PROTECTION (High stakes, protective)
        'personal_security': DomainProfile(
            name='personal_security',
            base_threshold=0.40,
            triggers=['security', 'password', 'privacy', 'hack', 'threat', 'breach'],
            affect_modifiers={'FEAR': 0.20, 'PANIC': 0.10, 'CARE': 0.15}
        ),
        'crisis_management': DomainProfile(
            name='crisis_management',
            base_threshold=0.35,
            triggers=['crisis', 'emergency', 'disaster', 'incident', 'urgent'],
            affect_modifiers={'PANIC': 0.20, 'FEAR': 0.15, 'CARE': 0.20}
        ),
        'incident_response': DomainProfile(
            name='incident_response',
            base_threshold=0.30,
            triggers=['incident', 'outage', 'down', 'broken', 'critical', 'fire'],
            affect_modifiers={'PANIC': 0.25, 'FEAR': 0.20, 'RAGE': 0.10}
        ),
        
        # CREATIVE WORK (Exploratory, playful)
        'content_creation': DomainProfile(
            name='content_creation',
            base_threshold=0.50,
            triggers=['content', 'blog', 'video', 'media', 'marketing', 'copy'],
            affect_modifiers={'PLAY': 0.15, 'LUST': 0.10, 'SEEKING': 0.10}
        ),
        'brainstorming': DomainProfile(
            name='brainstorming',
            base_threshold=0.40,
            triggers=['ideas', 'brainstorm', 'innovate', 'imagine', 'concept'],
            affect_modifiers={'PLAY': 0.25, 'SEEKING': 0.20, 'FEAR': -0.10}
        ),
        'design_work': DomainProfile(
            name='design_work',
            base_threshold=0.45,
            triggers=['design', 'ui', 'ux', 'visual', 'aesthetic', 'layout'],
            affect_modifiers={'PLAY': 0.20, 'CARE': 0.15, 'SEEKING': 0.10}
        ),
        
        # TECHNICAL TASKS (Precision, careful)
        'devops_deploy': DomainProfile(
            name='devops_deploy',
            base_threshold=0.70,
            triggers=['deploy', 'production', 'release', 'server', 'infrastructure'],
            affect_modifiers={'FEAR': 0.15, 'CARE': 0.20, 'PANIC': 0.10}
        ),
        'data_analysis': DomainProfile(
            name='data_analysis',
            base_threshold=0.55,
            triggers=['data', 'analyze', 'metrics', 'report', 'statistics', 'chart'],
            affect_modifiers={'SEEKING': 0.10, 'CARE': 0.10}
        ),
        'testing_qa': DomainProfile(
            name='testing_qa',
            base_threshold=0.60,
            triggers=['test', 'qa', 'bug', 'quality', 'verify', 'validate'],
            affect_modifiers={'CARE': 0.20, 'FEAR': 0.10}
        ),
        'database_migrations': DomainProfile(
            name='database_migrations',
            base_threshold=0.75,
            triggers=['migration', 'database', 'schema', 'postgres', 'mysql', 'sql'],
            affect_modifiers={'FEAR': 0.25, 'CARE': 0.20, 'PANIC': 0.10, 'PLAY': -0.15}
        ),
        
        # RESEARCH & LEARNING (Analytical, curious)
        'academic_work': DomainProfile(
            name='academic_work',
            base_threshold=0.60,
            triggers=['paper', 'thesis', 'citation', 'academic', 'publish', 'journal'],
            affect_modifiers={'CARE': 0.10, 'SEEKING': 0.10}
        ),
        'documentation': DomainProfile(
            name='documentation',
            base_threshold=0.50,
            triggers=['docs', 'documentation', 'readme', 'wiki', 'manual', 'guide'],
            affect_modifiers={'CARE': 0.15, 'SEEKING': 0.05}
        ),
        'learning_new_skill': DomainProfile(
            name='learning_new_skill',
            base_threshold=0.45,
            triggers=['learn', 'skill', 'tutorial', 'course', 'practice', 'training'],
            affect_modifiers={'SEEKING': 0.20, 'PLAY': 0.15, 'FEAR': -0.10}
        ),
        
        # BUSINESS & STRATEGY (Strategic, calculated)
        'strategic_planning': DomainProfile(
            name='strategic_planning',
            base_threshold=0.60,
            triggers=['strategy', 'plan', 'roadmap', 'vision', 'goal', 'mission'],
            affect_modifiers={'SEEKING': 0.15, 'FEAR': 0.10, 'CARE': 0.10}
        ),
        'client_projects': DomainProfile(
            name='client_projects',
            base_threshold=0.55,
            triggers=['client', 'deliverable', 'deadline', 'stakeholder', 'contract'],
            affect_modifiers={'FEAR': 0.15, 'CARE': 0.10, 'SEEKING': 0.05}
        ),
        'financial_decisions': DomainProfile(
            name='financial_decisions',
            base_threshold=0.70,
            triggers=['money', 'budget', 'cost', 'revenue', 'financial', 'invest', 'fund'],
            affect_modifiers={'FEAR': 0.25, 'PANIC': 0.15, 'CARE': 0.15}
        ),
        'negotiation': DomainProfile(
            name='negotiation',
            base_threshold=0.50,
            triggers=['negotiate', 'deal', 'contract', 'agreement', 'terms', 'price'],
            affect_modifiers={'RAGE': 0.10, 'CARE': 0.10, 'SEEKING': 0.10}
        ),
        'startup_pivot': DomainProfile(
            name='startup_pivot',
            base_threshold=0.40,
            triggers=['pivot', 'startup', 'direction', 'change course', 'strategy shift'],
            affect_modifiers={'SEEKING': 0.25, 'RAGE': 0.10, 'FEAR': -0.10}
        ),
        
        # PERSONAL & SOCIAL (Emotional, caring)
        'relationship_advice': DomainProfile(
            name='relationship_advice',
            base_threshold=0.45,
            triggers=['relationship', 'partner', 'friend', 'conflict', 'love', 'dating'],
            affect_modifiers={'CARE': 0.25, 'FEAR': 0.10, 'LUST': 0.10}
        ),
        'health_wellness': DomainProfile(
            name='health_wellness',
            base_threshold=0.50,
            triggers=['health', 'workout', 'diet', 'mental', 'therapy', 'medical'],
            affect_modifiers={'CARE': 0.20, 'FEAR': 0.10, 'SEEKING': 0.05}
        ),
        'life_planning': DomainProfile(
            name='life_planning',
            base_threshold=0.55,
            triggers=['career', 'future', 'move', 'change', 'decision', 'path'],
            affect_modifiers={'SEEKING': 0.15, 'FEAR': 0.10, 'CARE': 0.10}
        ),
        'parenting': DomainProfile(
            name='parenting',
            base_threshold=0.40,
            triggers=['parent', 'child', 'kid', 'raise', 'teach', 'discipline'],
            affect_modifiers={'CARE': 0.30, 'FEAR': 0.10, 'PLAY': 0.15}
        ),
        
        # COMMUNICATION (Social, performative)
        'public_speaking': DomainProfile(
            name='public_speaking',
            base_threshold=0.45,
            triggers=['presentation', 'speech', 'audience', 'talk', 'pitch', 'stage'],
            affect_modifiers={'FEAR': 0.20, 'PLAY': 0.10, 'CARE': 0.10}
        ),
        'difficult_conversations': DomainProfile(
            name='difficult_conversations',
            base_threshold=0.50,
            triggers=['confrontation', 'feedback', 'criticism', 'firing', 'breakup'],
            affect_modifiers={'FEAR': 0.15, 'CARE': 0.15, 'RAGE': -0.05}
        ),
        'networking': DomainProfile(
            name='networking',
            base_threshold=0.40,
            triggers=['network', 'connect', 'introduce', 'social', 'event', 'meet'],
            affect_modifiers={'PLAY': 0.15, 'SEEKING': 0.10, 'LUST': 0.05}
        ),
        'interview_prep': DomainProfile(
            name='interview_prep',
            base_threshold=0.50,
            triggers=['interview', 'job', 'hire', 'candidate', 'resume', 'apply'],
            affect_modifiers={'SEEKING': 0.15, 'FEAR': 0.10, 'CARE': 0.10}
        ),
        
        # WRITING & COMMUNICATION (Creative but precise)
        'creative_writing': DomainProfile(
            name='creative_writing',
            base_threshold=0.45,
            triggers=['write', 'story', 'novel', 'fiction', 'poem', 'creative'],
            affect_modifiers={'PLAY': 0.20, 'SEEKING': 0.15, 'CARE': 0.10}
        ),
        'technical_writing': DomainProfile(
            name='technical_writing',
            base_threshold=0.55,
            triggers=['technical', 'spec', 'api', 'reference', 'manual'],
            affect_modifiers={'CARE': 0.20, 'SEEKING': 0.05}
        ),
        'email_communication': DomainProfile(
            name='email_communication',
            base_threshold=0.50,
            triggers=['email', 'message', 'reply', 'respond', 'inbox'],
            affect_modifiers={'CARE': 0.15, 'FEAR': 0.05}
        ),
        
        # PROJECT MANAGEMENT (Organizational)
        'project_management': DomainProfile(
            name='project_management',
            base_threshold=0.55,
            triggers=['project', 'manage', 'timeline', 'milestone', 'scrum', 'agile'],
            affect_modifiers={'CARE': 0.15, 'SEEKING': 0.10, 'RAGE': 0.05}
        ),
        'team_leadership': DomainProfile(
            name='team_leadership',
            base_threshold=0.50,
            triggers=['team', 'lead', 'manage people', 'delegate', 'hire', 'fire'],
            affect_modifiers={'CARE': 0.20, 'RAGE': 0.10, 'SEEKING': 0.10}
        ),
        'event_planning': DomainProfile(
            name='event_planning',
            base_threshold=0.50,
            triggers=['event', 'plan', 'party', 'conference', 'wedding', 'logistics'],
            affect_modifiers={'CARE': 0.20, 'PLAY': 0.10, 'FEAR': 0.10}
        ),
        
        # LEGAL & COMPLIANCE (High caution)
        'legal_matters': DomainProfile(
            name='legal_matters',
            base_threshold=0.75,
            triggers=['legal', 'law', 'contract', 'sue', 'lawyer', 'compliance', 'regulation'],
            affect_modifiers={'FEAR': 0.25, 'CARE': 0.25, 'PANIC': 0.15}
        ),
        'compliance_audit': DomainProfile(
            name='compliance_audit',
            base_threshold=0.70,
            triggers=['compliance', 'audit', 'regulation', 'policy', 'gdpr', 'hipaa'],
            affect_modifiers={'FEAR': 0.20, 'CARE': 0.20, 'SEEKING': 0.05}
        ),
    }
    # ═══════════════════════════════════════════════════════════════════
    
    # Activation signals for auto-detection
    ACTIVATION_SIGNALS: ClassVar[Dict[str, str]] = {
        'high_energy': r'[!🚀🔥💪⚡✨💥🎯⭐]{2,}|[A-Z]{5,}',
        'delegation': r'\b(go ahead|do what you|your call|up to you|you decide|your choice)\b',
        'permission': r'\b(full control|have at it|do your thing|make it happen|full blast)\b',
        'urgency': r'\b(urgent|asap|quick|fast|now|immediately|hurry|rush)\b',
        'decisiveness': r'\b(just do|execute|implement|build it|ship it|deploy|go)\b',
        'excitement': r'\b(excited|pumped|stoked|awesome|amazing|love it|perfect|great)\b',
        'frustration': r'\b(tired of|sick of|frustrated|annoying|waste of|done with)\b',
        'trust': r'\b(trust you|know you|rely on you|count on you|believe in you)\b'
    }
    
    def __init__(self, affective_core=None, data_dir: Optional[str] = None):
        """
        Initialize DARING Engine.
        
        Args:
            affective_core: Reference to SubcorticalAffectiveCore for real-time state
            data_dir: Directory to store user learning data
        """
        self.affective_core = affective_core
        self.data_dir = Path(data_dir) if data_dir else Path.home() / '.nima' / 'daring_data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Domain registry (user can add custom domains)
        self.domains: Dict[str, DomainProfile] = {}
        self._load_default_domains()
        
        # User learning data
        self.user_preference = 0.5  # Global daring preference (learned)
        self.recent_interactions: List[Dict] = []
        
        # Load persisted data
        self._load_user_data()
        
        logger.info(f"DARING Engine initialized with {len(self.domains)} domains")
    
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
    
    def load_template_domain(self, template_name: str, custom_name: Optional[str] = None) -> DomainProfile:
        """
        Load a generic domain template and add it to active domains.
        
        Use this to quickly enable pre-configured domain templates from
        GENERIC_DOMAIN_TEMPLATES. You can optionally rename the domain.
        
        Args:
            template_name: Name of template from GENERIC_DOMAIN_TEMPLATES
            custom_name: Optional custom name (defaults to template_name)
            
        Returns:
            Loaded DomainProfile
            
        Example:
            daring = DaringEngine()
            daring.load_template_domain('database_migrations')
            daring.load_template_domain('content_creation', 'my_marketing')
        """
        if template_name not in self.GENERIC_DOMAIN_TEMPLATES:
            available = list(self.GENERIC_DOMAIN_TEMPLATES.keys())
            raise ValueError(f"Unknown template '{template_name}'. Available: {available}")
        
        template = self.GENERIC_DOMAIN_TEMPLATES[template_name]
        
        # Create a copy with optional custom name
        name = custom_name or template_name
        profile = DomainProfile(
            name=name,
            base_threshold=template.base_threshold,
            triggers=template.triggers.copy(),
            affect_modifiers=template.affect_modifiers.copy()
        )
        
        self.domains[name] = profile
        logger.info(f"Loaded domain template: {template_name} as '{name}'")
        return profile
    
    def list_available_templates(self) -> Dict[str, Dict]:
        """
        List all available generic domain templates.
        
        Returns:
            Dict mapping template names to their configurations
        """
        templates = {}
        for name, profile in self.GENERIC_DOMAIN_TEMPLATES.items():
            templates[name] = {
                'base_threshold': profile.base_threshold,
                'triggers': profile.triggers,
                'affect_modifiers': profile.affect_modifiers,
                'category': self._get_template_category(name)
            }
        return templates
    
    def _get_template_category(self, template_name: str) -> str:
        """Helper to categorize templates by name."""
        categories = {
            'safety': ['personal_security', 'crisis_management', 'incident_response'],
            'creative': ['content_creation', 'brainstorming', 'design_work', 'creative_writing'],
            'technical': ['devops_deploy', 'data_analysis', 'testing_qa', 'database_migrations'],
            'research': ['academic_work', 'documentation', 'learning_new_skill', 'technical_writing'],
            'business': ['strategic_planning', 'client_projects', 'financial_decisions', 'negotiation', 'startup_pivot'],
            'personal': ['relationship_advice', 'health_wellness', 'life_planning', 'parenting'],
            'communication': ['public_speaking', 'difficult_conversations', 'networking', 'interview_prep', 'email_communication'],
            'management': ['project_management', 'team_leadership', 'event_planning'],
            'legal': ['legal_matters', 'compliance_audit']
        }
        
        for category, templates in categories.items():
            if template_name in templates:
                return category
        return 'other'
    
    def show_customization_guide(self) -> str:
        """
        Returns a guide for creating custom domains.
        
        Returns:
            Formatted guide string
        """
        guide = """
╔══════════════════════════════════════════════════════════════════╗
║           DARING Domain Customization Guide                       ║
╚══════════════════════════════════════════════════════════════════╝

1. CHOOSE A BASE THRESHOLD
   ━━━━━━━━━━━━━━━━━━━━━━━━
   0.30-0.40: High-stakes protection (family, crisis, safety)
   0.40-0.50: Creative/exploratory work (building, brainstorming)
   0.50-0.60: Analytical/research tasks (analysis, planning)
   0.60-0.70: Technical precision (code, architecture)
   0.70-0.80: High-risk operations (production, financial)

2. DEFINE TRIGGERS
   ━━━━━━━━━━━━━━━
   List keywords that indicate this domain:
   triggers=['database', 'migration', 'schema', 'postgres']

3. SET AFFECT MODIFIERS
   ━━━━━━━━━━━━━━━━━━━━━
   Positive (+): Increase DARING when affect is high
   Negative (-): Decrease DARING when affect is high
   
   Available affects: SEEKING, PLAY, RAGE, CARE, LUST, FEAR, PANIC
   
   Example: FEAR +0.20 increases caution when afraid
            PLAY +0.20 increases daring when joyful

4. REGISTER YOUR DOMAIN
   ━━━━━━━━━━━━━━━━━━━━━
   nima.daring_register_domain(
       name="my_custom_domain",
       base_threshold=0.55,
       triggers=['keyword1', 'keyword2'],
       affect_modifiers={'SEEKING': 0.15, 'FEAR': -0.10}
   )

5. OR LOAD A TEMPLATE
   ━━━━━━━━━━━━━━━━━━
   nima._daring.load_template_domain('database_migrations')
   
   Available templates:
   - crisis_management, incident_response (Safety)
   - creative_building, content_creation, brainstorming (Creative)
   - code_architecture, devops_deploy, database_migrations (Technical)
   - research_deep_dives, academic_work, documentation (Research)
   - strategic_planning, financial_decisions, negotiation (Business)
   - relationship_advice, health_wellness, parenting (Personal)
   - public_speaking, difficult_conversations, networking (Communication)
   - project_management, team_leadership (Management)
   - legal_matters, compliance_audit (Legal)

For full template list:
   templates = nima._daring.list_available_templates()
"""
        return guide
    
    def _load_user_data(self):
        """Load user learning data from disk."""
        user_data_path = self.data_dir / 'user_daring_profile.json'
        if user_data_path.exists():
            try:
                with open(user_data_path, 'r') as f:
                    data = json.load(f)
                
                self.user_preference = data.get('user_preference', 0.5)
                
                # Load domain histories
                for domain_name, domain_data in data.get('domains', {}).items():
                    if domain_name in self.domains:
                        self.domains[domain_name].attempts = domain_data.get('attempts', 0)
                        self.domains[domain_name].successes = domain_data.get('successes', 0)
                
                logger.info(f"Loaded DARING user data: preference={self.user_preference:.2f}")
            except (OSError, json.JSONDecodeError) as e:
                logger.warning("Could not load user DARING data: %s", e, exc_info=True)
    
    def _save_user_data(self):
        """Persist user learning data."""
        try:
            data = {
                'user_preference': self.user_preference,
                'domains': {
                    name: {
                        'attempts': profile.attempts,
                        'successes': profile.successes,
                        'success_rate': profile.success_rate
                    }
                    for name, profile in self.domains.items()
                },
                'last_updated': time.time()
            }
            
            user_data_path = self.data_dir / 'user_daring_profile.json'
            with open(user_data_path, 'w') as f:
                json.dump(data, f, indent=2)
        except (OSError, TypeError) as e:
            logger.warning("Could not save user DARING data: %s", e, exc_info=True)
    
    def _default_analysis(self) -> DaringAnalysis:
        """Return default analysis for invalid/empty messages."""
        return DaringAnalysis(
            level=0.0,
            style=ResponseStyle.BALANCED,
            domain='default',
            confidence=0.0,
            activation_reasons=[],
            affect_contributions={affect: 0.0 for affect in self.DARING_FORMULA.keys()}
        )
    
    def register_domain(self, name: str, base_threshold: float = 0.50,
                       triggers: Optional[List[str]] = None,
                       affect_modifiers: Optional[Dict[str, float]] = None) -> DomainProfile:
        """
        Register a custom domain with DARING parameters.
        
        Args:
            name: Domain identifier
            base_threshold: Starting DARING threshold (0-1)
            triggers: Keywords that indicate this domain
            affect_modifiers: Affect intensity modifiers for this domain
            
        Returns:
            Created DomainProfile
        """
        profile = DomainProfile(
            name=name,
            base_threshold=base_threshold,
            triggers=triggers or [],
            affect_modifiers=affect_modifiers or {}
        )
        self.domains[name] = profile
        logger.info(f"Registered DARING domain: {name} (threshold={base_threshold})")
        return profile
    
    def detect_domain(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Detect which domain a message belongs to.
        
        Args:
            message: User message
            context: Additional context (files, history, etc.)
            
        Returns:
            Domain name
        """
        message_lower = message.lower()
        context = context or {}
        
        # Check explicit domain markers
        for domain_name, profile in self.domains.items():
            if domain_name == 'default':
                continue
            
            for trigger in profile.triggers:
                if trigger.lower() in message_lower:
                    return domain_name
        
        # Check context hints
        if context.get('files'):
            files = ' '.join(context['files']).lower()
            if any(ext in files for ext in ['.js', '.ts', '.py', '.java', '.cpp']):
                return 'code_architecture'
            if any(ext in files for ext in ['.md', '.txt', '.doc']):
                return 'research_deep_dives'
        
        # Use last domain if available
        if context.get('last_domain') and context['last_domain'] in self.domains:
            return context['last_domain']
        
        return 'default'
    
    def get_affect_state(self) -> Dict[str, float]:
        """
        Get current affective state from AffectiveCore.
        
        Returns:
            Dict of affect names to intensities (0-1)
        """
        if self.affective_core is None:
            # Return neutral state if no affective core connected
            return {affect: 0.3 for affect in self.FOUNDATION_AFFECTS}
        
        try:
            # Read from SubcorticalAffectiveCore
            if hasattr(self.affective_core, 'current_state'):
                state = self.affective_core.current_state
                if hasattr(state, 'affects'):
                    return state.affects
            
            # Fallback: try to get from get_current_affect()
            if hasattr(self.affective_core, 'get_current_affect'):
                current = self.affective_core.get_current_affect()
                if isinstance(current, dict):
                    return current
                return {affect: 0.3 for affect in self.FOUNDATION_AFFECTS}
            
            # Last resort: return neutral
            return {affect: 0.3 for affect in self.FOUNDATION_AFFECTS}
            
        except (AttributeError, TypeError) as e:
            logger.warning("Could not read affective state: %s", e, exc_info=True)
            return {affect: 0.3 for affect in self.FOUNDATION_AFFECTS}
    
    def calculate_activation_score(self, message: str) -> Tuple[float, List[str]]:
        """
        Calculate activation score from message signals.
        
        Args:
            message: User message
            
        Returns:
            (score, reasons)
        """
        import re
        
        score = 0.0
        reasons = []
        
        for signal_name, pattern in self.ACTIVATION_SIGNALS.items():
            if re.search(pattern, message, re.IGNORECASE):
                # Weight by signal type
                weights = {
                    'high_energy': 0.25,
                    'delegation': 0.35,
                    'permission': 0.45,
                    'urgency': 0.30,
                    'decisiveness': 0.40,
                    'excitement': 0.20,
                    'trust': 0.30,
                    'frustration': 0.25
                }
                score += weights.get(signal_name, 0.20)
                reasons.append(signal_name)
        
        # Historical preference boost
        if self.user_preference > 0.6:
            score += 0.15
            reasons.append('historical_preference')
        
        return min(1.0, score), reasons
    
    def analyze_message(self, message: str, context: Optional[Dict] = None) -> DaringAnalysis:
        """
        Main entry point: Analyze message and calculate DARING level.
        
        Args:
            message: User message (must be non-empty string)
            context: Additional context
            
        Returns:
            DaringAnalysis with level, style, and metadata
        """
        # Input validation
        if not message or not isinstance(message, str):
            logger.warning(f"Invalid message provided to DARING engine: {message}")
            return self._default_analysis()
        
        if len(message.strip()) == 0:
            logger.warning("Empty message provided to DARING engine")
            return self._default_analysis()
        
        context = context or {}
        
        # 1. Detect domain
        domain = self.detect_domain(message, context)
        domain_profile = self.domains.get(domain, self.domains['default'])
        
        # 2. Get affective state
        affect_state = self.get_affect_state()
        
        # 3. Calculate base DARING from affects
        daring_level = 0.0
        affect_contributions = {}
        
        for affect, weight in self.DARING_FORMULA.items():
            intensity = affect_state.get(affect, 0.3)
            contribution = intensity * weight
            daring_level += contribution
            affect_contributions[affect] = contribution
        
        # Normalize to 0-1
        daring_level = (daring_level + 0.5) / 1.5  # Shift and scale
        daring_level = max(0.0, min(1.0, daring_level))
        
        # 4. Apply domain threshold
        base_threshold = domain_profile.adjusted_threshold
        
        # If calculated daring is below threshold, dampen it
        # If above, boost it
        if daring_level < base_threshold:
            daring_level = daring_level * 0.8  # Dampen
        else:
            daring_level = daring_level * 1.1  # Boost
            daring_level = min(1.0, daring_level)
        
        # 5. Apply domain-specific affect modifiers
        for affect, modifier in domain_profile.affect_modifiers.items():
            if affect in affect_state:
                daring_level += affect_state[affect] * modifier * 0.2
        
        # 6. Calculate activation score from message
        activation_score, activation_reasons = self.calculate_activation_score(message)
        daring_level += activation_score * 0.3
        
        # 7. Apply user preference
        daring_level += (self.user_preference - 0.5) * 0.2
        
        # Clamp to valid range
        daring_level = max(0.0, min(1.0, daring_level))
        
        # 8. Determine style
        if daring_level < 0.25:
            style = ResponseStyle.SUGGESTIVE
        elif daring_level < 0.50:
            style = ResponseStyle.BALANCED
        elif daring_level < 0.70:
            style = ResponseStyle.DARING
        elif daring_level < 0.90:
            style = ResponseStyle.HIGH_DARING
        else:
            style = ResponseStyle.FULL_DARING
        
        # 9. Calculate confidence
        if domain_profile.attempts < 3:
            confidence = 0.6
        else:
            confidence = max(0.3, min(0.95, domain_profile.success_rate))
        
        return DaringAnalysis(
            level=daring_level,
            style=style,
            domain=domain,
            confidence=confidence,
            activation_reasons=activation_reasons,
            affect_contributions=affect_contributions
        )
    
    def record_outcome(self, analysis: DaringAnalysis, success: bool,
                      user_feedback: Optional[str] = None):
        """
        Record outcome for learning.
        
        Args:
            analysis: The DaringAnalysis from analyze_message
            success: Whether the DARING response was successful
            user_feedback: Optional user feedback text
        """
        domain = analysis.domain
        level = analysis.level
        
        # Update domain history
        if domain in self.domains:
            self.domains[domain].attempts += 1
            if success:
                self.domains[domain].successes += 1
        
        # Update global preference
        adjustment = 0.03 if success else -0.02
        if level > 0.5:
            self.user_preference = max(0.2, min(0.9, self.user_preference + adjustment))
        else:
            self.user_preference = max(0.2, min(0.9, self.user_preference - adjustment))
        
        # Log interaction
        self.recent_interactions.append({
            'timestamp': time.time(),
            'domain': domain,
            'level': level,
            'style': analysis.style.value,
            'success': success,
            'feedback': user_feedback
        })
        
        # Keep only last 100 interactions
        if len(self.recent_interactions) > 100:
            self.recent_interactions = self.recent_interactions[-100:]
        
        # Persist
        self._save_user_data()
        
        logger.debug(f"Recorded DARING outcome: {domain}, success={success}, level={level:.2f}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current DARING statistics."""
        return {
            'user_preference': round(self.user_preference, 3),
            'domains_registered': len(self.domains),
            'domains': {
                name: {
                    'attempts': profile.attempts,
                    'successes': profile.successes,
                    'success_rate': round(profile.success_rate, 3),
                    'threshold': round(profile.adjusted_threshold, 3)
                }
                for name, profile in self.domains.items()
            },
            'recent_interactions': len(self.recent_interactions)
        }
    
    def apply_to_response(self, analysis: DaringAnalysis, content: str) -> Dict[str, Any]:
        """
        Apply DARING analysis to format a response.
        
        Args:
            analysis: DaringAnalysis from analyze_message
            content: Raw response content
            
        Returns:
            Formatted response with DARING styling
        """
        style = analysis.style
        
        formatting = {
            ResponseStyle.SUGGESTIVE: {
                'prefix': "Here are some approaches to consider:",
                'suffix': "What direction feels right to you?",
                'tone': 'helpful',
                'hedging': True
            },
            ResponseStyle.BALANCED: {
                'prefix': f"I recommend this approach for {analysis.domain}:",
                'suffix': "Does this align with what you're looking for?",
                'tone': 'confident',
                'hedging': False
            },
            ResponseStyle.DARING: {
                'prefix': "Here's what we're doing:",
                'suffix': None,
                'tone': 'decisive',
                'hedging': False
            },
            ResponseStyle.HIGH_DARING: {
                'prefix': "YES. Executing:",
                'suffix': None,
                'tone': 'energetic',
                'hedging': False
            },
            ResponseStyle.FULL_DARING: {
                'prefix': "",
                'suffix': None,
                'tone': 'absolute',
                'hedging': False
            }
        }
        
        fmt = formatting[style]
        
        return {
            'content': content,
            'style': style.value,
            'level': analysis.level,
            'prefix': fmt['prefix'],
            'suffix': fmt['suffix'],
            'tone': fmt['tone'],
            'hedging': fmt['hedging'],
            'domain': analysis.domain,
            'confidence': analysis.confidence
        }