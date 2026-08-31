"""HTTP server and daemon runner for Antigravity Local Bridge.

Implements standard OpenAI API endpoints:
- GET  /v1/models
- POST /v1/chat/completions (with Server-Sent Events streaming support)
- GET  /health
- GET  /auth/status
- POST /auth/login
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from aiohttp import web

try:
    from bridge.auth import (
        AntigravityAuthManager,
        get_hermes_dir,
    )
    from bridge.client import (
        ANTIGRAVITY_SUPPORTED_MODELS,
        AntigravityClient,
    )
except ImportError:
    from tools.antigravity_bridge.auth import (
        AntigravityAuthManager,
        get_hermes_dir,
    )
    from tools.antigravity_bridge.client import (
        ANTIGRAVITY_SUPPORTED_MODELS,
        AntigravityClient,
    )

logger = logging.getLogger(__name__)


def _upstream_status(exc: Exception) -> int:
    """Lấy mã HTTP thật từ UpstreamError; các lỗi khác đoán an toàn từ nội dung."""
    status = getattr(exc, "status_code", None)
    if isinstance(status, int) and 400 <= status < 600:
        return status
    text = str(exc)
    if "429" in text or "exhausted" in text.lower():
        return 429
    return 500


DEFAULT_BRIDGE_PORT = 8100
DEFAULT_BRIDGE_HOST = "127.0.0.1"


def get_bridge_dir() -> Path:
    bridge_dir = get_hermes_dir() / "bridge" / "antigravity"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    return bridge_dir


def get_pid_file() -> Path:
    return get_bridge_dir() / "bridge.pid"


def get_log_file() -> Path:
    log_dir = get_hermes_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "antigravity_bridge.log"


class AntigravityBridgeServer:
    """Async HTTP Server exposing Antigravity Code Assist as OpenAI API."""

    def __init__(
        self,
        host: str = DEFAULT_BRIDGE_HOST,
        port: int = DEFAULT_BRIDGE_PORT,
        auth_manager: Optional[AntigravityAuthManager] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.auth_manager = auth_manager or AntigravityAuthManager()
        self.client = AntigravityClient(self.auth_manager)
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.app.router.add_get("/health", self.handle_health)
        self.app.router.add_get("/auth/status", self.handle_auth_status)
        self.app.router.add_post("/auth/login", self.handle_auth_login)
        self.app.router.add_get("/v1/models", self.handle_list_models)
        self.app.router.add_post("/v1/chat/completions", self.handle_chat_completions)

    async def handle_health(self, request: web.Request) -> web.Response:
        return web.json_response({
            "status": "ok",
            "bridge": "antigravity",
            "version": "1.0.0",
            "timestamp": time.time(),
        })

    async def handle_auth_status(self, request: web.Request) -> web.Response:
        creds = self.auth_manager.load_stored_credentials() or self.auth_manager.discover_local_tokens()
        if not creds:
            return web.json_response({
                "logged_in": False,
                "email": "",
                "project_id": "",
                "expires_at": None,
                "message": "No credentials stored. Please log in.",
            })

        return web.json_response({
            "logged_in": True,
            "email": creds.email,
            "project_id": creds.project_id,
            "expires_at": creds.expires_at,
            "is_expired": creds.is_expired,
            "has_refresh_token": bool(creds.refresh_token),
            "source": creds.source,
        })

    async def handle_auth_login(self, request: web.Request) -> web.Response:
        try:
            creds = await asyncio.to_thread(self.auth_manager.login_pkce)
            return web.json_response({
                "ok": True,
                "email": creds.email,
                "project_id": creds.project_id,
            })
        except Exception as e:
            return web.json_response({"ok": False, "error": str(e)}, status=500)

    async def handle_list_models(self, request: web.Request) -> web.Response:
        models = []
        for m in ANTIGRAVITY_SUPPORTED_MODELS:
            models.append({
                "id": m["id"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "antigravity",
                "permission": [],
                "description": m.get("description", ""),
            })
        return web.json_response({
            "object": "list",
            "data": models,
        })

    async def handle_chat_completions(self, request: web.Request) -> web.StreamResponse:
        try:
            payload = await request.json()
        except Exception as e:
            return web.json_response(
                {"error": {"message": f"Invalid JSON payload: {e}", "type": "invalid_request_error"}},
                status=400,
            )

        auth_header = request.headers.get("Authorization") or ""
        bearer_token = ""
        if auth_header.startswith("Bearer "):
            bearer_token = auth_header[7:].strip()
            if bearer_token in {"dummy", "none", "token", "default", "antigravity"}:
                bearer_token = ""

        is_stream = bool(payload.get("stream"))

        if is_stream:
            stream_gen = self.client.stream_chat_completion(payload, bearer_token=bearer_token)
            try:
                first_chunk = await stream_gen.__anext__()
            except Exception as e:
                logger.error("Error connecting to chat completion stream: %s", e)
                status_code = _upstream_status(e)
                err_type = "rate_limit_error" if status_code == 429 else "api_error"
                return web.json_response(
                    {"error": {"message": str(e), "type": err_type, "code": status_code}},
                    status=status_code,
                )

            response = web.StreamResponse(
                status=200,
                reason="OK",
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )
            try:
                await response.prepare(request)
                await response.write(first_chunk.encode("utf-8"))
                try:
                    async for chunk_str in stream_gen:
                        await response.write(chunk_str.encode("utf-8"))
                except Exception as e:
                    logger.error("Error during chat completion stream: %s", e)
                await response.write_eof()
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
                logger.debug("Client disconnected during streaming: %s", e)
            except Exception as e:
                if "closing transport" in str(e).lower() or "connection" in str(e).lower():
                    logger.debug("Client connection lost during streaming: %s", e)
                else:
                    logger.error("Unexpected error during streaming: %s", e)
            finally:
                # Đóng generator để giải phóng kết nối httpx tới Google ngay,
                # kể cả khi client ngắt giữa chừng (tránh cạn connection pool).
                with contextlib.suppress(Exception):
                    await stream_gen.aclose()
            return response
        else:
            try:
                result = await self.client.create_chat_completion(payload, bearer_token=bearer_token)
                return web.json_response(result)
            except Exception as e:
                logger.error("Error during chat completion: %s", e)
                status_code = _upstream_status(e)
                err_type = "rate_limit_error" if status_code == 429 else "api_error"
                return web.json_response(
                    {"error": {"message": str(e), "type": err_type, "code": status_code}},
                    status=status_code,
                )

    async def start(self) -> web.AppRunner:
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info("Antigravity Bridge Server listening on http://%s:%s", self.host, self.port)
        return runner


def run_server(host: str = DEFAULT_BRIDGE_HOST, port: int = DEFAULT_BRIDGE_PORT) -> None:
    """Run the bridge server in the foreground."""
    server = AntigravityBridgeServer(host=host, port=port)
    web.run_app(server.app, host=host, port=port)


def is_server_running(host: str = DEFAULT_BRIDGE_HOST, port: int = DEFAULT_BRIDGE_PORT) -> bool:
    """Check if the bridge server is responding to health checks."""
    import urllib.request
    try:
        req = urllib.request.Request(f"http://{host}:{port}/health")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("bridge") == "antigravity"
    except Exception:
        return False


def ensure_antigravity_bridge_running(
    host: str = DEFAULT_BRIDGE_HOST,
    port: int = DEFAULT_BRIDGE_PORT,
    timeout: float = 3.0,
) -> bool:
    """Ensure the Antigravity bridge server is running, spawning a daemon if not."""
    if is_server_running(host=host, port=port):
        return True

    import subprocess
    import sys
    import time

    try:
        from tools.antigravity_bridge.auth import AntigravityAuthManager
        mgr = AntigravityAuthManager()
        if not mgr.load_all_stored_credentials():
            return False
    except Exception:
        return False

    cmd = [
        sys.executable,
        "-u",
        "-c",
        f"from tools.antigravity_bridge.server import run_server; run_server(host='{host}', port={port})",
    ]
    package_root = Path(__file__).resolve().parents[2]

    try:
        if sys.platform == "win32":
            subprocess.Popen(
                cmd,
                cwd=str(package_root),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
        else:
            subprocess.Popen(
                cmd,
                cwd=str(package_root),
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(0.2)
            if is_server_running(host=host, port=port):
                logger.info("Antigravity Bridge auto-started on http://%s:%s", host, port)
                return True
        return is_server_running(host=host, port=port)
    except Exception as e:
        logger.warning("Failed to auto-spawn Antigravity Bridge: %s", e)
        return False

