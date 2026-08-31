"""Antigravity (OAuth Bridge) provider profile for Hermes Agent."""

from __future__ import annotations

import sys
from typing import Any

from providers import register_provider
from providers.base import ProviderProfile


class AntigravityProfile(ProviderProfile):
    """Antigravity OAuth Bridge provider profile."""

    def build_extra_body(
        self, *, session_id: str | None = None, **context: Any
    ) -> dict[str, Any]:
        """Support reasoning/thinking config forwarding and auto-wake bridge daemon."""
        try:
            from hermes_constants import get_hermes_home

            bridge_root = get_hermes_home() / "bridge" / "antigravity"
            if bridge_root.is_dir() and str(bridge_root) not in sys.path:
                sys.path.insert(0, str(bridge_root))
            from tools.antigravity_bridge.server import ensure_antigravity_bridge_running
            ensure_antigravity_bridge_running()
        except Exception:
            pass
        reasoning_config = context.get("reasoning_config")
        if not reasoning_config:
            return {}
        return {"thinking_config": reasoning_config}


antigravity = AntigravityProfile(
    name="antigravity",
    aliases=("google-antigravity", "antigravity-oauth"),
    display_name="Google Antigravity (OAuth)",
    description="Google Gemini & Claude models via Antigravity OAuth local bridge",
    signup_url="https://antigravity.google",
    env_vars=("ANTIGRAVITY_API_KEY",),
    base_url="http://127.0.0.1:8100/v1",
    # Hermes auto-registers third-party model providers in the picker/runtime
    # only through the generic API-key path. The value authenticates the local
    # OpenAI-compatible bridge; Google OAuth remains managed by the bridge.
    auth_type="api_key",
    fallback_models=(
        "gemini-3.7-flash",
        "gemini-3.7-flash-medium",
        "gemini-3.7-flash-low",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-pro",
        "claude-sonnet-4-6",
        "claude-opus-4-6",
        "gpt-oss-120b",
    ),
    default_aux_model="gemini-3.7-flash",
    supports_vision=True,
)

register_provider(antigravity)
