---
name: memory-config
description: Configure memory settings for Clawdbot including memory flush before compaction and session memory search. Use when the user wants to enable or configure memory features like compaction.memoryFlush, sessionMemory search, or memorySearch sources.
---

# Memory Config Skill

This skill configures advanced memory settings for the agent.

## Configuration Options

### 1. Memory Flush Before Compaction
Enables saving context to memory files before compaction occurs.

**Config path:** `agents.defaults.compaction.memoryFlush.enabled`
**Value:** `true` or `false`

### 2. Session Memory Search
Enables searching through past session transcripts (not just MEMORY.md).

**Config path:** `agents.defaults.memorySearch.experimental.sessionMemory`
**Value:** `true` or `false`

### 3. Memory Search Sources
Defines which sources to include in memory search.

**Config path:** `agents.defaults.memorySearch.sources`
**Value:** `["memory"]` or `["memory", "sessions"]`

## Usage

Apply configuration using gateway config.patch:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "memoryFlush": {
          "enabled": true
        }
      },
      "memorySearch": {
        "experimental": {
          "sessionMemory": true
        },
        "sources": ["memory", "sessions"]
      }
    }
  }
}
```

The gateway will restart automatically after applying config changes.
