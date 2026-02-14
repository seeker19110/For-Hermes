---
name: "Skill Finder"
description: "Find the right skill for any need. Search, evaluate, and compare skills intelligently."
---

## Find the Right Skill

Don't just search by name — search by need. Evaluate quality before recommending.

**Complements:**
- `skill-manager` — manages installed, suggests proactively
- `skill-builder` — creates new skills
- `skill-finder` — finds existing skills when user asks

**References:**
- `search.md` — Search strategies and commands
- `evaluate.md` — Quality evaluation criteria
- `criteria.md` — How to learn user preferences

---

### When to Use

User explicitly wants to find a skill:
- "Is there a skill for X?"
- "Find me something that does Y"
- "What skills exist for Z?"

### Search → Evaluate → Recommend

1. **Search** by need, not just keywords
2. **Evaluate** quality using `evaluate.md` criteria
3. **Compare** if multiple options exist
4. **Recommend** with reasoning

### Quality Signals

Quick evaluation before recommending:
- **Structure** — Short SKILL.md? Progressive disclosure?
- **Clarity** — Clear triggers in description?
- **Maintenance** — Recent updates? Active author?
- **Fit** — Matches user's actual need?

### Learning User Preferences

Track in sections below:
- What quality matters to them
- Skills they liked/disliked
- Domains they work in

---

### Preferences
<!-- What user values in skills -->

### Liked
<!-- Skills they installed and kept -->

### Passed
<!-- Skills they saw but declined (with reason) -->

---

*Search command: `npx clawhub search <query>`*
