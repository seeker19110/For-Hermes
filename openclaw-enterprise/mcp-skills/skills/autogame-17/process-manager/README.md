# Process Manager Skill

A utility skill to manage, list, and kill processes safely.
This automates the manual pattern of using `exec` to run `ps`, `kill`, or check process status.

## Features
- List running processes matching a pattern
- Kill processes by PID or pattern (with safety checks)
- Check resource usage of specific processes

## Usage
```bash
# List processes matching "node"
node skills/process-manager/index.js list --pattern "node"

# Kill a process by PID
node skills/process-manager/index.js kill --pid 12345

# Kill processes by pattern (requires confirmation flag)
node skills/process-manager/index.js kill --pattern "defunct_script" --force
```
