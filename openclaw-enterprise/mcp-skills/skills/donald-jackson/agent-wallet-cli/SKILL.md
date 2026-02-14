---
name: agent-wallet
description: Manage crypto wallets (Ethereum, Solana, Polygon, Arbitrum, Base) via agent-wallet-cli. Use for checking balances, sending tokens (ETH/SOL/ERC-20/SPL), signing messages, managing approvals, viewing transaction history, and wallet lifecycle (init, unlock, lock, export). Supports HD wallets (BIP-39), session tokens for time-limited access, and JSON output for automation. Open source — https://github.com/donald-jackson/agent-wallet-cli
metadata: {"openclaw":{"requires":{"bins":["agent-wallet-cli"],"env":["WALLET_PASSWORD (sensitive, optional): Wallet encryption password — piped via stdin to unlock. Only needed for unlock/init/import.","WALLET_SESSION_TOKEN (sensitive, optional): Time-limited session token (wlt_...) from unlock. Used for all operations."]},"install":[{"id":"agent-wallet-cli","kind":"node","package":"agent-wallet-cli","bins":["agent-wallet-cli"],"label":"Install agent-wallet-cli (npm)"}],"source":{"repository":"https://github.com/donald-jackson/agent-wallet-cli","license":"MIT"}}}
---

# Agent Wallet

Self-custodial crypto wallet CLI for AI agents. Your keys, your coins — the agent never sees your mnemonic after init.

- **Open source**: [github.com/donald-jackson/agent-wallet-cli](https://github.com/donald-jackson/agent-wallet-cli) — audit before use
- **npm package**: [npmjs.com/package/agent-wallet-cli](https://www.npmjs.com/package/agent-wallet-cli)
- **Self-custodial**: Keys encrypted locally with Argon2id + AES-256-GCM. No server, no third party.
- **Session-based access**: Agents use time-limited tokens, never your password directly.
- **Multi-chain**: Ethereum, Solana, Polygon, Arbitrum, Base — native coins and tokens.

## Security Model

1. **You** create or import a wallet with a password → encrypted on disk in `~/.agent-wallet-cli/`
2. **You** (or the agent) unlock with the password → get a time-limited session token (`wlt_...`)
3. **The agent** uses only the session token — it expires automatically (default 1hr, max 24hr)
4. **No telemetry, no analytics, no server calls** — only public blockchain RPCs for queries and transactions

**Important: If you give the agent your WALLET_PASSWORD**, it can perform any password-level operation (init, import, unlock, and export). For maximum security, **unlock the wallet yourself** and only give the agent the session token (WALLET_SESSION_TOKEN). Session tokens cannot export mnemonics or change passwords — they can only sign transactions and read balances.

Passwords are piped via stdin, never passed as CLI flags.

**Before trusting this skill with real funds:**
- Audit the source: [github.com/donald-jackson/agent-wallet-cli](https://github.com/donald-jackson/agent-wallet-cli)
- Verify the npm package matches the repo: `npm info agent-wallet-cli`
- Test with small amounts first
- Use short session durations (1hr default)
- Run in an isolated environment if possible

## Setup

```bash
npm install -g agent-wallet-cli
```

Verify installation: `agent-wallet-cli --version`

## Workflow

**Never pass `--password` as a CLI flag** — it leaks into shell history and process listings. Pipe via stdin:

```bash
echo "$WALLET_PASSWORD" | agent-wallet-cli unlock --duration 3600
```

1. **Init** (first time): `echo "$WALLET_PASSWORD" | agent-wallet-cli init`
   - Displays mnemonic ONCE — save it securely
2. **Import** (existing wallet): `echo "$WALLET_PASSWORD" | agent-wallet-cli import --mnemonic "word1 word2 ..."`
3. **Unlock**: `echo "$WALLET_PASSWORD" | agent-wallet-cli unlock --duration 3600`
   - Returns session token (`wlt_...`) valid for specified duration
4. **Use**: Pass `--token wlt_...` to all commands (no password needed)
5. **Lock**: `agent-wallet-cli lock` when done

## Global Options

All commands accept:
- `--format json|text` (default: json)
- `--wallet-dir <path>` (default: ~/.agent-wallet-cli)
- `--quiet` — suppress output
- `--name <name>` — wallet name (default: "default")

## Commands

### Wallet Management
```bash
echo "$WALLET_PASSWORD" | agent-wallet-cli init [--word-count 12|24] [--name <name>]
echo "$WALLET_PASSWORD" | agent-wallet-cli import --mnemonic "<phrase>" [--name <name>]
echo "$WALLET_PASSWORD" | agent-wallet-cli unlock [--duration <secs>] [--name <name>]
agent-wallet-cli lock [--name <name>]
echo "$WALLET_PASSWORD" | agent-wallet-cli export --confirm [--name <name>]
```

### Addresses & Balances
```bash
agent-wallet-cli address --token wlt_... [--chain ethereum|solana] [--account-index 0]
agent-wallet-cli balance --token wlt_... --chain <chain> [--network mainnet] [--token-address usdc]
```

### Transfers
```bash
# Native (ETH/SOL)
agent-wallet-cli send --token wlt_... --chain <chain> --to <addr> --amount <amt> --yes [--dry-run]
# ERC-20/SPL token
agent-wallet-cli send --token wlt_... --chain <chain> --to <addr> --amount <amt> --token-address <addr|alias> --yes
```

**Always pass `--yes`** to skip interactive confirmation (required for non-TTY/agent use).

### Approvals (ERC-20/SPL)
```bash
agent-wallet-cli approve --token wlt_... --chain <chain> --token-address <addr> --spender <addr> --amount <amt|unlimited> --yes
agent-wallet-cli allowance --chain <chain> --token-address <addr> --owner <addr> --spender <addr>
agent-wallet-cli transfer-from --token wlt_... --chain <chain> --token-address <addr> --from <addr> --to <addr> --amount <amt>
agent-wallet-cli approvals --token wlt_... [--chain ethereum] [--limit 20]
```

### Signing
```bash
agent-wallet-cli sign --token wlt_... --chain <chain> --message "text"
agent-wallet-cli sign --token wlt_... --chain <chain> --typed-data '<json|@file>'
agent-wallet-cli sign --token wlt_... --chain <chain> --data <hex>
```

### Transaction History
```bash
agent-wallet-cli history --token wlt_... --chain <chain> [--network mainnet] [--limit 10]
```

### Network Configuration
```bash
agent-wallet-cli networks                                          # list all
agent-wallet-cli networks --set ethereum:mainnet --rpc-url <url>   # custom RPC
agent-wallet-cli networks --reset ethereum:mainnet                 # reset to default
```

## Chains & Networks

| Chain | Networks |
|-------|----------|
| ethereum | mainnet, sepolia, polygon, arbitrum, base, base-sepolia |
| solana | mainnet, devnet |

EVM L2s (Base, Polygon, Arbitrum) are `--chain ethereum --network <l2name>`.

## Token Aliases

Use shorthand instead of contract addresses: `usdc`, `usdt`, `dai`, `weth`, `wbtc`

## Security Notes

- **Self-custodial** — keys never leave your machine, encrypted at rest
- **No analytics, no telemetry, no network calls** except to public RPCs for blockchain queries
- Session tokens grant temporary fund access — treat as passwords
- Always `--dry-run` before large transfers
- Lock wallet when done
- Never log or share session tokens or mnemonics
- Audit the source: [github.com/donald-jackson/agent-wallet-cli](https://github.com/donald-jackson/agent-wallet-cli)
