---
name: context-clean-up
slug: context-clean-up
version: 1.0.2
license: MIT
description: Audit OpenClaw context bloat sources and produce an actionable clean-up plan (no automatic changes).
disable-model-invocation: true
allowed-tools:
  - read
  - exec
  - sessions_list
  - sessions_history
  - session_status
metadata: { "openclaw": { "emoji": "🧹", "requires": { "bins": ["python3"] } } }
---

# Context Clean Up (audit-only)

This skill is a **runbook** to quickly identify *what is bloating your OpenClaw prompt context* and produce a **safe, reversible plan**.

**Important:** This version is intentionally **audit-only** (it does not auto-apply changes). If you want me to apply fixes, I will propose an exact patch + rollback plan and wait for explicit approval.

## Quick start

- `/context-clean-up` → audit + actionable plan (no changes)

## Workflow (audit → plan)

### Step 0 — Determine scope

Find:
- Workspace dir (your project files; usually the OpenClaw workspace)
- State dir (OpenClaw runtime state; usually `~/.openclaw`)

If unsure:

```bash
bash -lc 'echo "WORKDIR=$PWD"; echo "HOME=$HOME"; ls -ld ~/.openclaw'
```

### Step 1 — Run the audit script

This script prints a short summary and can write a full JSON report.

```bash
bash -lc 'cd "${WORKDIR:-.}" && python3 {baseDir}/scripts/context_cleanup_audit.py --out memory/context-cleanup-audit.json'
```

Interpretation cheatsheet:
- Huge `toolResult` entries (exec/read/web_fetch): **transcript bloat**
- Many `System:` / `Cron:` lines: **automation bloat**
- Large bootstrap docs (AGENTS/MEMORY/SOUL/USER): **reinjected rules bloat**

### Step 2 — Produce a fix plan (lowest-risk first)

Create a short plan with:
- Top offenders (largest transcript entries)
- Noisiest recurring jobs (cron/heartbeat)
- Quick wins (reversible)

Use these standard levers:

#### Lever A — Make no-op automation truly silent
Goal: maintenance loops should output exactly `NO_REPLY` unless there is an anomaly.

Pattern: update prompts so the last line forces:
- `Finally output ONLY: NO_REPLY`

#### Lever B — Keep notifications, avoid transcript injection
If you want alerts but want the *interactive* session lean:
- Send out-of-band (Telegram/Slack/etc.)
- Then output `NO_REPLY`

See: `references/out-of-band-delivery.md`

#### Lever C — Keep injected bootstrap files small
- Keep only restart-critical rules in `MEMORY.md`
- Move bulky notes into `references/*.md` or `memory/*.md`

### Step 3 — Verify

After you apply any changes:
- Confirm the next cron/heartbeat runs are silent on success.
- Watch context growth rate (it should flatten).

## References
- `references/out-of-band-delivery.md`
- `references/cron-noise-checklist.md`
