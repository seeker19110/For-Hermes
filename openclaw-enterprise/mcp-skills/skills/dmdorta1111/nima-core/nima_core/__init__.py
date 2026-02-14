"""NIMA Core — Biologically-inspired cognitive memory for AI agents."""

__version__ = "1.0.0"

from .core import NimaCore
from .config.nima_config import NimaConfig, get_config

# Convenience re-exports for common components
from .layers.affective_core import SubcorticalAffectiveCore, AffectState
from .layers.binding_layer import VSABindingLayer, BoundEpisode, BindingOperation
from .bridge import NimaV2Bridge, ProcessedExperience
from .services.heartbeat import NimaHeartbeat
from .services.markdown_bridge import MarkdownBridge
from .cognition.dream_engine import DreamEngine, DreamSession, Insight, Pattern

__all__ = [
    "NimaCore",
    "NimaConfig",
    "get_config",
    "SubcorticalAffectiveCore",
    "AffectState",
    "VSABindingLayer",
    "BoundEpisode",
    "BindingOperation",
    "NimaV2Bridge",
    "ProcessedExperience",
    "NimaHeartbeat",
    "MarkdownBridge",
    "DreamEngine",
    "DreamSession",
    "Insight",
    "Pattern",
    "__version__",
]
