# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Structure

```
12-factor-agents/
├── main.py              # Entry point - runs OpenClaw bot loop
├── openclaw-enterprise/ # Main Python application
│   ├── agents/          # SalesAgentWhale implementation
│   ├── scripts/         # Auth, DB, config, notifications
│   ├── workflows/       # Controller, memory manager
│   ├── training/        # Psychological triggers, sales scripts
│   └── mcp/            # MCP server config
├── packages/            # TypeScript agent templates
│   └── create-12-factor-agent/template/  # npx create-12-factor-agent
└── content/            # 12-factor agent documentation
```

## Commands

```bash
# Run the main bot
python3 main.py

# Run tests (in openclaw-enterprise/)
python3 -m pytest agents/test_*.py

# TypeScript projects
cd packages/create-12-factor-agent/template && npm run dev
```

## Project-Specific Patterns (Non-Obvious)

### Imports
- `main.py` adds `openclaw-enterprise` to sys.path: `sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openclaw-enterprise'))`
- All internal imports use this pattern

### Configuration
- Uses `claw_config.yaml` with Pydantic models
- Access via `scripts.config_manager.get_config()`
- Environment variables in `.env` file (see `.env.example`)

### Database
- SQLite at `data/user_profiles.db`
- Access via `scripts.database_manager.get_database()`

### State Recovery
- Bot saves cycle state to handle restarts
- Use `scripts.database_manager.load_cycle_state()` / `save_cycle_state()`

### Mock Mode
- Constructor accepts `mock_mode=True` for testing without real APIs
- Pass `--mock` or set in config

### Whale Detection
- Users with `spent_weekly > threshold` flagged as `is_whale`
- Different response generation for whales vs regular users

### Telegram Notifications
- Use `scripts.telegram_notifier.TelegramNotifier` for alerts

## Testing

```bash
# Run specific test
python3 openclaw-enterprise/agents/test_whale_integration.py

# Test auth
python3 openclaw-enterprise/scripts/test_tg_connection.py
```
