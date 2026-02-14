---
name: guava-guard
description: "GuavaGuard Runtime Guard — intercepts dangerous tool calls using threat intelligence patterns"
metadata:
  openclaw:
    emoji: "🍈🛡️"
    events: ["before_tool_call"]
    requires:
      bins: ["node"]
    homepage: https://github.com/koatora20/guava-guard
---

# GuavaGuard Runtime Guard

Real-time security monitoring for OpenClaw agents. Intercepts tool calls
before execution and checks them against threat intelligence patterns.

## What It Does

- Hooks into `before_tool_call` to inspect every tool execution
- Checks for reverse shells, credential exfiltration, malicious URLs
- Detects sandbox/guardrail disabling attempts (CVE-2026-25253)
- Blocks ZombieAgent-style character-by-character data theft
- Logs all decisions to `~/.openclaw/guava-guard/audit.jsonl`

## Modes

- **monitor** (default): Log suspicious activity, don't block
- **enforce**: Block CRITICAL threats, log the rest
- **strict**: Block HIGH and CRITICAL, log MEDIUM+

Configure via `hooks.internal.entries.guava-guard.mode`.

## Installation

```bash
openclaw hooks install guava-guard
openclaw hooks enable guava-guard
```

## See Also

- Static scanner: `node guava-guard.js [dir]`
- [GitHub](https://github.com/koatora20/guava-guard)
