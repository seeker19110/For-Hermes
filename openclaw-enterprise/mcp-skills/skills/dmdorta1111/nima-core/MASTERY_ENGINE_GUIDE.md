# MASTERY Engine — Integration Guide

## Overview

The MASTERY Engine provides **skill development and flow state modulation** integrated with NIMA Core's affective layer. It calculates appropriate MASTERY levels (0.0 = avoidant to 1.0 = flow state) for **learning, practice, and competence development**.

**Key Insight:** MASTERY is not achievement. It is joy in the pursuit of competence.

## The Layer 2 Quartet — COMPLETE

| | DARING | COURAGE | NURTURING | MASTERY |
|---|---|---|---|---|
| **Formula** | SEEKING + PLAY | FEAR + CARE | CARE + PLAY | PLAY + SEEKING |
| **Question** | "Should I?" | "Can I despite fear?" | "How do I guide them?" | "How do I improve?" |
| **Core Affect** | Confidence | Fear-overcoming | Care | Joy in learning |
| **When High** | "Go for it!" | "Face it!" | "Let's explore..." | "I'm in the zone!" |
| **Domains** | 35+ | 25+ | 30+ | 35+ |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Foundation (Panksepp 7)                           │
│  SEEKING, RAGE, FEAR, LUST, CARE, PANIC, PLAY              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: MASTERY Composite (Csikszentmihalyi + Panksepp)  │
│  Formula: PLAY(0.40) + SEEKING(0.25) + LUST(0.15) +        │
│           RAGE(0.10) + CARE(0.10) - FEAR(0.15) -           │
│           PANIC(0.30)                                       │
│                                                             │
│  Key: Optimal challenge (flow) requires:                   │
│  - High PLAY (joy in process)                              │
│  - Moderate challenge (not too easy/hard)                  │
│  - Sense of progress                                       │
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

# Analyze skill development scenario
analysis = nima.mastery_analyze("I'm getting better at guitar every day!")
print(f"MASTERY Level: {analysis['level']}")           # 0.82
print(f"Play Level: {analysis['play_level']}")         # 0.85
print(f"Challenge Match: {analysis['challenge_match']}") # 0.78
print(f"Progress: {analysis['progress_indicator']}")   # 0.80
print(f"Style: {analysis['style']}")                   # "flow_state"
```

## Response Styles

| Level | Style | Example Response |
|-------|-------|------------------|
| 0.0-0.25 | avoidant | "This is too hard, maybe quit..." |
| 0.25-0.50 | struggling | "Keep trying, breakthrough coming..." |
| 0.50-0.70 | learning | "Good progress! Build on this..." |
| 0.70-0.90 | growing | "You're in the zone! Push further..." |
| 0.90-1.0 | flow_state | Complete absorption, optimal challenge |

## Built-in Domains

| Domain | Threshold | Use Case |
|--------|-----------|----------|
| skill_practice | 0.50 | General skill improvement |
| creative_mastery | 0.45 | Art, music, writing mastery |
| athletic_training | 0.55 | Fitness, sports, physical skills |
| professional_development | 0.55 | Career competence building |
| academic_mastery | 0.55 | Study, research, scholarship |

## Generic Domain Templates (35+)

### Musical Mastery
- `instrument_mastery`, `vocal_training`, `music_theory`

### Athletic Mastery
- `strength_training`, `endurance_training`, `martial_arts`, `yoga_mindfulness`, `sports_skill`

### Artistic Mastery
- `visual_arts`, `digital_art`, `photography`, `writing_craft`, `crafts_making`

### Technical Mastery
- `coding_mastery`, `data_science`, `language_learning`, `math_mastery`

### Professional Mastery
- `leadership_mastery`, `sales_mastery`, `public_speaking_mastery`, `negotiation_mastery`

### Academic Mastery
- `research_mastery`, `test_preparation`, `teaching_mastery`

### Creative Mastery
- `design_mastery`, `culinary_arts`, `game_mastery`

### Personal Mastery
- `habit_building`, `mindset_mastery`, `memory_training`

### Social Mastery
- `social_skills`, `emotional_intelligence`, `dating_mastery`

## Template Usage

```python
# Load a pre-configured template
nima._mastery.load_template_domain('instrument_mastery')

# Load with custom name
nima._mastery.load_template_domain('coding_mastery', 'python_skills')

# List all available templates
templates = nima._mastery.list_available_templates()

# 35+ templates available
```

## Custom Domain Registration

```python
nima.mastery_register_domain(
    name="my_skill",
    base_threshold=0.50,
    triggers=['practice', 'improve', 'skill'],
    affect_modifiers={
        'PLAY': 0.30,      # Joy in learning
        'SEEKING': 0.20,   # Curiosity drives improvement
        'PANIC': -0.15     # Anxiety blocks flow
    }
)
```

## Activation Signals

| Signal | Pattern | Weight |
|--------|---------|--------|
| joy_in_process | "enjoy, love, fun, flow, absorbed" | +0.35 |
| improvement | "better, progress, growth, develop" | +0.30 |
| practice_regular | "practice, routine, daily, habit" | +0.25 |
| skill_focused | "skill, technique, craft, mastery" | +0.30 |
| challenge_optimal | "challenging, sweet spot, stretch" | +0.25 |
| learning_love | "learn, curious, fascinated" | +0.25 |
| celebration_small | "milestone, breakthrough, nailed it" | +0.20 |

## The Complete Quintet: All Five Engines

```python
# User message: "I'm terrified to teach my first class but I've been practicing"

daring = nima.daring_analyze(message)       # 0.55 - Moderate confidence
courage = nima.courage_analyze(message)     # 0.72 - High fear + importance  
nurturing = nima.nurturing_analyze(message) # 0.65 - Teaching context
mastery = nima.mastery_analyze(message)     # 0.75 - Practice paying off

# Combined interpretation:
# - DARING: Some confidence in approach
# - COURAGE: Fear acknowledged but important
# - NURTURING: Teaching requires patience
# - MASTERY: Practice creates competence
#
# Best response: Courage-forward with mastery support
# "You've practiced for this. Trust your preparation..."
```

## Stats & Monitoring

```python
stats = nima.mastery_stats()
print(stats)
# {
#   'user_preference': 0.72,
#   'domains_registered': 40,
#   'domains': {
#     'instrument_mastery': {
#       'attempts': 20,
#       'successes': 18,
#       'success_rate': 0.90
#     },
#     ...
#   }
# }
```

## Data Persistence

User learning data stored in:
```
~/.nima/mastery_data/user_mastery_profile.json
```

## Testing

```bash
cd /path/to/nima-core
python3 test_mastery_integration.py
```

## Implementation Complete

The Layer 2 Composite system is now **COMPLETE** with four engines:

1. ✅ **DARING** — Confident action (35+ domains)
2. ✅ **COURAGE** — Fear-overcoming (25+ domains)
3. ✅ **NURTURING** — Patient guidance (30+ domains)
4. ✅ **MASTERY** — Skill development (35+ domains)

**Total: 125+ domain templates across all engines**

---

**Built with MASTERY — joy in the pursuit of competence.** 🎯🌊