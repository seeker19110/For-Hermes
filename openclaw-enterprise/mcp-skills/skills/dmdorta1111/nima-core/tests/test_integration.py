#!/usr/bin/env python3
"""Basic integration test for nima-core package."""

import sys
import os

# Add parent to path for development (before pip install -e .)
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all modules import correctly."""
    print("1. Testing imports...")
    from nima_core import NimaCore, NimaConfig, get_config
    from nima_core.layers.affective_core import SubcorticalAffectiveCore
    from nima_core.layers.binding_layer import VSABindingLayer
    from nima_core.config.nima_config import should_use_v2_for
    print("   ✅ All imports OK")


def test_config():
    """Test config loading."""
    print("2. Testing config...")
    from nima_core.config.nima_config import NimaConfig
    cfg = NimaConfig()
    assert cfg.sparse_retrieval == True
    assert cfg.projection == True
    print(f"   ✅ Config OK: {cfg.to_dict()}")


def test_nima_core():
    """Test NimaCore initialization."""
    print("3. Testing NimaCore...")
    os.environ["NIMA_DATA_DIR"] = "/tmp/nima_test_data"
    os.environ["NIMA_V2_ALL"] = "false"  # Don't need full stack for import test
    
    from nima_core import NimaCore
    nima = NimaCore(name="TestBot", data_dir="/tmp/nima_test_data", auto_init=False)
    assert nima.name == "TestBot"
    
    status = nima.status()
    assert status["name"] == "TestBot"
    print(f"   ✅ NimaCore OK: {status['name']}, memories={status['memory_count']}")


def test_affective_core():
    """Test affective processing."""
    print("4. Testing Affective Core...")
    import numpy as np
    from nima_core.layers.affective_core import SubcorticalAffectiveCore
    
    core = SubcorticalAffectiveCore(storage_path=None)
    stimulus = np.random.randn(128)
    state = core.process(stimulus, {"text": "I love learning new things!", "who": "user"})
    assert state.dominant is not None
    print(f"   ✅ Affect: dominant={state.dominant}, valence={state.valence:.2f}")


def test_binding_layer():
    """Test VSA binding."""
    print("5. Testing Binding Layer...")
    from nima_core.layers.binding_layer import VSABindingLayer
    
    layer = VSABindingLayer(dimension=1000)
    episode = layer.create_episode({"WHO": "Alice", "WHAT": "asked a question"})
    assert episode.vector is not None
    print(f"   ✅ Binding: episode norm={float(episode.vector.__abs__().sum()):.2f}")


def test_experience_recall_roundtrip():
    """Test full capture/recall data flow."""
    print("6. Testing Experience Recall Roundtrip...")
    import tempfile
    import shutil
    from nima_core import NimaCore
    
    # Use temp directory for test
    temp_dir = tempfile.mkdtemp()
    try:
        os.environ["NIMA_V2_ALL"] = "false"
        os.environ["NIMA_DATA_DIR"] = temp_dir
        
        nima = NimaCore(name="TestBot", data_dir=temp_dir, auto_init=False)
        
        # Capture memories
        nima.capture("TestUser", "The weather is sunny today", importance=0.8)
        nima.capture("TestUser", "I love programming in Python", importance=0.7)
        
        # Verify status
        status = nima.status()
        assert status["memory_count"] >= 2, f"Expected >= 2 memories, got {status['memory_count']}"
        print(f"   ✓ Captured {status['memory_count']} memories")
        
        # Recall with text search fallback
        results = nima.recall("weather", top_k=5)
        assert len(results) > 0, "Recall returned no results"
        
        # Check if results contain weather-related content
        found_weather = any(
            "sunny" in str(r.get("what", "")).lower() or 
            "weather" in str(r.get("what", "")).lower()
            for r in results
        )
        assert found_weather, "Results don't contain expected weather content"
        print(f"   ✓ Recalled {len(results)} memories, found weather content")
        
        print("   ✅ Roundtrip test passed")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_introspect():
    """Test metacognitive introspection."""
    print("7. Testing Introspection...")
    import tempfile
    import shutil
    from nima_core import NimaCore
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Enable metacognitive layer
        os.environ["NIMA_V2_ALL"] = "false"
        os.environ["NIMA_V2_META"] = "true"
        os.environ["NIMA_DATA_DIR"] = temp_dir
        
        nima = NimaCore(name="TestBot", data_dir=temp_dir, auto_init=True)
        
        # Call introspect
        result = nima.introspect()
        
        if result is None:
            print("   ⚠️  Metacognitive layer not available (optional component)")
            return
        
        # Verify expected keys
        assert isinstance(result, dict), "Introspect should return dict"
        expected_keys = ["identity", "working_memory"]
        for key in expected_keys:
            if key not in result:
                print(f"   ⚠️  Missing key '{key}' in introspection result")
        
        print(f"   ✓ Introspection returned: {list(result.keys())}")
        print("   ✅ Introspection test passed")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        os.environ.pop("NIMA_V2_META", None)


def test_dream_engine():
    """Test dream consolidation engine."""
    print("8. Testing Dream Engine...")
    import tempfile
    import shutil
    from nima_core import NimaCore
    
    temp_dir = tempfile.mkdtemp()
    try:
        os.environ["NIMA_V2_ALL"] = "false"
        os.environ["NIMA_DATA_DIR"] = temp_dir
        
        nima = NimaCore(name="TestBot", data_dir=temp_dir, auto_init=False)
        
        # Capture varied memories across different domains and people
        nima.capture("Alice", "I wrote a new algorithm for sorting data efficiently", importance=0.8)
        nima.capture("Bob", "The team meeting about the project deadline went well", importance=0.7)
        nima.capture("Alice", "I'm feeling really excited about the architecture redesign", importance=0.9)
        nima.capture("Charlie", "We need to plan the schedule for next week's tasks", importance=0.6)
        nima.capture("Bob", "The relationship between the frontend and backend code is interesting", importance=0.7)
        nima.capture("Alice", "I had a wonderful idea for a creative design pattern", importance=0.85)
        nima.capture("Diana", "The meaning of consciousness in AI systems fascinates me", importance=0.75)
        
        # Verify memories stored
        status = nima.status()
        assert status["memory_count"] >= 5, f"Expected >= 5 memories, got {status['memory_count']}"
        print(f"   ✓ Captured {status['memory_count']} memories")
        
        # Run dream consolidation
        result = nima.dream(hours=24)
        
        # Verify result structure
        assert result["status"] == "complete", f"Dream status: {result['status']}"
        assert result["memories_processed"] > 0, "No memories processed"
        assert "patterns" in result, "Missing 'patterns' key in result"
        assert "insights" in result, "Missing 'insights' key in result"
        assert "schemas" in result, "Missing 'schemas' key in result"
        assert "summary" in result, "Missing 'summary' key in result"
        
        print(f"   ✓ Dream processed {result['memories_processed']} memories")
        print(f"   ✓ Found {len(result['patterns'])} patterns")
        print(f"   ✓ Generated {len(result['insights'])} insights")
        print(f"   ✓ Extracted {result['schemas']} schemas")
        print(f"   ✓ Summary: {result['summary']}")
        
        # Test DreamEngine directly for deeper checks
        from nima_core.cognition.dream_engine import DreamEngine
        
        engine = DreamEngine(data_dir=temp_dir, nima_core=nima)
        summary = engine.get_summary()
        assert isinstance(summary, dict), "get_summary should return dict"
        assert "total_patterns" in summary, "Missing total_patterns in summary"
        print(f"   ✓ Engine summary: {summary['total_patterns']} patterns, {summary['total_insights']} insights")
        
        print("   ✅ Dream Engine test passed")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("=" * 50)
    print("NIMA Core Integration Test")
    print("=" * 50)
    
    tests = [
        test_imports, 
        test_config, 
        test_nima_core, 
        test_affective_core, 
        test_binding_layer,
        test_experience_recall_roundtrip,
        test_introspect,
        test_dream_engine,
    ]
    passed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{len(tests)} passed")
    print("=" * 50)
    
    # Exit with appropriate code
    sys.exit(0 if passed == len(tests) else 1)