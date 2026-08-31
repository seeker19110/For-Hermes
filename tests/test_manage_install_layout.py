"""Regression tests for invoking manage.py from its installed layout."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_manage_module():
    if "tools.antigravity_bridge" not in sys.modules:
        tools_pkg = types.ModuleType("tools")
        tools_pkg.__path__ = []
        bridge_pkg = types.ModuleType("tools.antigravity_bridge")
        bridge_pkg.__path__ = [str(ROOT / "bridge")]
        sys.modules.setdefault("tools", tools_pkg)
        sys.modules["tools.antigravity_bridge"] = bridge_pkg

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    spec = importlib.util.spec_from_file_location("antigravity_manage_install", ROOT / "manage.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


manage = load_manage_module()


class InstalledLayoutInstallTests(unittest.TestCase):
    def test_install_from_installed_layout_preserves_runtime(self) -> None:
        """`manage.py setup` must not delete its only installed bridge source."""
        with tempfile.TemporaryDirectory() as tmp:
            hermes_dir = Path(tmp) / "hermes"
            installed_root = hermes_dir / "bridge" / "antigravity"
            runtime = installed_root / "tools" / "antigravity_bridge"
            runtime.mkdir(parents=True)
            sentinel = runtime / "server.py"
            sentinel.write_text("# existing runtime\n", encoding="utf-8")

            with (
                mock.patch.object(manage, "PLUGIN_ROOT", installed_root),
                mock.patch.object(manage, "REPO_ROOT", hermes_dir),
                mock.patch.object(manage, "get_hermes_dir", return_value=hermes_dir),
                mock.patch.object(manage, "_ensure_core_registrations"),
            ):
                result = manage.cmd_install(SimpleNamespace())

            self.assertEqual(result, 0)
            self.assertTrue(sentinel.is_file())


if __name__ == "__main__":
    unittest.main()
