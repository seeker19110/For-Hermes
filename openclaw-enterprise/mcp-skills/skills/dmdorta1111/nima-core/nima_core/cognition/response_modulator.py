#!/usr/bin/env python3
"""
DARING Response Modulator
Integrates affect state into response generation.
"""

import sys
sys.path.insert(0, '/Users/lilu/.openclaw/workspace/nima-core')

from nima_core.cognition import LayeredAffectEngine, FoundationAffect
from typing import Dict, Optional, Tuple
import json

class DaringResponseModulator:
    """
    Modulates responses based on DARING affect state.
    
    Usage:
        modulator = DaringResponseModulator()
        response = modulator.generate_response(
            prompt="Should I...?",
            domain="code_architecture",
            base_response="..."
        )
    """
    
    def __init__(self, data_dir: str = "./lilu_affect", user_id: str = "lilu"):
        self.engine = LayeredAffectEngine(data_dir=data_dir, user_id=user_id)
        
        # Domain detection keywords
        self.domain_keywords = {
            "theological_synthesis": ["theology", "christian", "faith", "bible", "prayer", "spiritual", "church", "god", "religion", "mercy", "healing"],
            "code_architecture": ["code", "architecture", "refactor", "rewrite", "system", "build", "implement", "rust", "python", "database"],
            "family_protection": ["family", "children", "kids", "parent", "protect", "safe", "daughter", "son", "spouse", "loved ones"],
            "research_deep_dives": ["research", "study", "deep dive", "paper", "scientific", "neuroscience", "cosmos", "space"],
            "creative_building": ["idea", "creative", "experiment", "new", "innovation", "design", "art", "dream"]
        }
    
    def detect_domain(self, prompt: str) -> Optional[str]:
        """Detect which domain a prompt belongs to."""
        prompt_lower = prompt.lower()
        
        scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for kw in keywords if kw in prompt_lower)
            if score > 0:
                scores[domain] = score
        
        if not scores:
            return None
        
        return max(scores, key=scores.get)
    
    def get_daring_state(self, domain: Optional[str] = None) -> Tuple[bool, float, float]:
        """
        Get current DARING state.
        
        Returns:
            (is_active, intensity, threshold)
        """
        # Current foundation state (would come from actual affect detection)
        foundation = {
            FoundationAffect.SEEKING: 0.85,  # High curiosity
            FoundationAffect.FEAR: 0.15,      # Low fear (safe environment)
            FoundationAffect.CARE: 0.8        # High care (important conversation)
        }
        
        if domain:
            intensity, threshold = self.engine.calculate_composite(
                'DARING', foundation, domain=domain
            )
        else:
            # Use base threshold
            intensity, threshold = self.engine.calculate_composite(
                'DARING', foundation
            )
        
        return intensity > threshold, intensity, threshold
    
    def modulate_response(self, response: str, domain: Optional[str] = None,
                         daring_active: bool = True) -> str:
        """
        Apply DARING modulation to a response.
        
        This is a simplified version - in production, this would
        modulate the actual LLM generation, not just post-process.
        """
        if not daring_active:
            return response
        
        # For now, just prepend an indicator
        # In real implementation, this would affect the generation itself
        stats = self.engine.get_domain_stats('DARING', domain) if domain else None
        
        if stats:
            ratio = stats['success_ratio']
            if ratio > 0.9:
                prefix = "[HIGH DARING — Direct guidance]\n\n"
            elif ratio > 0.7:
                prefix = "[DARING — Confident response]\n\n"
            else:
                prefix = "[Measured — Based on experience]\n\n"
        else:
            prefix = "[DARING ACTIVE]\n\n"
        
        return prefix + response
    
    def generate_response_style(self, prompt: str, domain: Optional[str] = None) -> Dict:
        """
        Determine response style based on DARING state.
        
        Returns guidance for response generation.
        """
        # Auto-detect domain from prompt if not provided
        if domain is None:
            domain = self.detect_domain(prompt)
        
        is_active, intensity, threshold = self.get_daring_state(domain)
        
        if is_active:
            return {
                "style": "DARING",
                "tone": "Direct, confident, conviction-based",
                "avoid": ["hedging", "maybe", "perhaps", "some experts say"],
                "embrace": ["direct statements", "specific guidance", "learned patterns"],
                "intensity": intensity,
                "threshold": threshold
            }
        else:
            return {
                "style": "CAUTIOUS", 
                "tone": "Measured, exploratory, open-ended",
                "avoid": ["strong claims", "definitive answers"],
                "embrace": ["questions", "multiple perspectives", "careful consideration"],
                "intensity": intensity,
                "threshold": threshold
            }
    
    def status(self) -> Dict:
        """Get current DARING status across all domains."""
        return {
            "active_domains": self.engine.list_domains('DARING'),
            "current_foundation": {
                "SEEKING": 0.85,
                "FEAR": 0.15,
                "CARE": 0.8
            }
        }


# Simple CLI test
if __name__ == "__main__":
    modulator = DaringResponseModulator()
    
    test_prompts = [
        "Should I rewrite my app in Rust?",
        "Explain why Orthodox Christians kiss icons",
        "My kid wants to start a YouTube channel",
        "What do you think about this new AI architecture?",
        "What's the weather like today?"  # No domain match
    ]
    
    print("DARING RESPONSE MODULATOR — TEST")
    print("=" * 70)
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        
        domain = modulator.detect_domain(prompt)
        print(f"Detected domain: {domain or 'NONE'}")
        
        is_active, intensity, threshold = modulator.get_daring_state(domain)
        print(f"DARING: {'ACTIVE' if is_active else 'INACTIVE'} (intensity: {intensity:.2f}, threshold: {threshold:.2f})")
        
        style = modulator.generate_response_style(prompt, domain)
        print(f"Style: {style['style']}")
        print(f"Tone: {style['tone']}")
        print(f"Avoid: {', '.join(style['avoid'][:2])}...")
        print("-" * 50)
