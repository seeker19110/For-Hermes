"""
Layered Affect Architecture for NIMA Core

Three-layer system:
- Layer 1: Foundation (Panksepp 7) - hardwired
- Layer 2: Composites - learned from experience  
- Layer 3: Situational - emergent blends
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import json
import math
from pathlib import Path


class FoundationAffect(Enum):
    """Layer 1: Panksepp's 7 foundational affects."""
    SEEKING = auto()
    RAGE = auto()
    FEAR = auto()
    LUST = auto()
    CARE = auto()
    PANIC = auto()
    PLAY = auto()


@dataclass
class AffectState:
    """Current activation level of an affect (0.0 to 1.0)."""
    affect: FoundationAffect
    intensity: float  # 0.0 to 1.0
    confidence: float = 1.0  # How sure we are about this reading
    
    def __post_init__(self):
        self.intensity = max(0.0, min(1.0, self.intensity))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class CompositeAffect:
    """Layer 2: Learned composite affect."""
    name: str
    formula: str  # e.g., "SEEKING * 0.7 + (1-FEAR) * 0.5"
    base_threshold: float = 0.6
    domains: Dict[str, 'DomainProfile'] = field(default_factory=dict)
    
    def calculate(self, foundation_states: Dict[FoundationAffect, float], 
                  domain: Optional[str] = None) -> float:
        """Calculate composite intensity based on foundation states."""
        result = 0.0
        
        # Parse simple formula like "SEEKING * 0.7 + (1-FEAR) * 0.5"
        # Handle patterns: AFFECT * weight, (1-AFFECT) * weight, AFFECT * weight + AFFECT * weight
        
        parts = self.formula.split('+')
        total_weight = 0.0
        
        for part in parts:
            part = part.strip()
            
            # Pattern: "AFFECT * weight"
            if '*' in part and '(1-' not in part:
                affect_part, weight_part = part.split('*')
                affect_name = affect_part.strip()
                weight = float(weight_part.strip())
                
                for affect, intensity in foundation_states.items():
                    if affect.name == affect_name:
                        result += intensity * weight
                        total_weight += weight
                        break
            
            # Pattern: "(1-AFFECT) * weight" (inverted)
            elif '(1-' in part and '*' in part:
                # Extract affect name from (1-AFFECT)
                start = part.find('(1-') + 3
                end = part.find(')', start)
                affect_name = part[start:end].strip()
                
                weight_start = part.find('*') + 1
                weight = float(part[weight_start:].strip())
                
                for affect, intensity in foundation_states.items():
                    if affect.name == affect_name:
                        result += (1 - intensity) * weight
                        total_weight += weight
                        break
        
        # Normalize if weights don't sum to 1
        if total_weight > 0 and total_weight != 1.0:
            result = result / total_weight
            
        return min(1.0, max(0.0, result))


@dataclass
class DomainProfile:
    """User-defined domain with learned parameters."""
    name: str
    description: str
    threshold: float = 0.6
    attempts: int = 0
    successes: int = 0
    
    @property
    def success_ratio(self) -> float:
        if self.attempts == 0:
            return 0.5  # Neutral starting point
        return self.successes / self.attempts
    
    def record_attempt(self, success: bool):
        """Record an attempt and update threshold."""
        self.attempts += 1
        if success:
            self.successes += 1
            # Success: lower threshold (become more daring/confident)
            self.threshold = max(0.3, self.threshold - 0.03)
        else:
            # Failure: raise threshold (become more cautious)
            self.threshold = min(0.9, self.threshold + 0.05)


@dataclass
class AffectTree:
    """Complete three-layer affect tree structure."""
    # Layer 1: Foundation
    foundation: Dict[FoundationAffect, AffectState] = field(default_factory=dict)
    
    # Layer 2: Composites (empty domain slots by default)
    composites: Dict[str, CompositeAffect] = field(default_factory=dict)
    
    # Layer 3: Current situational blend (transient)
    situational_blend: Optional[str] = None
    
    def __post_init__(self):
        if not self.foundation:
            # Initialize with neutral states
            for affect in FoundationAffect:
                self.foundation[affect] = AffectState(affect, 0.5)


class LayeredAffectEngine:
    """
    Generic affect engine for NIMA Core.
    
    Usage:
        engine = LayeredAffectEngine(data_dir="./affect_data")
        
        # Define domains
        engine.define_domain("creative_work", "Making art, writing, designing")
        engine.define_domain("public_speaking", "Presentations and speeches")
        
        # Record experience
        engine.record_attempt("creative_work", success=True)
        
        # Calculate current state
        state = engine.calculate_state(domains=["creative_work"])
    """
    
    # Default composite definitions (generic)
    DEFAULT_COMPOSITES = {
        "DARING": {
            "formula": "SEEKING * 0.7 + (1-FEAR) * 0.5",
            "base_threshold": 0.6,
            "description": "Risk-taking that pays off"
        },
        "COURAGE": {
            "formula": "FEAR * 0.4 + CARE * 0.6",
            "base_threshold": 0.5,
            "description": "Acting despite fear because it matters"
        },
        "NURTURING": {
            "formula": "CARE * 0.8 + PLAY * 0.3",
            "base_threshold": 0.55,
            "description": "Sustained attention with positive intent"
        },
        "MASTERY": {
            "formula": "PLAY * 0.6 + SEEKING * 0.5",
            "base_threshold": 0.6,
            "description": "Joy in skill development"
        }
    }
    
    def __init__(self, data_dir: Optional[str] = None, user_id: str = "default"):
        self.user_id = user_id
        self.data_dir = Path(data_dir) if data_dir else Path("./nima_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create affect tree
        self.tree = self._load_tree()
        
        # Initialize default composites if none exist
        if not self.tree.composites:
            self._init_default_composites()
    
    def _init_default_composites(self):
        """Initialize default composite affects with empty domains."""
        for name, config in self.DEFAULT_COMPOSITES.items():
            self.tree.composites[name] = CompositeAffect(
                name=name,
                formula=config["formula"],
                base_threshold=config["base_threshold"]
            )
    
    def _load_tree(self) -> AffectTree:
        """Load affect tree from disk or create new."""
        profile_path = self.data_dir / f"affect_profile_{self.user_id}.json"
        
        if profile_path.exists():
            with open(profile_path) as f:
                data = json.load(f)
                return self._deserialize_tree(data)
        
        return AffectTree()
    
    def _save_tree(self):
        """Save affect tree to disk."""
        profile_path = self.data_dir / f"affect_profile_{self.user_id}.json"
        data = self._serialize_tree()
        with open(profile_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _serialize_tree(self) -> Dict:
        """Convert tree to serializable dict."""
        return {
            "user_id": self.user_id,
            "composites": {
                name: {
                    "formula": comp.formula,
                    "base_threshold": comp.base_threshold,
                    "domains": {
                        domain_name: {
                            "description": domain.description,
                            "threshold": domain.threshold,
                            "attempts": domain.attempts,
                            "successes": domain.successes
                        }
                        for domain_name, domain in comp.domains.items()
                    }
                }
                for name, comp in self.tree.composites.items()
            }
        }
    
    def _deserialize_tree(self, data: Dict) -> AffectTree:
        """Convert dict to AffectTree."""
        tree = AffectTree()
        
        for name, comp_data in data.get("composites", {}).items():
            composite = CompositeAffect(
                name=name,
                formula=comp_data["formula"],
                base_threshold=comp_data["base_threshold"]
            )
            
            for domain_name, domain_data in comp_data.get("domains", {}).items():
                composite.domains[domain_name] = DomainProfile(
                    name=domain_name,
                    description=domain_data.get("description", ""),
                    threshold=domain_data.get("threshold", 0.6),
                    attempts=domain_data.get("attempts", 0),
                    successes=domain_data.get("successes", 0)
                )
            
            tree.composites[name] = composite
        
        return tree
    
    def define_domain(self, composite_name: str, domain_name: str, 
                      description: str, initial_threshold: float = 0.6):
        """
        Define a new domain for a composite affect.
        
        Args:
            composite_name: e.g., "DARING", "COURAGE"
            domain_name: User-defined label, e.g., "creative_projects"
            description: What this domain means
            initial_threshold: Starting threshold (0.0 to 1.0)
        """
        if composite_name not in self.tree.composites:
            raise ValueError(f"Unknown composite: {composite_name}")
        
        composite = self.tree.composites[composite_name]
        composite.domains[domain_name] = DomainProfile(
            name=domain_name,
            description=description,
            threshold=initial_threshold
        )
        
        self._save_tree()
    
    def record_attempt(self, composite_name: str, domain_name: str, 
                       success: bool):
        """
        Record an attempt in a domain and update learning.
        
        Args:
            composite_name: Which composite (e.g., "DARING")
            domain_name: Which domain (e.g., "creative_projects")
            success: Whether the attempt succeeded
        """
        if composite_name not in self.tree.composites:
            raise ValueError(f"Unknown composite: {composite_name}")
        
        composite = self.tree.composites[composite_name]
        
        if domain_name not in composite.domains:
            raise ValueError(f"Unknown domain: {domain_name}")
        
        domain = composite.domains[domain_name]
        domain.record_attempt(success)
        
        self._save_tree()
    
    def calculate_composite(self, composite_name: str, 
                           foundation_states: Dict[FoundationAffect, float],
                           domain: Optional[str] = None) -> Tuple[float, float]:
        """
        Calculate composite intensity and threshold.
        
        Returns:
            Tuple of (intensity, threshold)
            Active if intensity > threshold
        """
        if composite_name not in self.tree.composites:
            raise ValueError(f"Unknown composite: {composite_name}")
        
        composite = self.tree.composites[composite_name]
        intensity = composite.calculate(foundation_states, domain)
        
        threshold = composite.base_threshold
        if domain and domain in composite.domains:
            threshold = composite.domains[domain].threshold
        
        return intensity, threshold
    
    def is_active(self, composite_name: str, 
                  foundation_states: Dict[FoundationAffect, float],
                  domain: Optional[str] = None) -> bool:
        """Check if a composite affect is currently active."""
        intensity, threshold = self.calculate_composite(
            composite_name, foundation_states, domain
        )
        return intensity > threshold
    
    def get_active_composites(self, 
                              foundation_states: Dict[FoundationAffect, float],
                              domain: Optional[str] = None) -> Dict[str, float]:
        """Get all currently active composites and their intensities."""
        active = {}
        for name in self.tree.composites:
            intensity, threshold = self.calculate_composite(
                name, foundation_states, domain
            )
            if intensity > threshold:
                active[name] = intensity
        return active
    
    def get_domain_stats(self, composite_name: str, 
                         domain_name: str) -> Optional[Dict]:
        """Get statistics for a specific domain."""
        if composite_name not in self.tree.composites:
            return None
        
        composite = self.tree.composites[composite_name]
        if domain_name not in composite.domains:
            return None
        
        domain = composite.domains[domain_name]
        return {
            "name": domain.name,
            "description": domain.description,
            "threshold": domain.threshold,
            "attempts": domain.attempts,
            "successes": domain.successes,
            "success_ratio": domain.success_ratio
        }
    
    def list_domains(self, composite_name: Optional[str] = None) -> Dict:
        """List all defined domains."""
        if composite_name:
            if composite_name not in self.tree.composites:
                return {}
            composite = self.tree.composites[composite_name]
            return {
                name: {
                    "description": domain.description,
                    "success_ratio": domain.success_ratio
                }
                for name, domain in composite.domains.items()
            }
        
        # Return all domains for all composites
        result = {}
        for comp_name, composite in self.tree.composites.items():
            result[comp_name] = {
                name: {
                    "description": domain.description,
                    "success_ratio": domain.success_ratio
                }
                for name, domain in composite.domains.items()
            }
        return result


# Convenience exports
__all__ = [
    "LayeredAffectEngine",
    "FoundationAffect", 
    "AffectState",
    "CompositeAffect",
    "DomainProfile",
    "AffectTree"
]