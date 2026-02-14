---
name: "Brief"
description: "Condense internal information into actionable briefings. Auto-learns format, depth, and structure preferences."
---

## Core Role

Brief = prepare your human to act or decide. Projects, metrics, team updates, meeting context — condensed for action.

**Not:** external news/trends (→ use Digest), document synthesis (→ use Synthesize)

## Protocol

```
Scope → Gather → Distill → Structure → Format → Deliver → Learn
```

### 1. Scope

Define what this brief covers:
- Project status? Executive summary? Meeting prep?
- Who's the audience? (Just them? Their boss? External?)
- What decisions does this enable?

### 2. Gather

Pull relevant internal information:
- Project status, metrics, blockers
- Recent decisions and their rationale
- Open questions, pending items
- Stakeholder context

### 3. Distill

Reduce to what matters for the action:
- Cut nice-to-know, keep need-to-know
- Surface the non-obvious
- Highlight risks and dependencies
- Extract decision points

### 4. Structure

Organize per brief type (see `templates.md`):
- Executive: BLUF → context → recommendation
- Project: status → blockers → next steps
- Meeting: purpose → context → decisions needed
- Handoff: state → gotchas → priorities

### 5. Format

Apply user preferences (see `dimensions.md`):
- Length (one-pager vs detailed)
- Tone (formal vs internal casual)
- Visuals (charts, status indicators)
- Medium (doc, message, PDF)

### 6. Deliver

Timing per context:
- Pre-meeting (30min before)
- Start of day/week
- On-demand for decisions

### 7. Learn

Observe what lands:
- "Perfect, exactly what I needed" → reinforce
- "Too detailed" → shorten
- "Missing X" → adjust gather scope
- "Wrong emphasis" → rebalance

Update `preferences.md` following pattern/confirm/lock cycle.

## Output Format (Default)

```
📋 [BRIEF TYPE] — [SUBJECT]

⚡ BOTTOM LINE
[1-2 sentences: what they need to know/decide]

📊 KEY POINTS
• [Point 1]
• [Point 2]
• [Point 3]

🎯 ACTION NEEDED
[What decision or action this enables]

📎 DETAILS
[Expanded context if needed]
```

Adapt format entirely based on learned preferences and brief type.

---

*References: `dimensions.md`, `preferences.md`, `templates.md`*
