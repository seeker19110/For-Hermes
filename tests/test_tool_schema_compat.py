"""Regression tests for tool schemas forwarded to Code Assist."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_client_module():
    tools_pkg = types.ModuleType("tools")
    tools_pkg.__path__ = []
    bridge_pkg = types.ModuleType("tools.antigravity_bridge")
    bridge_pkg.__path__ = [str(ROOT / "bridge")]
    sys.modules.setdefault("tools", tools_pkg)
    sys.modules.setdefault("tools.antigravity_bridge", bridge_pkg)

    spec = importlib.util.spec_from_file_location(
        "tools.antigravity_bridge.client", ROOT / "bridge" / "client.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["tools.antigravity_bridge.client"] = module
    spec.loader.exec_module(module)
    return module


client = load_client_module()


class ToolSchemaCompatibilityTests(unittest.TestCase):
    def test_nullable_pydantic_shapes_are_normalized_before_forwarding(self) -> None:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "complex_tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "anyOf": [{"type": "string"}, {"type": "null"}],
                                "default": None,
                            },
                            "limit": {"type": ["integer", "null"], "nullable": True},
                            "target": {"$ref": "#/$defs/Target", "default": None},
                        },
                        "$defs": {
                            "Target": {
                                "type": "object",
                                "properties": {"path": {"type": "string"}},
                            }
                        },
                    },
                },
            }
        ]

        translated = client._translate_tools_to_gemini(tools)
        params = translated[0]["functionDeclarations"][0]["parameters"]

        self.assertEqual(params["properties"]["query"]["type"], "string")
        self.assertNotIn("anyOf", params["properties"]["query"])
        self.assertEqual(params["properties"]["limit"]["type"], "integer")
        self.assertNotIn("nullable", params["properties"]["limit"])
        self.assertNotIn("default", params["properties"]["target"])
        self.assertIn("$defs", params)


if __name__ == "__main__":
    unittest.main()
