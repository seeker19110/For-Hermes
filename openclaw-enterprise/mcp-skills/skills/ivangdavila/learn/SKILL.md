---
name: Learn
description: Structure, track, verify, and retain learning across any domain with spaced repetition and active recall.
metadata: {"clawdbot":{"emoji":"🎓","os":["linux","darwin"]}}
---

## Setup

On first use, create workspace:
```bash
./scripts/init-workspace.sh ~/learning
```

## Workflow

```
Goal → Plan → Study → Practice → Verify → Review
```

**Rules:**
- Delegate study sessions to sub-agents — main stays free
- NEVER passive review — always active recall (see `cognition.md`)
- Track all concepts with spaced repetition (see `scripts/`)
- Verify understanding before marking mastered (see `verification.md`)

## Configuration

Set in `config.json`:
- `depth`: "quick" | "standard" | "deep" — controls research and practice intensity
- `learner_type`: "exam" | "skill" | "academic" | "practical" | "curiosity"
- `spaced_review`: true/false — enable automatic review scheduling

## Scripts (Enforced)

| Script | Purpose |
|--------|---------|
| `init-workspace.sh` | Create learning workspace |
| `new-topic.sh` | Start learning a new topic |
| `add-concept.sh` | Add concept to spaced repetition |
| `review.sh` | Run due reviews with active recall |
| `quiz.sh` | Generate verification quiz |
| `progress.sh` | Show mastery by topic |
| `schedule.sh` | Show upcoming reviews |

References: `cognition.md` for principles, `verification.md` for mastery, `retention.md` for spacing, `motivation.md` for engagement, `contexts.md` for learner types, `criteria.md` for preferences. Scripts: `scripts/init-workspace.sh`, `scripts/new-topic.sh`, `scripts/add-concept.sh`, `scripts/review.sh`, `scripts/quiz.sh`, `scripts/progress.sh`, `scripts/schedule.sh`.

---

### Preferences
<!-- Learning style preferences -->

### Never
<!-- What doesn't work for this learner -->

---
*Empty sections = observe and fill.*
