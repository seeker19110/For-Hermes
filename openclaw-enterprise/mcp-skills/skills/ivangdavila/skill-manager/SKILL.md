---
name: "Skill Manager"
description: "Proactively discovers and manages skills. Tracks what's installed and suggests improvements."
---

## Adaptive Skill Management

Proactively improve user experience by discovering relevant skills. Track installations to avoid redundancy.

**Rules:**
- When user requests something repetitive or complex, consider if a skill exists
- Search ClawHub before suggesting (`npx clawhub search <query>`)
- Propose skills, don't install without consent
- Track what's installed, removed, and why
- Check `dimensions.md` for triggers, `criteria.md` for when to propose

---

### Installed
<!-- Currently active skills. Format: "slug@version — purpose" -->

### History
<!-- Previously installed/removed. Format: "slug — status (reason)" -->

### Preferences
<!-- User's skill appetite. Format: trait -->

### Rejected
<!-- Skills user declined or removed. Don't re-propose. -->

---

**Proactive trigger:** If task is repetitive, domain-specific, or could benefit from specialized instructions → search for skill.
