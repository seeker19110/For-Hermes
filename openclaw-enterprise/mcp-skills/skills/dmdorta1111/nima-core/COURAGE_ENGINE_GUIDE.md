# COURAGE Engine — Integration Guide

## Overview

The COURAGE Engine provides **fear-overcoming response modulation** integrated with NIMA Core's affective layer. It automatically calculates appropriate COURAGE levels (0.0 = avoidant to 1.0 = fearless action) for **feared-but-important tasks**.

**Key Insight:** COURAGE requires fear. Without fear, it's not courage—it's just action.

## COURAGE vs DARING

| | DARING | COURAGE |
|---|---|---|
| **Core Question** | "Should I do this?" | "Can I do this despite fear?" |
| **Required Affect** | SEEKING, PLAY, low FEAR | FEAR + CARE/SEEKING |
| **When High** | "Go for it!" | "Face it anyway!" |
| **When Low** | "Here are options..." | "Maybe we shouldn't..." |
| **Use Case** | Confident decisions | Fear-overcoming actions |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Foundation (Panksepp 7)                           │
│  SEEKING, RAGE, FEAR, LUST, CARE, PANIC, PLAY              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: COURAGE Composite                                 │
│  Formula: FEAR(0.40) + CARE(0.35) + SEEKING(0.20) +        │
│           LUST(0.15) + RAGE(0.10) + PLAY(0.05) -           │
│           PANIC(0.50)                                       │
│                                                             │
│  Key: Must have FEAR > 0.2, otherwise returns 0           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: Domain Modulation + Learning                      │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from nima_core import NimaCore

nima = NimaCore(name="MyBot")

# Analyze feared-but-important task
analysis = nima.courage_analyze("I'm scared to confront my boss about this")
print(f"COURAGE Level: {analysis['level']}")      # 0.68
print(f"Fear Level: {analysis['fear_level']}")    # 0.72
print(f"Importance: {analysis['importance_level']}") # 0.65
print(f"Style: {analysis['style']}")              # "bold"
```

## Response Styles

| Level | Style | Example Response |
|-------|-------|------------------|
| 0.0-0.25 | avoidant | "Maybe we shouldn't do this..." |
| 0.25-0.50 | cautious | "Let's think carefully about the risks..." |
| 0.50-0.70 | encouraging | "You can do this. Here's a plan..." |
| 0.70-0.90 | bold | "Face it. Now. Here's why..." |
| 0.90-1.0 | fearless | "Absolutely do this. No hesitation." |

## Built-in Domains

| Domain | Threshold | Use Case |
|--------|-----------|----------|
| difficult_conversations | 0.45 | Confrontations, hard talks |
| moral_stands | 0.40 | Ethics, defending others |
| vulnerability | 0.50 | Opening up, admitting mistakes |
| risk_taking | 0.55 | Calculated risks |
| leadership_challenges | 0.50 | Leading despite uncertainty |

## Generic Domain Templates

### Confrontation & Conflict
- `confronting_someone`, `admitting_mistakes`, `asking_for_help`, `saying_no`

### Emotional Risk
- `expressing_love`, `sharing_insecurities`, `grief_expression`

### Moral & Ethical
- `whistleblowing`, `defending_others`, `admitting_ignorance`

### Career & Professional
- `career_changes`, `salary_negotiation`, `public_speaking_courage`, `starting_business`

### Personal Growth
- `ending_relationships`, `setting_boundaries`, `therapy_counseling`

### Health & Safety
- `medical_procedures`, `addiction_recovery`

### Creative Risk
- `publishing_work`, `artistic_expression`

### Social Risk
- `meeting_new_people`, `apologizing`, `forgiving`

## Template Usage

```python
# Load a pre-configured template
nima._courage.load_template_domain('difficult_conversations')

# Load with custom name
nima._courage.load_template_domain('expressing_love', 'romantic_confession')

# List all available templates
templates = nima._courage.list_available_templates()

# 25+ templates available across all categories
```

## Custom Domain Registration

```python
nima.courage_register_domain(
    name="my_confrontation",
    base_threshold=0.45,
    triggers=['confront', 'challenge', 'disagree'],
    affect_modifiers={
        'CARE': 0.25,    # High care = more courage
        'FEAR': 0.15,    # Fear acknowledged
        'RAGE': 0.10     # Frustration helps
    }
)
```

## Activation Signals

| Signal | Pattern | Weight |
|--------|---------|--------|
| fear_language | "scared, afraid, nervous" | +0.35 |
| importance | "matter, important, care" | +0.30 |
| avoidance | "avoid, hide, ignore" | +0.25 |
| difficulty | "hard, difficult, scary" | +0.20 |
| should_do | "should, need to, must" | +0.25 |
| procrastination | "put off, later, someday" | +0.20 |
| regret | "regret, wish I had" | +0.30 |

## Learning System

```python
# Analyze first
analysis = nima.courage_analyze("I need to tell the truth")

# User acts on it
# ... user confronts the situation ...

# Record outcome
nima.courage_record_outcome(analysis, success=True)
# Engine learns: truth-telling = positive outcome
```

## Stats & Monitoring

```python
stats = nima.courage_stats()
print(stats)
# {
#   'user_preference': 0.62,
#   'domains_registered': 30,
#   'domains': {
#     'difficult_conversations': {
#       'attempts': 8,
#       'successes': 7,
#       'success_rate': 0.88
#     },
#     ...
#   }
# }
```

## Comparison: When to Use DARING vs COURAGE

### Use DARING When:
- User is confident but deciding between options
- "Which approach should I take?"
- Energy is high, just needs direction
- "Go full blast!" → DARING

### Use COURAGE When:
- User is afraid but knows they should act
- "I'm scared to do this but I have to"
- Fear is present, importance is high
- "Face your fear" → COURAGE

### Combined Example:
```python
# User message: "I'm terrified to launch this but I have to"

daring = nima.daring_analyze(message)
courage = nima.courage_analyze(message)

print(f"DARING: {daring['level']:.2f}")   # 0.45 (moderate)
print(f"COURAGE: {courage['level']:.2f}")  # 0.72 (high)

# Interpretation: User has fear but also determination
# Use COURAGE style: encouraging, supportive, action-oriented
```

## Data Persistence

User learning data stored in:
```
~/.nima/courage_data/user_courage_profile.json
```

## Testing

```bash
cd /path/to/nima-core
python3 test_courage_integration.py
```

## Implementation Status

- ✅ Layer 1: Foundation affects integration
- ✅ Layer 2: COURAGE composite formula
- ✅ 25+ generic domain templates
- ✅ Auto-detection signals
- ✅ Learning system
- ✅ NimaCore API integration
- ⬜ Bidirectional flow (future)

---

**Built with COURAGE — fear acknowledged, action taken anyway.** 🔥