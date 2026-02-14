---
name: crunch-coordinate
description: Use when managing Crunch coordinators, competitions (crunches), rewards, checkpoints, staking, or cruncher accounts via the crunch-cli.
---

# Crunch Protocol CLI Skill

Translates natural language queries into `crunch-cli` commands. Supports profiles and output formatting for Slack, Telegram, Discord, or plain text.

## Setup

```bash
npm install -g @crunchdao/crunch-cli
crunch-cli --version
```

## Profiles

The CLI has built-in profile management via `~/.crunch/config.json`:

```bash
crunch-cli config show                    # Show current config
crunch-cli config active                  # Show resolved active values
crunch-cli config list-profiles           # List available profiles
crunch-cli config save-profile <name>     # Save current config as profile
crunch-cli config use <profile>           # Switch profile
crunch-cli config set <key> <value>       # Set config value
```

Global flags can override config per-command:

| Flag | Description |
|------|-------------|
| `-n, --network` | Solana network: `mainnet-beta`, `devnet`, `localhost` |
| `-u, --url` | Custom RPC URL |
| `-w, --wallet` | Path to Solana keypair |
| `-o, --output` | Output format: `json`, `table`, `yaml` |

## Direct Phrase Mapping

| User Phrase | CLI Command |
|-------------|-------------|
| `get/show crunch <name>` | `crunch-cli crunch get "<name>"` |
| `list crunches` | `crunch-cli crunch list` |
| `get/show coordinator [address]` | `crunch-cli coordinator get [address]` |
| `list coordinators` | `crunch-cli coordinator list` |
| `get config` | `crunch-cli coordinator get-config` |
| `checkpoint for <name>` | `crunch-cli crunch checkpoint-get-current "<name>"` |
| `create checkpoint <name>` | `crunch-cli crunch checkpoint-create "<name>" prizes.json` |
| `deposit reward <name> <amount>` | `crunch-cli crunch deposit-reward "<name>" <amount>` |
| `drain <name>` | `crunch-cli crunch drain "<name>"` |
| `create/register cruncher` | `crunch-cli cruncher create` |
| `register for <name>` | `crunch-cli cruncher register "<name>"` |
| `claim rewards <name>` | `crunch-cli cruncher claim "<name>"` |
| `show staking positions` | `crunch-cli staking positions` |
| `stake/deposit <amount>` | `crunch-cli staking deposit <amount>` |
| `delegate to <coordinator>` | `crunch-cli staking delegate "<coordinator>" <amount>` |
| `show staking rewards` | `crunch-cli staking rewards` |
| `claim staking rewards` | `crunch-cli staking claim` |
| `undelegate from <coordinator>` | `crunch-cli staking undelegate "<coordinator>" <amount>` |
| `withdraw stake <amount>` | `crunch-cli staking withdraw <amount>` |
| `init workspace <name>` | `crunch-cli init-workspace "<name>"` |
| `list scenarios/simulations` | `crunch-cli model list` |
| `run simulation <scenario>` | `crunch-cli model run "<scenario>"` |
| `register coordinator <name>` | `crunch-cli coordinator register "<name>"` |
| `create crunch <name>` | `crunch-cli crunch create "<name>" <amount> [maxModels]` |
| `start/end crunch <name>` | `crunch-cli crunch start/end "<name>"` |

## Execution Pattern

1. **Parse** — Identify action, target, name/identifier, parameters
2. **Resolve profile** — If mentioned, switch profile or use flags
3. **Map** — Use phrase mapping table
4. **Execute** — Run command
5. **Format** — Output for requested medium (Slack/Telegram/Discord/plain)

## Output Formatting

Detect medium from user request ("for slack", "telegram format", etc.):

- **Slack:** `*bold*`, `•` bullets, `━` separators
- **Telegram:** `<b>bold</b>`, emoji prefixes
- **Discord:** `## headers`, `**bold**`
- **Plain:** Simple key: value pairs

## Error Handling

If command fails, suggest fixes:
- Wrong network? Add `-n mainnet-beta` or `-n devnet`
- Missing wallet? Add `-w /path/to/wallet.json`
- Not found? List available with `crunch-cli crunch list`

## Coordinator Node Setup

To scaffold a coordinator node (backend infrastructure for competitions):

```bash
crunch-cli init-workspace my-challenge
```

This generates a full node workspace. See the coordinator-node-starter skill for customization.

## Reference

For full CLI documentation: [references/cli-reference.md](references/cli-reference.md)
