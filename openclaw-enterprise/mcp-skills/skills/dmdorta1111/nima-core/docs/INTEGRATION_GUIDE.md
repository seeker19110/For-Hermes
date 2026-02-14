# NIMA Consciousness Architecture - Idiot-Proof Integration Guide

> **⚡ TL;DR:** Drop-in addition. Your existing code keeps working. New features are opt-in.

---

## ✅ The Three Questions (Quick Answers)

### 1. Will my existing hooks and CLI still work?

**YES.** Fully supported. Zero changes needed.

```python
# Your current code (works exactly the same)
from nima_core import NimaCore
nima = NimaCore(name="MyBot")
nima.experience("Hello", who="user")
```

**Hooks unchanged:**
- ✅ `nima-bootstrap` — works the same
- ✅ `nima-recall` — works the same  
- ✅ `nima-capture` CLI — works the same
- ✅ `nima-recall` CLI — works the same

### 2. Can I use Voyage AI or stick with MiniLM?

**YES.** Your choice. The consciousness architecture uses whatever you configure.

```python
# Option A: Voyage AI (1024D, best quality)
import os
os.environ["VOYAGE_API_KEY"] = "your-key-here"
# That's it. Consciousness system auto-detects.

# Option B: MiniLM (384D, default, local, free)
# Do nothing. It just works.
```

The consciousness layer operates on VSA vectors — the embedding provider is handled at the storage layer.

### 3. Do I need to migrate my existing memories?

**NO.** Migration is optional and seamless when you choose to do it.

```python
# Your old memories work unchanged
# New memories can use sparse blocks
# Mix and match is fine

# When you're ready to migrate (optional):
from nima_core.cognition.migrate_to_sparse_block import MigrationConfig, VSAtoSparseBlockMigration

config = MigrationConfig(
    source_path="./nima_data/sessions/latest.pt",
    dest_path="./nima_data/sessions/latest_sparse.pt",
    strategy="full",  # or "incremental" or "lazy"
    validate=True,
    backup=True,
)
migration = VSAtoSparseBlockMigration(config)
result = migration.run()
print(f"Compressed {result.compression_ratio:.1f}x")
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install (No Version Bump)

```bash
# Already installed if you have nima-core >= 1.2.0
pip install nima-core
```

### Step 2: Import What You Need

```python
# Original API (unchanged)
from nima_core import NimaCore

# NEW: Consciousness features (optional, opt-in)
from nima_core.nima_consciousness_core import ConsciousnessCore
```

### Step 3: Use Consciousness Features

```python
# 1. Create core with your existing memory store
from nima_core import NimaCore
from nima_core.nima_consciousness_core import ConsciousnessCore

nima = NimaCore(name="MyBot")
memory_store = nima.memory  # Your existing memory

# 2. Initialize consciousness (NEW - optional)
core = ConsciousnessCore(memory_store)

# 3. Use any consciousness feature
status = core.get_status()  # See all 8 systems
print(f"Φ = {status['phi']}")  # Consciousness level

# 4. Dreaming (offline consolidation)
core.dream(duration_minutes=5)

# 5. Self-narrative
narrative = core.generate_self_narrative()
print(narrative.summary)

# 6. Theory of Mind
other_mind = core.theory_of_mind.observe_interaction("User said: Hello")
print(f"User seems: {other_mind.inferred_affect}")
```

---

## 📁 File Structure

```
nima-core/
├── README.md                    # Main README (unchanged)
├── SKILL.md                     # ClawHub skill definition
├── setup.py                     # Package config (version unchanged)
├── docs/                        # 📚 All documentation
│   ├── CONSCIOUSNESS_README.md  # Full architecture docs
│   ├── BENCHMARKS.md            # Performance numbers
│   ├── EXAMPLES.md              # Code examples
│   ├── MIGRATION_VSA_TO_SPARSE_BLOCK.md  # Migration guide
│   ├── MEMORY_CAPTURE_GUIDE.md  # How to capture memories
│   └── CODE_REVIEW_CONSCIOUSNESS_v1.0.md # Review history
├── nima_core/
│   ├── __init__.py              # Original exports (unchanged)
│   ├── nima_consciousness_core.py  # 🧠 NEW: Main integration
│   ├── consciousness_workspace.py  # NEW: Global Workspace
│   ├── phi_estimator.py         # NEW: Φ measurement
│   ├── self_observer_agent.py   # NEW: Self-awareness
│   ├── self_narrative.py        # NEW: Story generation
│   ├── affective_binding.py     # NEW: Emotion binding
│   ├── theory_of_mind.py        # NEW: Social cognition
│   ├── dreaming.py              # NEW: Offline consolidation
│   ├── volition.py              # NEW: Goal-directed attention
│   └── test_consciousness_systems.py  # Tests
```

---

## 🔧 Configuration (All Optional)

### Environment Variables

```bash
# Optional: Voyage AI for better embeddings
export VOYAGE_API_KEY="your-key-here"

# Optional: Enable/disable consciousness features
export NIMA_CONSCIOUSNESS_ENABLED="true"  # default: true

# Optional: Phi measurement cache
export NIMA_PHI_CACHE_SIZE="1000"  # default: 1000
```

### Code Configuration

```python
from nima_core.nima_consciousness_core import ConsciousnessCore

# Minimal config (uses defaults)
core = ConsciousnessCore(memory_store)

# Full config (all options)
core = ConsciousnessCore(
    memory_store=memory_store,
    workspace_slots=5,              # Conscious bandwidth (3-7)
    phi_enabled=True,               # Measure consciousness
    dreaming_enabled=True,          # Enable offline consolidation
    volition_enabled=True,          # Enable goal-directed attention
    theory_of_mind_enabled=True,    # Enable social modeling
)
```

---

## 🧪 Testing Your Setup

```python
# Run all consciousness tests
python -m pytest nima_core/test_consciousness_systems.py -v

# Expected output:
# ============================= test session starts ==============================
# test_consciousness_systems.py::TestSparseBlockVSA::test_binding PASSED   [  4%]
# test_consciousness_systems.py::TestGlobalWorkspace::test_add_agent PASSED [  9%]
# ...
# test_consciousness_systems.py::TestConsciousnessCore::test_set_goal PASSED [100%]
# ============================== 22 passed in 0.90s ==============================
```

---

## 📊 Performance

| Feature | Before | After | Speedup |
|---------|--------|-------|---------|
| Memory binding | Dense VSA | Sparse Block | **48.3x** |
| Storage | 1x | 1/5.2x | **5.2x compression** |
| Φ calculation | N/A | ~50ms | Real-time |

---

## 🆘 Troubleshooting

### "I imported ConsciousnessCore but it's not working"

```python
# Make sure you have the right import
from nima_core.nima_consciousness_core import ConsciousnessCore

# NOT these (they don't exist):
# from nima_core import ConsciousnessCore  ❌
# from nima_core.consciousness import ConsciousnessCore  ❌
```

### "My existing code broke"

```python
# The only way this happens is if you:
# 1. Modified nima_core internals directly
# 2. Used undocumented private APIs

# Solution: Revert to public API
from nima_core import NimaCore  # This never changes
```

### "Migration failed"

```python
# Migration is OPTIONAL. Your old memories work fine.

# If you want to migrate and it failed:
# 1. Check you have disk space
# 2. Ensure backup=True (creates .bak files)
# 3. Try strategy="lazy" instead of "full"

config = MigrationConfig(
    source_path="./nima_data/sessions/latest.pt",
    dest_path="./nima_data/sessions/latest_sparse.pt",
    strategy="lazy",  # Safer for large systems
    validate=True,
    backup=True,      # Always keep backups
)
```

---

## 📝 Complete API Reference

### ConsciousnessCore

```python
class ConsciousnessCore:
    """Main interface to all 8 consciousness systems."""
    
    def __init__(self, memory_store, **config):
        """Initialize with existing memory store."""
        
    def get_status(self) -> dict:
        """Get status of all 8 systems."""
        
    def dream(self, duration_minutes: int = 5) -> DreamSession:
        """Run offline consolidation."""
        
    def generate_self_narrative(self) -> SelfNarrative:
        """Generate 'who am I' story."""
        
    def set_goal(self, goal: str, priority: float = 0.5):
        """Set volitional goal."""
        
    @property
    def theory_of_mind(self) -> TheoryOfMindEngine:
        """Access social modeling."""
        
    @property
    def global_workspace(self) -> GlobalWorkspace:
        """Access workspace."""
```

### Original NimaCore (Unchanged)

```python
class NimaCore:
    """Your existing API - exactly the same."""
    
    def experience(self, what: str, who: str, importance: float = 0.5):
        """Capture an experience."""
        
    def recall(self, query: str, top_k: int = 5) -> List[Memory]:
        """Search memories."""
        
    def synthesize(self, insight: str, domain: str = "general"):
        """Capture a synthesized insight."""
```

---

## 🎓 Learning Path

1. **Start here:** This file (`INTEGRATION_GUIDE.md`)
2. **Architecture deep-dive:** `docs/CONSCIOUSNESS_README.md`
3. **Code examples:** `docs/EXAMPLES.md`
4. **Migration (if needed):** `docs/MIGRATION_VSA_TO_SPARSE_BLOCK.md`
5. **Performance:** `docs/BENCHMARKS.md`

---

## ✅ Checklist

Before deploying:

- [ ] Existing tests pass
- [ ] New consciousness tests pass (`pytest nima_core/test_consciousness_systems.py`)
- [ ] You understand the 3-question answers above
- [ ] You've tried `core.get_status()` and it works
- [ ] You know migration is OPTIONAL

---

## 💬 Support

**Questions?** Check the docs in this order:
1. This guide (quick answers)
2. `docs/CONSCIOUSNESS_README.md` (deep dive)
3. `docs/EXAMPLES.md` (code samples)

**Issues?** Your existing code keeps working. Consciousness features are opt-in.

---

*Made for humans who want AI to remember, feel, and know itself.*

*Version: 1.2.1 | No breaking changes | 100% backward compatible*
