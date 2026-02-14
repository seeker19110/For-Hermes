"""
Example: Layered Affect Architecture Usage

This demonstrates how ANY bot using nima-core can define their own
affect personality through experience.
"""

from nima_core.cognition import LayeredAffectEngine, FoundationAffect

# Initialize the affect engine
engine = LayeredAffectEngine(
    data_dir="./my_affect_data",
    user_id="my_bot"
)

# Define your own domains (personal to YOUR bot)
engine.define_domain(
    composite_name="DARING",
    domain_name="deep_conversations",
    description="Going deep with users on complex topics",
    initial_threshold=0.6
)

engine.define_domain(
    composite_name="DARING", 
    domain_name="code_architecture",
    description="Designing new systems and architectures",
    initial_threshold=0.5  # More comfortable here
)

# Simulate experiences and learn from them
engine.record_attempt("DARING", "deep_conversations", success=True)
engine.record_attempt("DARING", "deep_conversations", success=True)
engine.record_attempt("DARING", "deep_conversations", success=False)
# After 2 successes, 1 failure:
# - threshold adjusts from 0.6 toward learned value
# - success_ratio = 0.67

# Check current foundation states (from your detection system)
foundation_states = {
    FoundationAffect.SEEKING: 0.8,
    FoundationAffect.FEAR: 0.3,
    FoundationAffect.CARE: 0.7
}

# Calculate if DARING is active for a specific domain
intensity, threshold = engine.calculate_composite(
    "DARING", 
    foundation_states,
    domain="deep_conversations"
)
print(f"DARING intensity: {intensity:.2f}, threshold: {threshold:.2f}")
print(f"Is active: {intensity > threshold}")

# Get all active composites
active = engine.get_active_composites(foundation_states, domain="deep_conversations")
print(f"Active affects: {active}")

# Check domain stats
stats = engine.get_domain_stats("DARING", "deep_conversations")
print(f"Domain stats: {stats}")

# List all your defined domains
domains = engine.list_domains()
print(f"All domains: {domains}")
