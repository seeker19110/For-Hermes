# NIMA Core v1.2.0 - Usage Examples

## Quick Start

```python
from nima_core import NimaCore

nima = NimaCore(name="MyBot")
nima.experience("User asked about Python", who="Alice", importance=0.7)
```

## Async Affective Processing

```python
from nima_core.cognition import analyze_async

# Fast analysis (50,000x speedup when cached)
result = analyze_async("I'm scared but need to do this")
print(result.engine)   # COURAGE
print(result.level)    # 0.57
print(result.style)    # cautious
```

## Lazy VSA Loading

```python
from nima_core.embeddings import get_embedder, is_loaded, memory_usage_mb

# Create embedder (doesn't load yet)
embedder = get_embedder()
print(is_loaded())        # False
print(memory_usage_mb())  # 0.0 MB

# Explicitly load when needed
embedder.load()
print(memory_usage_mb())  # ~173 MB

# Free memory when done
embedder.unload()
```

## All 4 Affective Engines

```python
from nima_core.cognition import (
    DaringEngine, CourageEngine,
    NurturingEngine, MasteryEngine
)

daring = DaringEngine()
courage = CourageEngine()
nurturing = NurturingEngine()
mastery = MasteryEngine()

# Analyze messages
result = daring.analyze_message("Go full blast!")
print(result.level)  # 0.61
```

## Response Modulation

```python
from nima_core.cognition import DaringResponseModulator
from nima_core import NimaCore

nima = NimaCore()
modulator = DaringResponseModulator(nima)

guidance = modulator.generate_response_guidance(
    "Help me understand theology"
)
print(guidance.engine)  # DARING
print(guidance.style)   # bold
print(guidance.tone_guidance)  # direct
```

## Environment Variables

```bash
# Lazy loading (default: true)
export NIMA_LAZY_LOAD=true

# Projection (default: true)
export NIMA_PROJECTION=true

# Voyage AI (optional)
export VOYAGE_API_KEY="your-key-here"
```
