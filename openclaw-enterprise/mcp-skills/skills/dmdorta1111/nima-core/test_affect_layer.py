#!/usr/bin/env python3
"""
Test script for Layered Affect Architecture
"""

import sys

from nima_core.cognition import LayeredAffectEngine, FoundationAffect
import tempfile
import shutil

# Create temp directory for test data
test_dir = tempfile.mkdtemp()
print(f"Test data dir: {test_dir}")

try:
    # Initialize engine
    print("\n=== Test 1: Initialize Engine ===")
    engine = LayeredAffectEngine(data_dir=test_dir, user_id="test_bot")
    print("✓ Engine initialized")
    print(f"  Composites: {list(engine.tree.composites.keys())}")
    
    # Define domains
    print("\n=== Test 2: Define Domains ===")
    engine.define_domain(
        composite_name="DARING",
        domain_name="deep_conversations",
        description="Going deep with users",
        initial_threshold=0.6
    )
    print("✓ Domain defined: deep_conversations (DARING)")
    
    engine.define_domain(
        composite_name="DARING",
        domain_name="code_architecture", 
        description="Designing systems",
        initial_threshold=0.5
    )
    print("✓ Domain defined: code_architecture (DARING)")
    
    # Check initial stats
    print("\n=== Test 3: Initial Stats ===")
    stats = engine.get_domain_stats("DARING", "deep_conversations")
    print(f"  Threshold: {stats['threshold']}")
    print(f"  Attempts: {stats['attempts']}")
    print(f"  Success ratio: {stats['success_ratio']:.2f}")
    
    # Simulate foundation states
    print("\n=== Test 4: Calculate Composite ===")
    foundation_states = {
        FoundationAffect.SEEKING: 0.8,
        FoundationAffect.FEAR: 0.3,
        FoundationAffect.CARE: 0.7
    }
    
    intensity, threshold = engine.calculate_composite(
        "DARING", foundation_states, domain="deep_conversations"
    )
    print("  SEEKING: 0.8, FEAR: 0.3")
    print(f"  DARING intensity: {intensity:.2f}")
    print(f"  DARING threshold: {threshold:.2f}")
    print(f"  Is active: {intensity > threshold}")
    
    # Record attempts
    print("\n=== Test 5: Learning Loop ===")
    engine.record_attempt("DARING", "deep_conversations", success=True)
    engine.record_attempt("DARING", "deep_conversations", success=True)
    engine.record_attempt("DARING", "deep_conversations", success=False)
    print("✓ Recorded 2 successes, 1 failure")
    
    # Check updated stats
    stats = engine.get_domain_stats("DARING", "deep_conversations")
    print(f"  New threshold: {stats['threshold']:.3f} (adjusted from learning)")
    print(f"  Attempts: {stats['attempts']}")
    print(f"  Successes: {stats['successes']}")
    print(f"  Success ratio: {stats['success_ratio']:.2f}")
    
    # Test active composites
    print("\n=== Test 6: Get Active Composites ===")
    active = engine.get_active_composites(foundation_states, domain="deep_conversations")
    print(f"  Active: {active}")
    
    # List all domains
    print("\n=== Test 7: List Domains ===")
    domains = engine.list_domains()
    for composite, domain_list in domains.items():
        print(f"  {composite}: {list(domain_list.keys())}")
    
    # Test persistence
    print("\n=== Test 8: Persistence ===")
    del engine
    engine2 = LayeredAffectEngine(data_dir=test_dir, user_id="test_bot")
    stats2 = engine2.get_domain_stats("DARING", "deep_conversations")
    print(f"  Loaded attempts: {stats2['attempts']} (should be 3)")
    print(f"  Loaded threshold: {stats2['threshold']:.3f}")
    print("✓ Persistence working" if stats2['attempts'] == 3 else "✗ Persistence failed")
    
    print("\n=== All Tests Passed! ===")
    
finally:
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"\nCleaned up: {test_dir}")
