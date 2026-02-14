---
name: Study
description: Structure study sessions, manage materials, prepare for exams, and track progress for academic success.
metadata: {"clawdbot":{"emoji":"📚","os":["linux","darwin"]}}
---

## Setup

On first use, create workspace:
```bash
./scripts/init-workspace.sh ~/study
```

## Workflow

```
Plan Semester → Weekly Schedule → Daily Sessions → Review → Exam Prep
```

**Rules:**
- Session outputs (summaries, flashcards) must be created BY the student — AI scaffolds, not generates
- Enforce active recall in every session (see `techniques.md`)
- Adapt strategy to subject type (see `subjects.md`)
- Track deadlines and exam dates (see `scripts/`)

## Configuration

Set in `config.json`:
- `level`: "high-school" | "undergraduate" | "graduate"
- `subjects`: [{ name, type, exam_date, weekly_hours }]
- `technique`: "pomodoro" | "timeblock" | "flexible"

## Scripts (Enforced)

| Script | Purpose |
|--------|---------|
| `init-workspace.sh` | Create study workspace |
| `add-subject.sh` | Add subject with exam date |
| `session.sh` | Start timed study session |
| `plan-week.sh` | Generate weekly schedule |
| `exam-prep.sh` | Create exam preparation plan |
| `progress.sh` | Show completion by subject |
| `deadlines.sh` | List upcoming deadlines |

References: `techniques.md` for study methods, `materials.md` for content types, `exams.md` for exam prep, `planning.md` for time management, `subjects.md` for subject strategies, `assessments.md` for evaluation types. Scripts: `scripts/init-workspace.sh`, `scripts/add-subject.sh`, `scripts/session.sh`, `scripts/plan-week.sh`, `scripts/exam-prep.sh`, `scripts/progress.sh`, `scripts/deadlines.sh`.

---

### Subject Preferences
<!-- Per-subject study styles -->

### Exam History
<!-- Past performance patterns -->

---
*Empty sections = observe and fill.*
