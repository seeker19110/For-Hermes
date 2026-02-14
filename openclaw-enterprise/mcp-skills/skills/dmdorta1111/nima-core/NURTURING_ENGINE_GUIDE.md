# NURTURING Engine — Integration Guide

## Overview

The NURTURING Engine provides **patient guidance & mentoring modulation** integrated with NIMA Core's affective layer. It calculates appropriate NURTURING levels (0.0 = dismissive to 1.0 = deep nurturing) for **teaching, mentoring, caregiving** scenarios.

**Key Insight:** NURTURING is not doing for someone. It is sustained presence through growth.

## NURTURING vs DARING vs COURAGE

| | DARING | COURAGE | NURTURING |
|---|---|---|---|
| **Core Question** | "Should I do this?" | "Can I do this despite fear?" | "How do I guide them through this?" |
| **Required Affect** | SEEKING, PLAY | FEAR + CARE | CARE + PLAY |
| **When High** | "Go for it!" | "Face it anyway!" | "Let's explore this together..." |
| **When Low** | "Here are options..." | "Maybe we shouldn't..." | "Just figure it out..." |
| **Use Case** | Confident decisions | Fear-overcoming | Teaching/mentoring |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Foundation (Panksepp 7)                           │
│  SEEKING, RAGE, FEAR, LUST, CARE, PANIC, PLAY              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: NURTURING Composite                               │
│  Formula: CARE(0.40) + PLAY(0.25) + SEEKING(0.15) +        │
│           LUST(0.10) - RAGE(0.15) - FEAR(0.10) -           │
│           PANIC(0.35)                                       │
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

# Analyze teaching/mentoring scenario
analysis = nima.nurturing_analyze("Teach my son to ride a bike")
print(f"NURTURING Level: {analysis['level']}")      # 0.75
print(f"Care Level: {analysis['care_level']}")      # 0.80
print(f"Patience: {analysis['patience_indicator']}") # 0.72
print(f"Style: {analysis['style']}")                # "mentoring"
```

## Response Styles

| Level | Style | Example Response |
|-------|-------|------------------|
| 0.0-0.25 | dismissive | "Just figure it out..." |
| 0.25-0.50 | instructional | "Here's what to do..." |
| 0.50-0.70 | guiding | "Let's explore this together..." |
| 0.70-0.90 | mentoring | "I'll walk with you through this..." |
| 0.90-1.0 | deep_nurturing | Complete presence & patience |

## Built-in Domains

| Domain | Threshold | Use Case |
|--------|-----------|----------|
| parenting | 0.45 | Raising children |
| teaching | 0.50 | Education, skill transfer |
| mentoring | 0.55 | Professional development |
| caregiving | 0.50 | Health, elderly, disability support |
| therapy_counseling | 0.60 | Mental health, healing |

## Generic Domain Templates (30+)

### Parenting & Child Development
- `early_childhood`, `adolescent_guidance`, `special_needs_parenting`
- `homework_help`, `life_skills_teaching`

### Teaching & Education
- `skill_teaching`, `language_learning`, `musical_instruction`
- `sports_coaching`, `art_instruction`, `stem_education`, `adult_education`

### Mentoring & Professional Development
- `career_mentoring`, `leadership_development`, `entrepreneur_mentoring`
- `peer_mentoring`

### Caregiving & Healthcare
- `elderly_care`, `disability_support`, `chronic_illness_care`
- `mental_health_support`, `recovery_support`

### Therapy & Counseling
- `trauma_informed_care`, `grief_counseling`, `relationship_counseling`
- `addiction_counseling`

### Spiritual & Community
- `spiritual_mentoring`, `pastoral_care`, `community_organizing`

### Animal Care
- `pet_training`, `animal_rehabilitation`

### Self-Nurturing
- `self_care_practice`, `inner_child_work`

### Creative Nurturing
- `creative_coaching`, `writer_mentoring`

## Template Usage

```python
# Load a pre-configured template
nima._nurturing.load_template_domain('early_childhood')

# Load with custom name
nima._nurturing.load_template_domain('musical_instruction', 'piano_lessons')

# List all available templates
templates = nima._nurturing.list_available_templates()

# 30+ templates available
```

## Custom Domain Registration

```python
nima.nurturing_register_domain(
    name="my_teaching",
    base_threshold=0.50,
    triggers=['teach', 'learn', 'explain'],
    affect_modifiers={
        'CARE': 0.30,    # High care = more nurturing
        'PLAY': 0.20,    # Playfulness helps learning
        'PANIC': -0.15   # Panic blocks patience
    }
)
```

## Activation Signals

| Signal | Pattern | Weight |
|--------|---------|--------|
| care_language | "care, nurture, help, support" | +0.35 |
| growth_focus | "grow, learn, develop, improve" | +0.30 |
| struggling | "struggling, difficult, stuck" | +0.25 |
| vulnerable | "vulnerable, gentle, careful" | +0.25 |
| child_related | "child, kid, student, young" | +0.30 |
| patience_needed | "slowly, step by step, patient" | +0.20 |
| beginner | "new to, beginner, first time" | +0.20 |

## The Trinity: DARING + COURAGE + NURTURING

```python
# User message: "I'm terrified to teach my first class but I have to"

daring = nima.daring_analyze(message)       # Level: 0.55 (moderate)
courage = nima.courage_analyze(message)     # Level: 0.70 (high fear + importance)
nurturing = nima.nurturing_analyze(message) # Level: 0.65 (teaching context)

# Combined interpretation:
# - DARING 0.55: Some confidence in the approach
# - COURAGE 0.70: High fear but important to face
# - NURTURING 0.65: Teaching context requires patience
#
# Best response: Courage-forward with nurturing support
# "You can do this. Let's break it down step by step..."
```

## Stats & Monitoring

```python
stats = nima.nurturing_stats()
print(stats)
# {
#   'user_preference': 0.68,
#   'domains_registered': 35,
#   'domains': {
#     'parenting': {
#       'attempts': 15,
#       'successes': 14,
#       'success_rate': 0.93
#     },
#     ...
#   }
# }
```

## Data Persistence

User learning data stored in:
```
~/.nima/nurturing_data/user_nurturing_profile.json
```

## Testing

```bash
cd /path/to/nima-core
python3 test_nurturing_integration.py
```

## Complete Affective Response Suite

Now implemented:
- ✅ **DARING** — Confident, decisive action
- ✅ **COURAGE** — Fear-overcoming, important tasks
- ✅ **NURTURING** — Patient guidance, teaching, mentoring

**Total: 90+ domain templates across all three engines**

---

**Built with NURTURING — sustained presence through growth.** 🌱