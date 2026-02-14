---
name: mema
description: Mema's personal brain - SQLite document index + Redis mental buffer. Use for indexing MD files, storing short-term mental state, and organizing memory across sessions.
---
# Mema Brain (Centralized Memory)

This skill provides the **Long-Term Memory** (SQLite) and **Short-Term Context** (Redis) for the agent.
It is integrated directly into the Agent's core database.

## Architecture

### 1. Long-Term Memory (SQLite)

- **Path:** `~/.openclaw/memory/main.sqlite`
- **Tables:**
  - `documents`: Index of knowledge files (path, title, tags).
  - `skills`: Tracking skill usage and success rates.
- **Why?** Persistent storage that survives restarts and is backed up with the agent state.

### 2. Short-Term Memory (Redis)

- **Key Prefix:** `mema:mental:*`
- **Usage:** Passing context between sessions, caching thoughts, temporary scratchpad.
- **TTL:** 6 hours (matches Agent Session cycle).

## Usage

### Indexing Knowledge

When you learn something new or create a doc:

```bash
scripts/mema.py index "docs/NEW_FEATURE.md" --tag "feature"
```

### Searching Memory

Find relevant docs:

```bash
scripts/mema.py list --tag "iot"
```

### Mental State (Context)

Save context for the next turn/session:

```bash
scripts/mema.py mental set context:summary "Working on Hub Redesign..."
```

Recall it:

```bash
scripts/mema.py mental get context:summary
```

## Setup

1. Copy `.env.example` to `.env` and configure Redis connection if needed.
2. Install dependencies: `pip install -r requirements.txt` (or use a venv).
3. **Init:** Run `scripts/mema.py init` once to create tables in `main.sqlite`.
