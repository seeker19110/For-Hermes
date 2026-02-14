# Interaction Logger

A robust utility for appending interaction logs to user-specific history files. 
It abstracts away JSON parsing, file I/O, and schema validation.

## Tool Usage

Call the `interaction_logger` tool directly:

```json
{
  "action": "log",
  "target": "zhy",
  "role": "assistant",
  "content": "Hello world"
}
```

```json
{
  "action": "sync"
}
```

## CLI Usage (Legacy)

```bash
node skills/interaction-logger/index.js --action log --target <target_alias> --role <role> --content <message>
```

## Arguments

- `--action`: `log` or `sync`
- `--target`: The user alias.
  - `zhy`, `shiqi`, `master` -> `memory/master_history.json`
  - `fmw`, `big-brother` -> `fmw/history.json`
- `--role`: Who is speaking (`user` | `assistant` | `system`). Default: `assistant`.
- `--content`: The text content to log.

## Why use this?
- **Safety**: Prevents JSON syntax errors from manual editing.
- **Convenience**: One-line command vs multi-step read/edit/write.
- **Compliance**: Ensures mandatory logging rules (from MEMORY.md) are actually followed.

## Features
- **Atomic Writes**: Uses `.tmp` file + rename to prevent corruption on crash.
- **Log Rotation**: Automatically rotates log files when they exceed 5MB to `filename_YYYY-MM-DD-HHmmss.json`.
- **Dynamic Targets**: Auto-creates log files for new users in `memory/users/`.
- **Sync**: Automatically syncs session logs to history files.
