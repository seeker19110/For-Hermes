# Mema Cognitive Architecture

## 1. Long-Term Memory (SQLite)
- **Location**: `~/.openclaw/memory/main.sqlite`
- **Purpose**: "Hard facts" and indexed documents.
- **Tables**:
  - `documents`: Indexed Markdown files (Knowledge Base).
  - `skills`: Usage stats for system skills (Self-Optimization).

## 2. Short-Term Memory (Redis)
- **Prefix**: `mema:mental:`
- **Purpose**: "Working memory" / Context / Train of thought.
- **TTL**: 6 hours (default).
- **Mechanism**: Stores ephemeral state that survives session restarts but fades over time.

## 3. Skill Integration
- Mema uses `memory-cache` skill logic but implements it natively for speed.
- All skill usage is logged to `skills` table to track reliability.
