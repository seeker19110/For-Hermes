#!/usr/bin/env python3
"""
NIMA v2 Bridge — Integration Layer
====================================
Unified integration layer for NIMA v2 components.

This is the production integration point that:
- Routes processing through v2 components when enabled
- Falls back to legacy for safety
- Provides unified API
- Enables gradual rollout via feature flags

Author: NIMA Project
Date: 2026
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import os
import threading
import logging

logger = logging.getLogger(__name__)

# Feature flags
from .config.nima_config import get_config, should_use_v2_for

# Legacy imports
try:
    from .cognition.free_energy import FreeEnergyConsolidation
    HAS_FE = True
except ImportError:
    HAS_FE = False

try:
    from .cognition.schema_extractor import SchemaExtractor
    HAS_SCHEMA = True
except ImportError:
    HAS_SCHEMA = False

# NIMA v2 imports
try:
    from .layers.affective_core import SubcorticalAffectiveCore, AffectState
    from .layers.binding_layer import VSABindingLayer, BoundEpisode
    HAS_NIMA_V2 = True
except ImportError:
    HAS_NIMA_V2 = False


@dataclass
class ProcessedExperience:
    """Result of processing an experience through the bridge."""
    content: str
    affect: Optional[Dict] = None
    bound_episode: Optional[Dict] = None
    should_consolidate: bool = True
    consolidation_reason: str = "default"
    free_energy: float = 0.5
    v2_components_used: List[str] = None
    
    def __post_init__(self):
        if self.v2_components_used is None:
            self.v2_components_used = []
    
    def to_dict(self) -> Dict:
        return {
            'content': self.content,
            'affect': self.affect,
            'bound_episode': self.bound_episode,
            'should_consolidate': self.should_consolidate,
            'consolidation_reason': self.consolidation_reason,
            'free_energy': self.free_energy,
            'v2_components_used': self.v2_components_used,
        }


class NimaV2Bridge:
    """
    Bridge connecting all NIMA v2 components.
    
    Usage:
        bridge = NimaV2Bridge()
        result = bridge.process_experience("Alice asked about NIMA", who="Alice")
        
        if result.should_consolidate:
            # Store in memory
            pass
    """
    
    def __init__(self, auto_init: bool = True):
        """Initialize bridge with available components."""
        self.config = get_config()
        self._lock = threading.RLock()
        
        # Components (lazy init)
        self._affective_core: Optional[SubcorticalAffectiveCore] = None
        self._binding_layer: Optional[VSABindingLayer] = None
        self._fe_consolidation: Optional[FreeEnergyConsolidation] = None
        self._schema_extractor: Optional[SchemaExtractor] = None
        
        # Stats
        self.experiences_processed = 0
        self.v2_calls = 0
        self.legacy_fallbacks = 0
        
        if auto_init:
            self._initialize_components()
    
    def _initialize_components(self):
        """Initialize enabled components (all under lock)."""
        with self._lock:
            if not HAS_NIMA_V2:
                logger.warning("NIMA v2 module not found, using legacy only")
                return
            
            # Affective Core
            if self.config.affective_core:
                try:
                    self._affective_core = SubcorticalAffectiveCore()
                    logger.info("Affective core initialized")
                except Exception as e:
                    logger.warning(f"Affective core failed: {e}")
            
            # Binding Layer
            if self.config.binding_layer:
                try:
                    self._binding_layer = VSABindingLayer(dimension=10000)
                    logger.info("Binding layer initialized")
                except Exception as e:
                    logger.warning(f"Binding layer failed: {e}")
            
            # Free Energy (from cognition, not nima_v2)
            if self.config.consolidation_fe and HAS_FE:
                try:
                    self._fe_consolidation = FreeEnergyConsolidation()
                    logger.info("FE consolidation initialized")
                except Exception as e:
                    logger.warning(f"FE consolidation failed: {e}")
            
            # Schema Extractor
            if HAS_SCHEMA:
                try:
                    self._schema_extractor = SchemaExtractor()
                    logger.info("Schema extractor initialized")
                except Exception as e:
                    logger.warning(f"Schema extractor failed: {e}")
    
    def process_experience(self, content: str,
                          who: str = "unknown",
                          where: str = "session",
                          when: str = None,
                          importance: float = 0.5,
                          **kwargs) -> ProcessedExperience:
        """
        Process an experience through the v2 pipeline.
        
        Order:
        1. Affective processing (if enabled)
        2. Binding (if enabled)
        3. FE consolidation decision (if enabled)
        
        Returns:
            ProcessedExperience with all annotations
        """
        self.experiences_processed += 1
        v2_used = []
        
        result = ProcessedExperience(content=content)
        
        # Build context
        context = {
            'text': content,
            'who': who,
            'where': where,
            'when': when or str(np.datetime64('now')),
            'importance': importance,
            **kwargs,
        }
        
        # Step 1: Affective processing
        affect_state = None
        if self._affective_core and should_use_v2_for('affect_processing'):
            try:
                stimulus = np.random.randn(128)  # Placeholder
                affect_state = self._affective_core.process(stimulus, context)
                result.affect = affect_state.to_dict()
                v2_used.append('affective_core')
                self.v2_calls += 1
            except Exception as e:
                logger.warning(f"Affective processing failed: {e}")
                self.legacy_fallbacks += 1
        
        # Step 2: Binding
        if self._binding_layer and should_use_v2_for('binding'):
            try:
                bindings = {
                    'WHO': who,
                    'WHAT': content[:100],
                    'WHERE': where,
                    'WHEN': context['when'],
                }
                
                # Note: Affect vector has different dimension (128 vs 10000)
                # We bind affect as text label instead of raw vector
                if affect_state and affect_state.dominant:
                    bindings['AFFECT'] = affect_state.dominant
                
                episode = self._binding_layer.create_episode(bindings, affect=None)
                result.bound_episode = episode.to_dict()
                v2_used.append('binding_layer')
                self.v2_calls += 1
            except Exception as e:
                logger.warning(f"Binding failed: {e}")
                self.legacy_fallbacks += 1
        
        # Step 3: Consolidation decision
        if self._fe_consolidation and should_use_v2_for('consolidation'):
            try:
                # FE expects (text, affect) signature
                fe_result = self._fe_consolidation.should_consolidate(
                    text=content,
                    affect=affect_state.to_dict() if affect_state else None,
                )
                
                result.should_consolidate = fe_result.should_consolidate
                result.consolidation_reason = fe_result.reason.value
                result.free_energy = fe_result.free_energy
                v2_used.append('fe_consolidation')
                self.v2_calls += 1
            except Exception as e:
                logger.warning(f"FE consolidation failed: {e}")
                # Fall back to importance threshold
                result.should_consolidate = importance > 0.3
                result.consolidation_reason = "importance_fallback"
                self.legacy_fallbacks += 1
        else:
            # Legacy: simple importance threshold
            result.should_consolidate = importance > 0.3
            result.consolidation_reason = "importance_threshold"
        
        result.v2_components_used = v2_used
        
        return result
    
    def annotate_for_story(self, content: str, **kwargs) -> Dict:
        """
        Get annotations suitable for StoryEngine.
        
        Returns dict compatible with StoryEngine's expected format.
        """
        result = self.process_experience(content, **kwargs)
        
        annotations = {
            'content': content,
            'emotional_valence': result.affect.get('valence', 0) if result.affect else 0,
            'emotional_arousal': result.affect.get('arousal', 0.5) if result.affect else 0.5,
            'dominant_affect': result.affect.get('dominant') if result.affect else None,
            'attention_weight': result.affect.get('attention_weight', 1.0) if result.affect else 1.0,
            'should_consolidate': result.should_consolidate,
            'free_energy': result.free_energy,
        }
        
        return annotations
    
    def annotate_for_dream(self, content: str, **kwargs) -> Dict:
        """
        Get annotations suitable for DreamEngine.
        
        Returns dict compatible with DreamEngine's replay format.
        """
        result = self.process_experience(content, **kwargs)
        
        annotations = {
            'content': content,
            'priority': result.free_energy,  # High FE = replay priority
            'affect': result.affect,
            'consolidation_reason': result.consolidation_reason,
            'replay_weight': result.affect.get('attention_weight', 1.0) if result.affect else 1.0,
        }
        
        return annotations
    
    def learn_somatic_marker(self, situation: str, 
                            outcome_valence: float,
                            description: str = None):
        """
        Learn a gut feeling from experience outcome.
        
        Call this after experiences resolve (positive or negative).
        """
        with self._lock:
            if self._affective_core:
                self._affective_core.update_somatic_marker(
                    situation, 
                    outcome_valence,
                    description=description,
                )
    
    def get_current_affect(self) -> Optional[Dict]:
        """Get current affective state."""
        if self._affective_core:
            return self._affective_core.get_stats()
        return None
    
    def get_affect_trajectory(self, window: int = 10) -> Optional[Dict]:
        """Get recent affective trajectory."""
        if self._affective_core:
            return self._affective_core.get_trajectory(window)
        return None
    
    def is_v2_active(self) -> bool:
        """Check if any v2 components are active."""
        return any([
            self._affective_core is not None,
            self._binding_layer is not None,
            self._fe_consolidation is not None,
        ])
    
    def get_stats(self) -> Dict:
        """Get bridge statistics."""
        stats = {
            'config': self.config.to_dict(),
            'experiences_processed': self.experiences_processed,
            'v2_calls': self.v2_calls,
            'legacy_fallbacks': self.legacy_fallbacks,
            'v2_active': self.is_v2_active(),
            'components': {
                'affective_core': self._affective_core is not None,
                'binding_layer': self._binding_layer is not None,
                'fe_consolidation': self._fe_consolidation is not None,
                'schema_extractor': self._schema_extractor is not None,
            },
        }
        
        if self._affective_core:
            stats['affective'] = self._affective_core.get_stats()
        
        if self._binding_layer:
            stats['binding'] = self._binding_layer.get_stats()
        
        if self._fe_consolidation:
            stats['consolidation'] = self._fe_consolidation.get_stats()
        
        return stats


# Singleton instance for easy access
_bridge_instance: Optional[NimaV2Bridge] = None


def get_bridge() -> NimaV2Bridge:
    """Get or create the singleton bridge instance."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = NimaV2Bridge()
    return _bridge_instance


def process_experience(content: str, **kwargs) -> ProcessedExperience:
    """Convenience function for one-shot processing."""
    return get_bridge().process_experience(content, **kwargs)


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Testing NimaV2Bridge...")
    
    bridge = NimaV2Bridge()
    
    # Process some experiences
    experiences = [
        ("Alice asked about NIMA progress", "Alice"),
        ("The weather is nice today", "system"),
        ("I enjoy learning new things!", "Agent"),
        ("Something frustrating happened", "unknown"),
    ]
    
    for content, who in experiences:
        result = bridge.process_experience(content, who=who)
        logger.debug(f"'{content[:40]}...'")
        logger.debug(f"  Affect: {result.affect.get('dominant') if result.affect else 'N/A'}")
        logger.debug(f"  FE: {result.free_energy:.3f}")
        logger.debug(f"  Consolidate: {result.should_consolidate} ({result.consolidation_reason})")
        logger.debug(f"  v2 used: {result.v2_components_used}")
    
    logger.info(f"Stats: {bridge.get_stats()}")
    logger.info("Bridge working!")
