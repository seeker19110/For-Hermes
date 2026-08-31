#!/usr/bin/env python3
"""1-Click Standalone Installer for Hermes Antigravity OAuth Plugin.

Works on:
- Local machines (Windows, macOS, Linux)
- Cloud / VPS (Oracle Cloud, Ubuntu, Debian, CentOS, Docker)

Usage:
  python install.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent

def get_hermes_home() -> Path:
    hermes_home = os.environ.get("HERMES_HOME")
    if hermes_home:
        return Path(hermes_home).expanduser().resolve()
    return Path.home() / ".hermes"

def main():
    print("=" * 65)
    print("   HERMES AGENT - GOOGLE ANTIGRAVITY OAUTH PLUGIN INSTALLER   ")
    print("=" * 65)

    hermes_dir = get_hermes_home()
    hermes_dir.mkdir(parents=True, exist_ok=True)

    # 1. Install Plugin
    plugin_dest = hermes_dir / "plugins" / "model-providers" / "antigravity"
    plugin_src = PACKAGE_DIR / "plugin"
    print(f"\n[1/4] Installing Provider Plugin to {plugin_dest}...")
    plugin_dest.mkdir(parents=True, exist_ok=True)
    for f in plugin_src.glob("*"):
        if f.is_file():
            shutil.copy2(f, plugin_dest / f.name)
            print(f"      + Copied {f.name}")

    # 2. Install Bridge Engine
    bridge_dest = hermes_dir / "bridge" / "antigravity" / "tools" / "antigravity_bridge"
    bridge_src = PACKAGE_DIR / "bridge"
    print(f"\n[2/4] Installing Bridge Runtime Engine to {bridge_dest}...")
    bridge_dest.parent.mkdir(parents=True, exist_ok=True)
    if bridge_dest.exists():
        shutil.rmtree(bridge_dest, ignore_errors=True)
    shutil.copytree(bridge_src, bridge_dest)
    print(f"      + Copied Bridge Engine files.")

    # 3. Copy Manager
    shutil.copy2(PACKAGE_DIR / "manage.py", hermes_dir / "bridge" / "antigravity" / "manage.py")
    print(f"\n[3/4] Installed Management CLI at {hermes_dir / 'bridge' / 'antigravity' / 'manage.py'}")

    # 4. In-Repo synchronization (if executed from inside a hermes-agent git repo)
    repo_candidate = PACKAGE_DIR.parent
    if (repo_candidate / "run_agent.py").is_file() and (repo_candidate / "hermes_cli").is_dir():
        print(f"\n[4/5] Synchronizing with local workspace repository ({repo_candidate})...")
        repo_plugin = repo_candidate / "plugins" / "model-providers" / "antigravity"
        repo_tools = repo_candidate / "tools" / "antigravity_bridge"
        repo_plugin.mkdir(parents=True, exist_ok=True)
        for f in plugin_src.glob("*"):
            if f.is_file():
                shutil.copy2(f, repo_plugin / f.name)
        if repo_tools.exists():
            shutil.rmtree(repo_tools, ignore_errors=True)
        shutil.copytree(bridge_src, repo_tools)
        print("      + Workspace repository fully synchronized.")
    else:
        print(f"\n[4/5] Standalone environment installation complete.")

    # 5. Zero-touch failover: make Hermes use Antigravity as primary (on a
    #    fresh install only — an existing configured primary is left alone)
    #    and automatically rotate to openai-codex then anthropic on rate
    #    limit / quota / auth failure. No manual `hermes fallback add` needed,
    #    and re-running this installer on an upgrade never resets a primary
    #    provider the user already configured.
    print(f"\n[5/5] Configuring automatic cross-provider failover...")
    try:
        sys.path.insert(0, str(PACKAGE_DIR))
        import manage as _manage  # local module, see manage.py

        _manage.configure_priority_fallback_preserving_existing_primary(hermes_dir)
        print("      + fallback_providers: antigravity -> openai-codex -> anthropic (auto-tried on failure)")
        print("      + Existing primary provider preserved if you already had one configured.")
        print("      + No further action needed to enable automatic rotation.")
    except Exception as exc:
        print(f"      ! Could not auto-configure failover: {exc}")
        print("      Run 'python manage.py setup' manually to finish configuration.")

    print("\n" + "=" * 65)
    print(" INSTALLATION COMPLETED SUCCESSFULLY!")
    print("=" * 65)
    print("\nNext Steps:")
    print("  1. Log in with your Google account(s):")
    print("     python manage.py login       (repeat for additional accounts)")
    print("  2. Start bridge server daemon:")
    print("     python manage.py start")
    print("  3. Chat — Hermes already uses Antigravity as primary, with")
    print("     automatic openai-codex -> anthropic failover on rate limit.")
    print("     (Run 'python manage.py setup --no-fallback' to opt out of the")
    print("      automatic cross-provider chain, or --as-fallback-only to keep")
    print("      your existing primary provider and only add antigravity as a")
    print("      fallback option instead of the new primary.)")
    print("=" * 65)

if __name__ == "__main__":
    main()
