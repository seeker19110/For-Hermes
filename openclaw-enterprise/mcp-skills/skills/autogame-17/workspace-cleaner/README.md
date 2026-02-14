# Workspace Cleaner

A skill to automatically clean up temporary files and old logs to maintain workspace hygiene.

## Usage

```bash
node skills/workspace-cleaner/index.js --dry-run
node skills/workspace-cleaner/index.js --execute
```

## Features

- Removes `.tmp`, `.bak`, `.log` files older than 7 days in `temp/`
- Cleans up empty directories in `temp/`
- Respects protected files
