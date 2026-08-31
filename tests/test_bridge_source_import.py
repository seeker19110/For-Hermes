"""Regression test: `bridge` package must import from the SOURCE layout too.

`bridge/__init__.py` previously imported unconditionally via the
`tools.antigravity_bridge.*` identity (the installed layout), which broke any
direct `import bridge` from a cloned/uninstalled checkout — including
`manage.py`'s own local-module import path used by `install.py` step 5.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bridge_package_imports_in_a_clean_subprocess_without_tools_shim() -> None:
    """A fresh interpreter with ONLY the repo root on sys.path must be able to
    `import bridge` and reach its public API — no pre-registered
    `tools.antigravity_bridge` shim, matching how `install.py` imports
    `manage.py` (which does `import bridge`) directly from source.
    """
    code = (
        "import sys; sys.path.insert(0, r'" + str(ROOT) + "'); "
        "import bridge; "
        "assert bridge.AntigravityAuthManager is not None; "
        "assert bridge.AntigravityClient is not None; "
        "print('OK')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


if __name__ == "__main__":
    test_bridge_package_imports_in_a_clean_subprocess_without_tools_shim()
    print("test_bridge_package_imports_in_a_clean_subprocess_without_tools_shim: OK")
