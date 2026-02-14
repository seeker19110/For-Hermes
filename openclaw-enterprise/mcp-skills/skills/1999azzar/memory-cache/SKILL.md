---
name: memory-cache
description: High-performance temporary storage using Redis. Use to save context, cache expensive API results, or share state between agent sessions. Follows strict key naming conventions.
---

# Memory Cache

## Setup
1. Copy `.env.example` to `.env`.
2. Set `REDIS_URL` (e.g. `redis://localhost:6379/0`) or `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD`.
3. Ensure Redis is running. Optional timeouts: `REDIS_SOCKET_TIMEOUT`, `REDIS_SOCKET_CONNECT_TIMEOUT`.
4. On first run, `scripts/cache` creates a venv and installs dependencies.

## Usage
- **Role**: Memory Manager.
- **Trigger**: "Save this for later", "Cache these results", "What was the last search?".
- **Output**: Confirmation of storage or retrieved values.

## Commands (CLI)

Use `scripts/cache` (recommended) or `python3 scripts/cache_manager.py`.

| Command | Description |
|---------|-------------|
| `set <key> <value> [--ttl N] [--json]` | Set key; optional TTL (seconds) and JSON encode |
| `get <key> [--json]` | Get key; optional JSON decode and pretty-print |
| `del <key>` | Delete key |
| `exists <key>` | Return 1 if exists, 0 otherwise |
| `ttl <key>` | Get TTL in seconds (-1 no expiry, -2 missing) |
| `expire <key> <seconds>` | Set TTL on existing key |
| `scan [pattern] [--count N]` | List keys by pattern (SCAN; production-safe) |
| `keys [pattern]` | Alias for scan |
| `ping` | Check Redis connection |

All keys must follow `mema:<category>:<name>`. Invalid keys return exit code 2.

## Key Naming Convention

**ALWAYS** use the `mema:<category>:<name>` structure. Categories: `context`, `cache`, `state`, `queue`. Name segments: letters, numbers, `_`, `:`, `.`, `-`.

- `mema:context:*` – Session context (TTL: 24h).
- `mema:cache:*` – API/data cache (TTL: 7d).
- `mema:state:*` – Persistent app state.
- `mema:queue:*` – Task queues (lists/streams).

See [Key Standards](references/key-standards.md) for full details.

## Examples

```bash
# Cache a search result for 1 hour
./scripts/cache set mema:cache:search:123 "search result json" --ttl 3600

# Store and retrieve JSON
./scripts/cache set mema:cache:config '{"theme":"dark"}' --ttl 86400 --json
./scripts/cache get mema:cache:config --json

# Retrieve context
./scripts/cache get mema:context:summary

# List keys (SCAN; safe on large datasets)
./scripts/cache scan mema:cache:*
./scripts/cache keys

# Check connection
./scripts/cache ping
```

## Exit codes
- 0: Success
- 1: Redis/cache error
- 2: Key validation error
