#!/usr/bin/env python3
"""
NIMA Capture Diagnostic Script
Run this to check if the capture pipeline is working
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("NIMA Capture Diagnostic Tool")
print("=" * 60)
print()

# Check 1: Python imports
print("[1/5] Checking Python imports...")
try:
    from nima_core import NimaCore
    print("   ✓ nima_core imports successfully")
except ImportError as e:
    print(f"   ✗ Failed to import nima_core: {e}")
    print("   → Fix: pip install nima-core or check PYTHONPATH")
    sys.exit(1)

# Check 2: Initialize NimaCore
print()
print("[2/5] Initializing NimaCore...")
try:
    nima = NimaCore()
    print("   ✓ NimaCore initialized")
    print(f"   → Config path: {nima.config.config_path}")
    print(f"   → Data path: {nima.config.data_path}")
except Exception as e:
    print(f"   ✗ Failed to initialize ({type(e).__name__}): {e}")
    sys.exit(1)

# Check 3: Config settings
print()
print("[3/5] Checking configuration...")
print(f"   → v2_enabled: {nima.config.v2_enabled}")
print(f"   → episodic_v2: {nima.config.episodic_v2}")
print(f"   → projection: {nima.config.projection}")
print(f"   → sparse_retrieval: {nima.config.sparse_retrieval}")

if not nima.config.v2_enabled:
    print("   ⚠️  WARNING: v2_enabled is False!")
    print("   → Fix: Set NIMA_V2_ENABLED=true or update config")

# Check 4: Memory count
print()
print("[4/5] Checking memory storage...")
try:
    if hasattr(nima, 'episodic') and hasattr(nima.episodic, 'memories'):
        count = len(nima.episodic.memories)
        print(f"   ✓ Current memories: {count}")
    else:
        print("   ⚠️  Cannot determine memory count")
except Exception as e:
    print(f"   ⚠️  Error checking memories: {e}")

# Check 5: Test capture
print()
print("[5/5] Testing capture pipeline...")
try:
    result = nima.capture(
        who="diagnostic",
        what="Test capture from diagnostic script",
        importance=0.1
    )
    print("   ✓ Capture successful!")
    print(f"   → Result: {result}")
    
    # Verify it was stored
    if hasattr(nima, 'episodic') and hasattr(nima.episodic, 'memories'):
        new_count = len(nima.episodic.memories)
        print(f"   → Memory count after capture: {new_count}")
        
except Exception as e:
    print(f"   ✗ Capture failed: {e}")
    print("   → This is the main issue!")
    import traceback
    traceback.print_exc()

# Summary
print()
print("=" * 60)
print("Summary:")
print("=" * 60)

# Check OpenClaw hooks
print()
print("[Bonus] Checking OpenClaw hooks...")
hook_dir = Path.home() / ".openclaw/extensions/nima-core/hooks"
if hook_dir.exists():
    hooks = list(hook_dir.iterdir())
    print("   ✓ Hook directory exists")
    print(f"   → Hooks found: {[h.name for h in hooks]}")
else:
    print(f"   ⚠️  Hook directory not found: {hook_dir}")
    print("   → Hooks may not be installed!")

print()
print("=" * 60)
print("Diagnostics complete!")
print("=" * 60)
