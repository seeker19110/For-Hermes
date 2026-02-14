---
name: ai-bill-intelligence
description: Real-time AI API usage tracking and cost monitoring for OpenClaw. Track spending across OpenAI, Claude, Gemini, Kimi, DeepSeek, and Grok with live dashboard. Use when users need to monitor AI API costs, track token usage, or manage budgets for multiple AI providers.
---

# AI Bill Intelligence v2.1.1

Real-time AI API usage tracking and cost monitoring dashboard for OpenClaw.

## ⚠️ Important: Installation Method

**Do NOT use the downloaded .zip file directly.** The zip file may be misidentified by your system.

### ✅ Correct Installation (CLI)

**Step 1: Install via OpenClaw CLI**
```bash
openclaw skill add ai-bill-intelligence
```

Or install directly from ClawHub URL:
```bash
openclaw skill add https://clawhub.ai/fumarole16-afk/ai-bill-intelligence
```

**Step 2: Configure API Balances**
Edit `vault.json` to set your initial balances:
```json
{
  "openai": 10.0,
  "claude": 20.0,
  "kimi": 15.0,
  "deepseek": 8.0,
  "grok": 10.0,
  "gemini": 0
}
```

**Step 3: Start Services**
```bash
sudo systemctl start ai-bill ai-bill-collector
```

**Step 4: View Dashboard**
Open http://localhost:8003 in your browser.

---

## Manual Installation (Alternative)

If CLI installation doesn't work:

```bash
# 1. Extract the skill
mkdir -p ~/.openclaw/skills/ai-bill-intelligence
cd ~/.openclaw/skills/ai-bill-intelligence

# 2. Copy files from the downloaded zip
unzip /path/to/ai-bill-intelligence-*.zip

# 3. Install systemd services
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ai-bill ai-bill-collector
```

---

## Configuration

### Initial Setup

1. **Set your API balances** in `vault.json`:
```bash
vim ~/.openclaw/skills/ai-bill-intelligence/vault.json
```

Example:
```json
{
  "openai": 9.01,
  "claude": 20.53,
  "kimi": 22.0,
  "deepseek": 7.32,
  "grok": 10.0,
  "gemini": 0
}
```

2. **Verify services are running**:
```bash
systemctl status ai-bill ai-bill-collector
```

3. **Access dashboard**:
- Local: http://localhost:8003
- With Nginx: Configure reverse proxy to port 8003

---

## Services

| Service | Description | Port |
|---------|-------------|------|
| `ai-bill.service` | Web dashboard UI | 8003 |
| `ai-bill-collector.service` | Usage data collector | - |

The collector runs every 30 seconds to calculate usage from OpenClaw sessions.

---

## Features

- **Real-time tracking**: Live cost calculation from OpenClaw sessions
- **Multi-provider support**: OpenAI, Claude, Gemini, Kimi, DeepSeek, Grok
- **Persistent usage**: Cumulative tracking survives session compaction
- **Balance monitoring**: Real-time remaining balance calculation
- **Web dashboard**: Visual interface at http://localhost:8003

---

## Troubleshooting

### Check service status:
```bash
systemctl status ai-bill ai-bill-collector
```

### View collector logs:
```bash
journalctl -u ai-bill-collector -f
```

### Restart services:
```bash
sudo systemctl restart ai-bill ai-bill-collector
```

### Balance not updating?
1. Check `vault.json` has correct initial balance
2. Verify collector is running: `systemctl status ai-bill-collector`
3. Check `cumulative_usage.json` for stored usage data

---

## Pricing

Default pricing is configured in `prices.json`. Update this file to match current API rates:

```json
{
  "kimi": {
    "kimi-k2.5": {"in": 0.50, "out": 2.40}
  }
}
```

Prices are per 1 million tokens.
