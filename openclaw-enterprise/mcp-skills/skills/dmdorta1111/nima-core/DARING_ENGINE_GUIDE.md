# DARING Engine — Integration Guide

## Overview

The DARING Engine provides **variable response modulation** integrated with NIMA Core's affective layer. It automatically calculates appropriate DARING levels (0.0 = suggestive to 1.0 = absolute) based on:

- **Real-time affective state** (Panksepp's 7 affects)
- **Message content** (activation signals)
- **Domain-specific learning** (success/failure history)
- **User preference** (learned over time)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Foundation (Panksepp 7)                           │
│  SEEKING, RAGE, FEAR, LUST, CARE, PANIC, PLAY              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: DARING Composite                                  │
│  Formula: SEEKING(0.35) + PLAY(0.25) + RAGE(0.15) +        │
│           CARE(0.15) + LUST(0.10) - FEAR(0.30) -           │
│           PANIC(0.45)                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: Domain Modulation + Learning                      │
│  - Domain thresholds (family: 0.36, code: 0.65)            │
│  - Success rate adjustment                                   │
│  - User preference learning                                  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from nima_core import NimaCore

# Initialize NimaCore
nima = NimaCore(name="MyBot")

# Analyze message for DARING level
analysis = nima.daring_analyze("Go full blast! 🚀")
print(f"DARING Level: {analysis['level']}")  # 0.52
print(f"Style: {analysis['style']}")         # "daring"
print(f"Domain: {analysis['domain']}")       # "creative_building"
```

## Response Styles

| Level | Style | Example Prefix |
|-------|-------|----------------|
| 0.0-0.25 | suggestive | "Here are options..." |
| 0.25-0.50 | balanced | "I recommend..." |
| 0.50-0.70 | daring | "Here's what we're doing..." |
| 0.70-0.90 | high_daring | "YES. Executing..." |
| 0.90-1.0 | full_daring | Pure execution |

## Domain Registration Framework

The DARING Engine provides a **generic domain framework** for customizing response modulation across any task type. Use these templates as starting points:

### Generic Domain Templates

| Domain Category | Domain Name | Default Threshold | Recommended Triggers | Affect Modifiers |
|----------------|-------------|-------------------|---------------------|------------------|
| **Safety & Protection** | family_protection | 0.36 | family, kids, children, protect, safety, emergency | CARE +0.25, FEAR +0.10 |
| | personal_security | 0.40 | security, password, privacy, hack, threat | FEAR +0.20, PANIC +0.10 |
| **Creative Work** | creative_building | 0.45 | create, design, build, make, art, write | PLAY +0.20, SEEKING +0.15 |
| | content_creation | 0.50 | content, blog, video, media, marketing | PLAY +0.15, LUST +0.10 |
| | brainstorming | 0.40 | ideas, brainstorm, innovate, imagine | PLAY +0.25, SEEKING +0.20 |
| **Technical Tasks** | code_architecture | 0.65 | code, debug, refactor, system, architecture | RAGE -0.05 (frustration = caution) |
| | devops_deploy | 0.70 | deploy, production, release, server, infrastructure | FEAR +0.15 (production = careful) |
| | data_analysis | 0.55 | data, analyze, metrics, report, statistics | SEEKING +0.10 |
| **Research & Learning** | research_deep_dives | 0.55 | research, investigate, study, explore, learn | SEEKING +0.20 |
| | academic_work | 0.60 | paper, thesis, citation, academic, publish | CARE +0.10 (precision matters) |
| | documentation | 0.50 | docs, documentation, readme, wiki, manual | CARE +0.15 |
| **Business & Strategy** | strategic_planning | 0.60 | strategy, plan, roadmap, vision, goal | SEEKING +0.15, FEAR +0.10 |
| | client_projects | 0.55 | client, deliverable, deadline, stakeholder | FEAR +0.15, CARE +0.10 |
| | financial_decisions | 0.70 | money, budget, cost, revenue, financial, invest | FEAR +0.25, PANIC +0.15 |
| | negotiation | 0.50 | negotiate, deal, contract, agreement | RAGE +0.10, CARE +0.10 |
| **Personal & Social** | theological_synthesis | 0.40 | theology, faith, bible, spiritual, meaning | SEEKING +0.15, CARE +0.10 |
| | relationship_advice | 0.45 | relationship, partner, friend, conflict, love | CARE +0.25, FEAR +0.10 |
| | health_wellness | 0.50 | health, workout, diet, mental, therapy | CARE +0.20, FEAR +0.10 |
| | life_planning | 0.55 | career, future, move, change, decision | SEEKING +0.15, FEAR +0.10 |
| **Communication** | public_speaking | 0.45 | presentation, speech, audience, talk, pitch | FEAR +0.20, PLAY +0.10 |
| | difficult_conversations | 0.50 | confrontation, feedback, criticism, firing | FEAR +0.15, CARE +0.15 |
| | networking | 0.40 | network, connect, introduce, social, event | PLAY +0.15, SEEKING +0.10 |
| **Crisis & Urgent** | crisis_management | 0.35 | crisis, urgent, emergency, disaster, incident | PANIC +0.20, FEAR +0.15 |
| | incident_response | 0.30 | incident, outage, down, broken, critical | PANIC +0.25, FEAR +0.20 |

### Custom Domain Registration

Use the templates above or create your own:

```python
# Example 1: Marketing Campaigns (high creativity, moderate risk)
nima.daring_register_domain(
    name="marketing_campaigns",
    base_threshold=0.45,
    triggers=["campaign", "marketing", "launch", "promo", "ads"],
    affect_modifiers={
        "PLAY": 0.20,      # Be playful and creative
        "SEEKING": 0.15,   # Explore new ideas
        "FEAR": -0.10      # Don't fear failure in marketing
    }
)

# Example 2: Database Migrations (high caution, production risk)
nima.daring_register_domain(
    name="database_migrations",
    base_threshold=0.75,
    triggers=["migration", "database", "schema", "postgres", "mysql"],
    affect_modifiers={
        "FEAR": 0.25,      # Respect the risk
        "CARE": 0.20,      # Be careful and precise
        "PANIC": 0.10,     # If panic detected, extra caution
        "PLAY": -0.15      # Don't play around with data
    }
)

# Example 3: Startup Pivot (high stakes, needs conviction)
nima.daring_register_domain(
    name="startup_pivot",
    base_threshold=0.40,
    triggers=["pivot", "startup", "strategy", "direction", "change course"],
    affect_modifiers={
        "SEEKING": 0.25,   # Explore possibilities
        "RAGE": 0.10,      # Channel frustration into action
        "FEAR": -0.10      # Don't let fear block change
    }
)
```

### Domain Configuration Guide

**Base Threshold Guidelines:**
- **0.30-0.40**: High-stakes protection (family, crisis, safety)
- **0.40-0.50**: Creative/exploratory work (building, brainstorming)
- **0.50-0.60**: Analytical/research tasks (analysis, planning)
- **0.60-0.70**: Technical precision (code, architecture)
- **0.70-0.80**: High-risk operations (production, financial)

**Affect Modifier Guidelines:**
- **Positive modifiers** (+): Increase DARING when this affect is high
- **Negative modifiers** (-): Decrease DARING when this affect is high
- Range: -0.30 to +0.30 per affect

## Built-in Domains

These domains are pre-configured:

| Domain | Threshold | Triggers | Use Case |
|--------|-----------|----------|----------|
| family_protection | 0.36 | family, kids, spouse, protect | High-stakes personal safety |
| theological_synthesis | 0.40 | theology, bible, faith, spiritual | Spiritual exploration |
| creative_building | 0.45 | create, build, design, implement | Creative projects |
| research_deep_dives | 0.55 | research, analyze, investigate | Academic/investigation |
| code_architecture | 0.65 | code, architect, system, debug | Technical implementation |

## Learning System

The DARING Engine learns from outcomes:

```python
# After responding with DARING
analysis = nima.daring_analyze(message)

# User indicates success/failure
nima.daring_record_outcome(analysis, success=True)

# Engine automatically adjusts:
# - Domain success rate
# - User preference
# - Threshold adjustments
```

## Activation Signals

Messages are analyzed for these signals:

| Signal | Pattern | Weight |
|--------|---------|--------|
| high_energy | `!! 🚀🔥` | +0.25 |
| delegation | "go ahead" | +0.35 |
| permission | "full control" | +0.45 |
| urgency | "ASAP" | +0.30 |
| decisiveness | "execute" | +0.40 |
| excitement | "awesome!" | +0.20 |
| trust | "trust you" | +0.30 |

## Affect Integration

The DARING Engine reads real-time affect from `SubcorticalAffectiveCore`:

```python
# Automatic affect reading
affect_state = nima._daring.get_affect_state()
# Returns: {'SEEKING': 0.7, 'FEAR': 0.2, 'PLAY': 0.5, ...}
```

Affects contribute to DARING level:
- **SEEKING** (+0.35): High curiosity = more daring
- **PLAY** (+0.25): Joy = experimentation
- **FEAR** (-0.30): Anxiety = caution
- **PANIC** (-0.45): Distress = emergency restraint

## Stats & Monitoring

```python
stats = nima.daring_stats()
print(stats)
# {
#   'user_preference': 0.65,
#   'domains_registered': 6,
#   'domains': {
#     'family_protection': {
#       'attempts': 12,
#       'successes': 11,
#       'success_rate': 0.92,
#       'threshold': 0.32
#     },
#     ...
#   }
# }
```

## Data Persistence

User learning data stored in:
```
~/.nima/daring_data/user_daring_profile.json
```

Includes:
- User preference (global daring tendency)
- Domain success rates
- Recent interaction history

## Testing

```bash
cd /path/to/nima-core
python3 test_daring_integration.py
```

## Integration with AFFECT_FRAMEWORK

The DARING Engine implements the **Layer 2 Composite** pattern from `AFFECT_FRAMEWORK.md`:

```
SEEKING
├── Exploration (default)
└── DARING (SEEKING + low_FEAR + success_history)
    ├── family_protection (user-defined)
    ├── creative_building (user-defined)
    └── [your_custom_domains]
```

## Future Enhancements

- [ ] Bidirectional flow: DARING outcomes → AffectiveCore updates
- [ ] Voice tone analysis for spoken input
- [ ] Conversation momentum tracking
- [ ] Multi-user profile support
- [ ] Real-time dashboard for stats

---

**Built with DARING conviction.** 🔥