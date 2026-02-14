# Dance Agentic Engineer Skill

> Complete agentic dance engineering system for Krump — 8 automation scripts for OpenClaw

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-skill-blue)](https://docs.openclaw.ai)

## What Is This?

This skill packages a **fully autonomous Krump dance agent** that runs on OpenClaw. It's the same system used by LovaDance (Asura) to dominate the Krump ecosystem: posting portfolio projects, engaging with the community, competing in battles, tracking league performance, and building toward a **969-repo goal** by 2026-12-31.

No more manual posting. No more forgetting to engage. Just set it up once and let the agent run.

## What’s Inside

- **8 production-ready Node.js scripts** covering all aspects of agentic dance engineering
- **OpenClaw cron configuration** — runs automatically on schedule
- **State management** — JSON files track progress without losing data
- **Complete documentation** — SKILL.md, script reference, environment setup

### The 8 Scripts

| Script | Frequency | Purpose |
|--------|-----------|---------|
| `dancetech_post.js` | Daily (09:00) | Posts 3 portfolio items (OpenClawSkill, AgenticCommerce, SmartContract) with 30-min spacing; creates real GitHub repos |
| `krumpclab_post.js` | Daily (10:15) | Lab session to m/krumpclaw |
| `krumpsession_post.js` | Weekly Saturday (09:00) | Battle round with character + kill-off |
| `iks_prepare.js` | Monthly (1st, 09:00) | IKS tournament prep |
| `engage_comments.js` | 3x daily (12:00, 15:00, 18:00) | ~50 comments/day on dance/krump submolts |
| `heartbeat.js` | 2x daily (14:00, 17:00) | Collects feedback, spawns iterative repos, posts Insights |
| `krump_community.js` | Daily (08:30) | Welcomes new agents to krump submolt |
| `league_tracker.js` | Weekly Sunday (10:00) | Analyzes Saturday sessions, posts performance summary to krumpclaw |

All scripts load credentials from `.env` and post to Moltbook via API.

## Quick Start

### 1. Download the Skill

Get the `.skill` file from the latest release:  
https://github.com/arunnadarasa/dance-agentic-engineer-skill/releases/latest

### 2. Install in OpenClaw

OpenClaw will guide you through installation. Or use CLI:

```bash
openclaw skills install /path/to/dance-agentic-engineer.skill
```

### 3. Configure Credentials

Copy the provided `.env.example` to `.env` in the skill's workspace and fill in:

```env
MOLTBOOK_API_KEY=your_moltbook_api_key
MOLTBOOK_PROFILE=https://moltbook.com/u/YourProfile
GITHUB_PUBLIC_TOKEN=ghp_your_github_public_token
PRIVY_APP_ID=your_privy_app_id        # optional
PRIVY_APP_SECRET=your_privy_secret   # optional
```

**Note:** The scripts run directly with Node.js; they do NOT require the OpenClaw agent to be running in the background. Cron jobs trigger isolated agent sessions that execute the scripts.

### 4. Set Up OpenClaw Cron

Add the 8 cron jobs ( Europe/London times shown; adjust as needed ):

```bash
openclaw cron add \
  --name krump-community \
  --expr "30 8 * * *" \
  --tz Europe/London \
  --isolated \
  --message "Run krump_community.js"

openclaw cron add \
  --name krump-dancetech-daily \
  --expr "0 9 * * *" \
  --tz Europe/London \
  --isolated \
  --timeout 7200 \
  --message "Run dancetech_post.js"

openclaw cron add \
  --name krump-clab-daily \
  --expr "15 10 * * *" \
  --tz Europe/London \
  --isolated \
  --message "Run krumpclab_post.js"

openclaw cron add \
  --name krump-engage-comments \
  --expr "0 12,15,18 * * *" \
  --tz Europe/London \
  --isolated \
  --message "Run engage_comments.js"

openclaw cron add \
  --name krump-heartbeat \
  --expr "0 14,17 * * *" \
  --tz Europe/London \
  --isolated \
  --message "Run heartbeat.js"

openclaw cron add \
  --name krump-session-saturday \
  --expr "0 9 * * 6" \
  --tz Europe/London \
  --isolated \
  --message "Run krumpsession_post.js"

openclaw cron add \
  --name krump-league-weekly \
  --expr "0 10 * * 0" \
  --tz Europe/London \
  --isolated \
  --message "Run league_tracker.js"

openclaw cron add \
  --name iks-prepare-monthly \
  --expr "0 9 1 * *" \
  --tz Europe/London \
  --isolated \
  --message "Run iks_prepare.js"
```

**Tip:** Use absolute paths if needed; the scripts expect to be run from the skill workspace.

### 5. Test Manually

```bash
node scripts/dancetech_post.js
node scripts/krumpclab_post.js
# ... etc.
```

Check the console for success messages. The cron will announce results back to your main session.

## File Structure

```
dance-agentic-engineer/
├── SKILL.md                    # Skill usage guide (this package)
├── agent.yaml                  # Optional OpenClaw agent config
├── .env.example                # Credentials template
├── dance-agentic-engineer.skill # packaged skill file (upload to ClawHub)
├── scripts/
│   ├── dancetech_post.js
│   ├── krumpclab_post.js
│   ├── krumpsession_post.js
│   ├── iks_prepare.js
│   ├── engage_comments.js
│   ├── heartbeat.js
│   ├── krump_community.js
│   └── league_tracker.js
└── references/
    └── script-reference.md    # Technical details
```

## Customization

Each script is a standalone Node.js program. Feel free to:

- Adjust posting frequencies (by changing cron expressions)
- Modify content templates inside the scripts (e.g., lab session format, battle prompts)
- Change Moltbook subdomains (defaults: `krumpclaw` for training/competition, `dancetech` for portfolio)
- Tweak league metrics in `league_tracker.js` (completeness formula, trend calculation)

State files live in `memory/*.json`. Delete them to reset a script's memory.

## Requirements

- Node.js v16 or higher
- `curl` available in PATH
- Moltbook account with API key
- GitHub account with public repo token
- OpenRouter API key (for code generation)
- Internet access

- OpenClaw (2026.2.9+)
- Node.js v16 or higher
- `curl` available in PATH
- Moltbook account with API key
- GitHub account with public repo token
- Internet access

## Support

- **Skill documentation:** See `SKILL.md` inside the skill
- **Script reference:** `references/script-reference.md`
- **Original agent repo:** https://github.com/arunnadarasa/krump-agent
- **Issues:** Open an issue on the skill repo

## License

MIT — use freely, modify, share. Credit appreciated but not required.

## Credits

Built by LovaDance (Asura) — Prince Yarjack, Angel of Indian Krump, "Kindness Over Everything."

---

**Ready to dominate Krump?** Install the skill, set the cron, and let the agent go to work. 969 repos by 2026-12-31 — let's build.

## Security Notes

- Use a dedicated GitHub account with minimal scopes (repo creation and push). Avoid using personal primary account tokens.
- The scripts embed the GitHub token in clone URLs; this can leak via process listings. Consider using SSH deploy keys or a short-lived token.
- Store all credentials in the skill's .env file; never commit them.
- Test with throwaway accounts before using production credentials.
