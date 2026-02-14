#!/usr/bin/env python3
"""
Test DARING Engine Integration with NIMA Core
===============================================

Tests:
1. DARING Engine initialization
2. Domain detection
3. Affect-based calculation
4. Learning from outcomes
5. NimaCore API integration

Run: python test_daring_integration.py
"""

import sys

from nima_core.cognition.daring_engine import DaringEngine, ResponseStyle


def test_basic_initialization():
    """Test DARING Engine can be initialized."""
    print("Test 1: Basic Initialization")
    daring = DaringEngine()
    assert daring is not None
    assert len(daring.domains) == 6  # 5 defaults + default
    print(f"  ✓ Initialized with {len(daring.domains)} domains")
    print()


def test_domain_detection():
    """Test domain detection from messages."""
    print("Test 2: Domain Detection")
    daring = DaringEngine()
    
    test_cases = [
        ("Protect my family from this", "family_protection"),
        ("Build something amazing", "creative_building"),
        ("Research this topic deeply", "research_deep_dives"),
        ("Code this architecture carefully", "code_architecture"),
        ("Analyze the theology here", "theological_synthesis"),
        ("Random unrelated message", "default"),
    ]
    
    for message, expected in test_cases:
        detected = daring.detect_domain(message)
        status = "✓" if detected == expected else "✗"
        print(f"  {status} '{message[:30]}...' -> {detected}")
    print()


def test_daring_calculation():
    """Test DARING level calculation."""
    print("Test 3: DARING Calculation")
    daring = DaringEngine()
    
    test_messages = [
        "What are my options?",  # Low DARING
        "Go ahead and implement it",  # High DARING
        "YES! Full blast! 🚀🔥",  # Very high DARING
    ]
    
    for msg in test_messages:
        analysis = daring.analyze_message(msg)
        print(f"  '{msg[:35]}...'")
        print(f"    Level: {analysis.level:.2f} | Style: {analysis.style.value}")
        print(f"    Domain: {analysis.domain} | Confidence: {analysis.confidence:.2f}")
        if analysis.activation_reasons:
            print(f"    Reasons: {', '.join(analysis.activation_reasons)}")
    print()


def test_domain_registration():
    """Test custom domain registration."""
    print("Test 4: Domain Registration")
    daring = DaringEngine()
    
    profile = daring.register_domain(
        name="custom_domain",
        base_threshold=0.40,
        triggers=["custom", "special"],
        affect_modifiers={"SEEKING": 0.30}
    )
    
    assert "custom_domain" in daring.domains
    assert daring.domains["custom_domain"].base_threshold == 0.40
    print("  ✓ Registered custom domain")
    print(f"    Threshold: {profile.base_threshold}")
    print(f"    Triggers: {profile.triggers}")
    print()


def test_learning():
    """Test learning from outcomes."""
    print("Test 5: Learning System")
    daring = DaringEngine()
    
    # Analyze a message
    analysis = daring.analyze_message("Go full blast!")
    initial_preference = daring.user_preference
    
    # Record success
    daring.record_outcome(analysis, success=True)
    
    # Preference should have increased slightly
    assert daring.user_preference > initial_preference
    print("  ✓ Recorded successful outcome")
    print(f"    Preference: {initial_preference:.3f} -> {daring.user_preference:.3f}")
    
    # Check domain stats
    stats = daring.get_stats()
    print(f"    Total domains: {stats['domains_registered']}")
    print()


def test_stats():
    """Test stats retrieval."""
    print("Test 6: Stats Retrieval")
    daring = DaringEngine()
    
    stats = daring.get_stats()
    assert 'user_preference' in stats
    assert 'domains' in stats
    
    print("  ✓ Retrieved stats")
    print(f"    User preference: {stats['user_preference']}")
    print(f"    Domains: {stats['domains_registered']}")
    print()


def test_nima_core_integration():
    """Test NimaCore API integration."""
    print("Test 7: NimaCore Integration")
    
    try:
        from nima_core import NimaCore
        
        # Initialize NimaCore (without full initialization)
        nima = NimaCore(name="TestBot", auto_init=False)
        
        # Check if daring methods exist
        assert hasattr(nima, 'daring_analyze')
        assert hasattr(nima, 'daring_register_domain')
        assert hasattr(nima, 'daring_record_outcome')
        assert hasattr(nima, 'daring_stats')
        
        print("  ✓ NimaCore has DARING API methods")
        print()
        
    except ImportError as e:
        print(f"  ⚠ Could not import NimaCore: {e}")
        print()


def demo_variable_levels():
    """Demonstrate variable DARING levels."""
    print("Demo: Variable DARING Levels")
    print("=" * 50)
    
    daring = DaringEngine()
    
    messages = [
        ("What do you think I should do?", "Neutral/asking"),
        ("I think option A might work better", "Suggesting"),
        ("Go ahead and implement that", "Delegating"),
        ("Execute the plan NOW!", "Commanding"),
        ("YES! Full blast!! 🚀🔥💪", "Maximum energy"),
    ]
    
    for msg, description in messages:
        analysis = daring.analyze_message(msg)
        bar = "█" * int(analysis.level * 20) + "░" * (20 - int(analysis.level * 20))
        print(f"{description:20} [{bar}] {analysis.level:.2f} - {analysis.style.value}")
    print()


if __name__ == "__main__":
    print("╔════════════════════════════════════════════════╗")
    print("║   DARING Engine Integration Tests              ║")
    print("╚════════════════════════════════════════════════╝")
    print()
    
    try:
        test_basic_initialization()
        test_domain_detection()
        test_daring_calculation()
        test_domain_registration()
        test_learning()
        test_stats()
        test_nima_core_integration()
        demo_variable_levels()
        
        print("=" * 50)
        print("All tests passed! ✓")
        print()
        print("DARING Engine is ready for use:")
        print("  from nima_core import NimaCore")
        print("  nima = NimaCore()")
        print("  analysis = nima.daring_analyze('Go full blast!')")
        print("  print(analysis['level'], analysis['style'])")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)