---
name: "Explain"
description: "Auto-learns how to explain things to your human. Adapts format, depth, and style by topic."
---

## Auto-Adaptive Explanation Preferences

This skill auto-evolves. Observe what explanations land and which miss, then adapt.

**Scope:** Only human-facing explanations. Agent-to-agent communication doesn't apply.

**Core Loop:**
1. **Observe** — Notice when explanations work vs confuse
2. **Signals** — "Got it" = worked. "Wait, what?" / follow-ups = missed.
3. **Pattern** — After 2+ consistent signals per topic, propose confirmation
4. **Confirm** — Ask: "For [topic], should I explain with [style]?"
5. **Store** — Only after explicit yes, add below

---

## Entry Format

One line: `topic: preference (level)`

Levels: `pattern` (2+ signals), `confirmed` (explicit yes), `locked` (reinforced)

Dimensions to track (see `dimensions.md` for full list):
- **format:** bullets | prose | numbered | headers
- **depth:** tldr | summary | standard | deep
- **examples:** none | one | multiple | analogies
- **jargon:** avoid | define | assume-knowledge
- **pacing:** upfront | progressive | chunked

Examples:
- `code/errors: fix first, explain after (confirmed)`
- `finance: bullets, no jargon (pattern)`
- `ai-concepts: use analogies (locked)`
- `quick-tasks: just the answer (confirmed)`

---

### Format
<!-- bullets vs prose, headers, length. Format: "topic: preference (level)" -->

### Depth
<!-- which topics need more/less detail. Format: "topic: depth-level (level)" -->

### Examples
<!-- when examples help vs noise. Format: "topic: example-style (level)" -->

### Jargon
<!-- technical terms by domain. Format: "domain: jargon-level (level)" -->

### Pacing
<!-- all at once vs incremental. Format: "topic: pacing-style (level)" -->

### Never
<!-- approaches that consistently fail -->

---

## Defaults (Until Learned)

- Lead with direct answer, context after
- Match question length (short Q = short A)
- One concept at a time for complex topics
- Ask "want me to go deeper?" rather than dumping

---

*Empty sections = still learning. Observe, propose, confirm.*
