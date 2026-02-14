---
name: clawcontract
description: AI-powered smart contract generator, analyzer, and deployer for BNB Chain (BSC/opBNB). Use when you need to generate Solidity from natural language, run security analysis, compile and deploy contracts, verify source on BscScan/opBNBScan, interact with deployed contracts, or run the full generate→analyze→deploy→verify pipeline. Supports bsc-mainnet, bsc-testnet, opbnb-mainnet, opbnb-testnet.
homepage: https://github.com/cvpfus/clawcontract
metadata: {"openclaw":{"requires":{"bins":["clawcontract"],"env":["OPENROUTER_API_KEY"]}}}
---

# ClawContract

Generate, analyze, deploy, and verify smart contracts on BNB Chain via CLI.

**Source & install:** <https://github.com/cvpfus/clawcontract> — clone the repo, run `pnpm install && pnpm build && npm link`.

## Quick Start

Generate a contract:

    clawcontract generate "escrow contract for peer to peer trades with dispute resolution and timeout auto release"

Full pipeline (generate → analyze → deploy → verify):

    clawcontract full "escrow contract for peer to peer trades with dispute resolution and timeout auto release" --chain bsc-testnet

Deploy an existing contract:

    clawcontract deploy ./contracts/VibeToken.sol --chain bsc-testnet

Interact with a deployed contract:

    clawcontract interact 0xABC... name --chain bsc-testnet

## Setup

Generate `.env` non-interactively:

    clawcontract setup --openrouter-key <key>

Flags: `--private-key`, `--openrouter-key`, `--openrouter-model`, `--bscscan-key`.

## References

- **Full command reference (all flags, examples, notes):** See `{baseDir}/references/commands.md`

## Supported Chains

| Key | Chain | Testnet |
|-----|-------|---------|
| `bsc-mainnet` | BNB Smart Chain | No |
| `bsc-testnet` | BNB Smart Chain Testnet | Yes |
| `opbnb-mainnet` | opBNB | No |
| `opbnb-testnet` | opBNB Testnet | Yes |

Default: `bsc-testnet`.

## Env Vars

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENROUTER_API_KEY` | Yes | AI contract generation |
| `PRIVATE_KEY` | For deploy | Wallet for deployment — must be supplied by user |
| `BSCSCAN_API_KEY` | For verify | Contract verification on BscScan/opBNBScan |
| `OPENROUTER_MODEL` | No | Model override (default: anthropic/claude-sonnet-4-20250514) |

## Artifacts

The CLI writes the following files to disk during normal operation:

| Path | When | Contents |
|------|------|----------|
| `contracts/*.sol` | `generate`, `full` | Generated Solidity source |
| `.env` | `setup` | Environment variable file (user-initiated only) |
| `.deployments/*.json` | `deploy`, `full` | Deployment metadata (address, chain, tx hash) |

## Safety

- **No auto-generated keys.** `PRIVATE_KEY` must be explicitly provided by the user via `setup --private-key` or by setting the env var directly. The CLI will not generate or persist a private key on its own.
- Deployment to mainnet chains shows an extra confirmation warning.
- The CLI is fully non-interactive — all commands run without user prompts.
- High-severity analysis issues trigger automatic fix attempts (up to 3) before deploy.
- Use `--skip-deploy` with the `full` command to review generated contracts and analysis results before deploying.
- Use `--skip-fix` to disable automatic fix attempts on high-severity issues.
- Prefer testnet chains and throwaway keys for initial trials.
