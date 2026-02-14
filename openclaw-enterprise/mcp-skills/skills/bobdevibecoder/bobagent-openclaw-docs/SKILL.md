---
name: openclaw-docs
description: Reference documentation for OpenClaw capabilities, configuration options, and best practices. Use when the user needs information about OpenClaw features, config schema, cron jobs, multi-agent routing, or troubleshooting.
metadata:
  {"openclaw": {"always": true, "emoji": "📚"}}
---

# OpenClaw Docs Reference

Quick reference for OpenClaw capabilities.

## Config Paths (agents.defaults)

| Feature | Config Path |
|---------|-------------|
| Memory flush | `compaction.memoryFlush.enabled` |
| Session memory | `memorySearch.experimental.sessionMemory` |
| Web search | `tools.web.search.{enabled,provider,apiKey}` |
| Cron | `cron.{enabled,store,maxConcurrentRuns}` |
| Skills dirs | `skills.load.extraDirs[]` |
| Multi-agent | `agents.list[], bindings[]` |
| Sandbox | `agents.defaults.sandbox.{mode,scope,workspaceAccess}` |

## Cron Job Types

**Main session** (uses heartbeat context):
```json
{
  "schedule": {"kind": "at", "atMs": 1234567890000},
  "sessionTarget": "main",
  "payload": {"kind": "systemEvent", "text": "Check calendar"}
}
```

**Isolated session** (dedicated agent run):
```json
{
  "schedule": {"kind": "cron", "expr": "0 7 * * *", "tz": "UTC"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Morning brief",
    "deliver": true,
    "channel": "telegram"
  }
}
```

## Tool Categories

- **Core**: read, write, edit, apply_patch
- **Shell**: exec, process
- **Web**: web_search, web_fetch, browser
- **Sessions**: sessions_list, sessions_history, sessions_send, sessions_spawn
- **Schedule**: cron, system event
- **System**: gateway, nodes, canvas
- **Memory**: memory_search, memory_get

## Security Gates

- `requires.bins`: Binaries that must exist on PATH
- `requires.env`: Required environment variables
- `requires.config`: Config paths that must be truthy
- `os`: darwin, linux, win32

See references/ for full details.
