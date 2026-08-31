"""Offline integration smoke test for the Hermes Antigravity plugin."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="hermes-antigravity-verify-") as tmp:
        home = Path(tmp)
        env = dict(os.environ)
        env["HERMES_HOME"] = str(home)
        env["ANTIGRAVITY_API_KEY"] = "local-bridge-test-token"

        run(str(ROOT / "install.py"), env=env)

        provider_probe = """
from providers import get_provider_profile
from hermes_cli.auth import PROVIDER_REGISTRY
from hermes_cli.models import CANONICAL_PROVIDERS
from hermes_cli.runtime_provider import resolve_runtime_provider
p = get_provider_profile('antigravity')
assert p is not None
assert 'antigravity' in PROVIDER_REGISTRY
assert any(entry.slug == 'antigravity' for entry in CANONICAL_PROVIDERS)
runtime = resolve_runtime_provider(requested='antigravity')
assert runtime['base_url'] == 'http://127.0.0.1:8100/v1'
"""
        run("-c", provider_probe, env=env)

        manager = home / "bridge" / "antigravity" / "manage.py"
        port = free_port()
        try:
            run(str(manager), "start", "--port", str(port), env=env)
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/health", timeout=5
            ) as response:
                health = json.load(response)
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/v1/models", timeout=5
            ) as response:
                models = json.load(response)

            assert health["status"] == "ok"
            assert health["bridge"] == "antigravity"
            assert len(models["data"]) == 9
            assert "gemini-3.7-pro" not in {m["id"] for m in models["data"]}
        finally:
            if manager.exists():
                subprocess.run(
                    [sys.executable, str(manager), "stop"],
                    cwd=ROOT,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )

    print("Antigravity provider install, discovery, runtime, and bridge: OK")


if __name__ == "__main__":
    main()
