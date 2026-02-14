---
name: Ralph Loop
description: Run iterative agent loops until success criteria are met. Autonomous iteration pattern.
---

## Pattern

```
Task + Criteria → Execute → Verify → [Pass? Exit : Retry]
```

Keep trying until task succeeds or max iterations reached. Each iteration starts fresh but carries forward learnings. Check `memory.md` for what to persist between iterations.

## When to Propose

- Task has clear success criteria but uncertain path
- Previous attempt failed but error is fixable
- User says "keep trying until..." or "make it work"

**Not for:** One-shot tasks, undefined goals, exploratory work.

## Setup

Before starting, establish with user:

| Element | Required | Example |
|---------|----------|---------|
| Task | Yes | "Fix failing tests" |
| Success criteria | Yes | "All tests pass" |
| Max iterations | Default: 5 | 10 |
| Verify command | Recommended | `npm test` |

## Execution

Each iteration:
1. **Fresh context** — Only carry: task, criteria, count, learnings
2. **Execute** — Attempt the task
3. **Verify** — Check success criteria
4. **Record** — Append to learnings: what worked, what failed
5. **Decide** — Pass? Exit. Fail? Retry if under limit.

Check `examples.md` for common loop patterns.

## Stopping

Exit when: ✅ Criteria met · ❌ Max reached · ⚠️ Unrecoverable error

On max without success: summarize attempts, recommend next steps.

---

**Related:** For designing structured multi-phase workflows (not iteration), see the `cycle` skill.
