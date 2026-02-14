# Memory Between Iterations

## What to Persist

- **learnings.txt** — Append-only log: what tried, what happened, what to try next
- **progress.json** — Structured state for complex multi-step tasks
- Git commits — Each successful step committed

## What NOT to Persist

- Full conversation history (context bloat)
- Failed code attempts (noise)
- Intermediate debugging output

## Cost Awareness

Loops multiply cost. Before starting:
- Estimate tokens per iteration
- Confirm with user if >10 iterations likely
- Consider if approach should change rather than iterate
