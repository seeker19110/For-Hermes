"""NIMA Core cognition module."""
from .free_energy import FreeEnergyConsolidation, FreeEnergyResult, ConsolidationReason
from .schema_extractor import SchemaExtractor, Schema, SchemaConfig
from .temporal_encoder import TemporalEncoder, TemporalConfig, SequenceEncoding
from .sequence_predictor import SequenceCorpus, NextTurnPredictor
from .active_inference import ActiveInferenceEngine
from .hyperbolic_memory import HyperbolicTaxonomy
from .metacognitive import MetacognitiveLayer
from .dream_engine import DreamEngine, DreamSession, Insight, Pattern
from .affect_layer import (
    LayeredAffectEngine,
    FoundationAffect,
    AffectState,
    CompositeAffect,
    DomainProfile,
    AffectTree
)
from .response_modulator import DaringResponseModulator
from .daring_engine import DaringEngine, ResponseStyle, DaringAnalysis
from .courage_engine import CourageEngine, ResponseStyle as CourageStyle, CourageAnalysis
from .nurturing_engine import NurturingEngine, ResponseStyle as NurturingStyle, NurturingAnalysis
from .mastery_engine import MasteryEngine, ResponseStyle as MasteryStyle, MasteryAnalysis
from .async_affective import AsyncAffectiveProcessor, AffectiveResult, analyze_async, get_processor

__all__ = [
    "FreeEnergyConsolidation",
    "FreeEnergyResult",
    "ConsolidationReason",
    "SchemaExtractor",
    "Schema",
    "SchemaConfig",
    "TemporalEncoder",
    "TemporalConfig",
    "SequenceEncoding",
    "SequenceCorpus",
    "NextTurnPredictor",
    "ActiveInferenceEngine",
    "HyperbolicTaxonomy",
    "MetacognitiveLayer",
    "DreamEngine",
    "DreamSession",
    "Insight",
    "Pattern",
    # Affect Layer
    "LayeredAffectEngine",
    "FoundationAffect",
    "AffectState",
    "CompositeAffect",
    "DomainProfile",
    "AffectTree",
    # Response Modulation
    "DaringResponseModulator",
    # DARING Engine
    "DaringEngine",
    "ResponseStyle",
    "DaringAnalysis",
    # COURAGE Engine
    "CourageEngine",
    "CourageStyle",
    "CourageAnalysis",
    # NURTURING Engine
    "NurturingEngine",
    "NurturingStyle",
    "NurturingAnalysis",
    # MASTERY Engine
    "MasteryEngine",
    "MasteryStyle",
    "MasteryAnalysis",
    # Async Affective
    "AsyncAffectiveProcessor",
    "AffectiveResult",
    "analyze_async",
    "get_processor",
]
