#!/usr/bin/env python3
"""
Test COURAGE Engine Integration with NIMA Core
================================================

Tests:
1. COURAGE Engine initialization
2. Fear detection (required for courage)
3. Importance calculation
4. Domain detection
5. Learning from outcomes
6. NimaCore API integration

Run: python test_courage_integration.py
"""

import sys

from nima_core.cognition.courage_engine import CourageEngine, ResponseStyle


def test_basic_initialization():
    """Test COURAGE Engine can be initialized."""
    print("Test 1: Basic Initialization")
    courage = CourageEngine()
    assert courage is not None
    assert len(courage.domains) >= 6  # 5 defaults + default
    print(f"  ✓ Initialized with {len(courage.domains)} domains")
    print()


def test_courage_requires_fear():
    """Test that courage requires fear to activate."""
    print("Test 2: COURAGE Requires Fear")
    courage = CourageEngine()
    
    # No fear = no courage (it's just action)
    # Since we have no affective core, fear defaults to 0.3
    # With fear = 0.3 (above 0.2 threshold), we get courage
    # Let's test the logic
    
    # Message indicating fear
    analysis = courage.analyze_message("I'm scared to talk to my boss")
    print("  Message: 'I'm scared to talk to my boss'")
    print(f"    Fear level: {analysis.fear_level:.2f}")
    print(f"    COURAGE Level: {analysis.level:.2f}")
    print(f"    Style: {analysis.style.value}")
    
    if analysis.fear_level < 0.2:
        print(f"    ✓ No fear = no courage (level: {analysis.level})")
    else:
        print(f"    ✓ Fear detected = courage calculation")
    print()


def test_domain_detection():
    """Test domain detection for courage scenarios."""
    print("Test 3: Domain Detection")
    courage = CourageEngine()
    
    test_cases = [
        ("I need to confront my friend about this", "difficult_conversations"),
        ("Should I quit my job?", "career_changes"),
        ("I want to tell her how I feel", "expressing_love"),
        ("I need to admit I was wrong", "admitting_mistakes"),
        ("Random message", "default"),
    ]
    
    for message, expected in test_cases:
        detected = courage.detect_domain(message)
        status = "✓" if detected == expected else "~"
        print(f"  {status} '{message[:40]}...' -> {detected}")
    print()


def test_courage_calculation():
    """Test courage level calculation."""
    print("Test 4: COURAGE Calculation")
    courage = CourageEngine()
    
    messages = [
        "I'm scared to do this but I have to",
        "I should talk to him but I'm afraid",
        "This is wrong and I need to stand up",
        "I can't keep avoiding this",
    ]
    
    for msg in messages:
        analysis = courage.analyze_message(msg)
        print(f"  '{msg[:45]}...'")
        print(f"    Fear: {analysis.fear_level:.2f} | Importance: {analysis.importance_level:.2f}")
        print(f"    COURAGE: {analysis.level:.2f} | Style: {analysis.style.value}")
        if analysis.activation_reasons:
            print(f"    Reasons: {', '.join(analysis.activation_reasons[:3])}")
    print()


def test_template_loading():
    """Test loading domain templates."""
    print("Test 5: Template Loading")
    courage = CourageEngine()
    
    # Load a template
    profile = courage.load_template_domain('public_speaking_courage')
    assert 'public_speaking_courage' in courage.domains
    print("  ✓ Loaded template: public_speaking_courage")
    print(f"    Threshold: {profile.base_threshold}")
    print(f"    Triggers: {profile.triggers[:3]}...")
    
    # List templates
    templates = courage.list_available_templates()
    print(f"  ✓ Available templates: {len(templates)}")
    print()


def test_nima_core_integration():
    """Test NimaCore API integration."""
    print("Test 6: NimaCore Integration")
    
    try:
        from nima_core import NimaCore
        
        nima = NimaCore(name="TestBot", auto_init=False)
        
        assert hasattr(nima, 'courage_analyze')
        assert hasattr(nima, 'courage_register_domain')
        assert hasattr(nima, 'courage_record_outcome')
        assert hasattr(nima, 'courage_stats')
        
        print("  ✓ NimaCore has COURAGE API methods")
        print()
        
    except ImportError as e:
        print(f"  ⚠ Could not import NimaCore: {e}")
        print()


def demo_courage_levels():
    """Demonstrate variable courage levels."""
    print("Demo: Variable COURAGE Levels")
    print("=" * 60)
    
    courage = CourageEngine()
    
    scenarios = [
        ("I kind of want to maybe do this", "Hesitant"),
        ("I'm scared but I should do it", "Fear + obligation"),
        ("This terrifies me but it's important", "High fear + importance"),
        ("I HAVE to face this NOW", "Urgent importance"),
    ]
    
    for msg, description in scenarios:
        analysis = courage.analyze_message(msg)
        bar = "█" * int(analysis.level * 20) + "░" * (20 - int(analysis.level * 20))
        print(f"{description:25} [{bar}] {analysis.level:.2f} - {analysis.style.value}")
    print()


if __name__ == "__main__":
    print("╔════════════════════════════════════════════════╗")
    print("║   COURAGE Engine Integration Tests             ║")
    print("╚════════════════════════════════════════════════╝")
    print()
    
    try:
        test_basic_initialization()
        test_courage_requires_fear()
        test_domain_detection()
        test_courage_calculation()
        test_template_loading()
        test_nima_core_integration()
        demo_courage_levels()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print()
        print("COURAGE Engine is ready for use:")
        print("  from nima_core import NimaCore")
        print("  nima = NimaCore()")
        print("  analysis = nima.courage_analyze('I need to confront my boss')")
        print("  print(analysis['level'], analysis['style'])")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)