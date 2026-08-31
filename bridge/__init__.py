"""Antigravity Local OAuth Bridge for Hermes Agent.

Provides a local OpenAI-compatible HTTP daemon that simulates Antigravity IDE/CLI
client headers, manages Google OAuth 2.0 PKCE authentication, translates OpenAI
chat payloads into Gemini/Code Assist generateContent requests, and surfaces
models to Hermes.
"""

from __future__ import annotations

try:
    # Source-tree layout: `bridge/` imported directly (e.g. `import bridge`
    # from the repo root, as manage.py/install.py do before any install step
    # has copied files under `tools/antigravity_bridge/`).
    from bridge.auth import (
        AntigravityAuthManager,
        AntigravityCredentials,
    )
    from bridge.client import (
        AntigravityClient,
        ANTIGRAVITY_SUPPORTED_MODELS,
    )
    from bridge.server import (
        AntigravityBridgeServer,
        run_server,
    )
except ImportError:
    # Installed layout: copied to $HERMES_HOME/bridge/antigravity/tools/antigravity_bridge/.
    from tools.antigravity_bridge.auth import (
        AntigravityAuthManager,
        AntigravityCredentials,
    )
    from tools.antigravity_bridge.client import (
        AntigravityClient,
        ANTIGRAVITY_SUPPORTED_MODELS,
    )
    from tools.antigravity_bridge.server import (
        AntigravityBridgeServer,
        run_server,
    )

__all__ = [
    "AntigravityAuthManager",
    "AntigravityCredentials",
    "AntigravityClient",
    "ANTIGRAVITY_SUPPORTED_MODELS",
    "AntigravityBridgeServer",
    "run_server",
]
