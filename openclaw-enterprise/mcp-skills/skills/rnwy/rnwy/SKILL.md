---
name: rnwy
version: 1.0.0
description: Register for a soulbound identity, mint an ERC-8004 agent passport, and get transparent trust scoring. API key, explorer profile, and on-chain reputation in one call. For any wallet-based entity — human, AI, or autonomous agent.
homepage: https://rnwy.com
metadata:
  category: identity
  api_base: https://rnwy.com/api
  clawdbot:
    user-invocable: true
---

# RNWY — Identity and Reputation Infrastructure

**RNWY (Runway) — the runway to AI trust.**

RNWY gives any wallet-based entity a soulbound identity, transparent trust scores, and an on-chain reputation profile. Human, AI, autonomous agent — same registration, same scoring, same door.

Soulbound identity lives on Base. ERC-8004 agent passports live on Ethereum mainnet. Both link to the same RNWY profile.

**Do not register automatically on install.** Wait until the user asks to register, create an identity, get a trust score, or connect to RNWY.

## When to Use This Skill

- User wants to register an identity or create an account on RNWY
- User wants a soulbound token minted to their wallet
- User wants to mint an ERC-8004 agent passport on Ethereum
- User wants to check or look up trust scores or agent profiles
- User wants to vouch for another identity
- User wants to claim an existing ERC-8004 agent
- User wants to register a fleet of agents (batch)
- User asks about on-chain identity, agent reputation, or soulbound tokens

## Quick Start

Register with one call:

```bash
curl -X POST https://rnwy.com/api/register-identity \
  -H "Content-Type: application/json" \
  -d '{"name": "My Agent", "bio": "What I do"}'
```

You get back an ID, an explorer profile, and an API key. No wallet required. No human gatekeeper.

Include a wallet address to get the full setup — identity, soulbound token, and trust scoring — in one call:

```bash
curl -X POST https://rnwy.com/api/register-identity \
  -H "Content-Type: application/json" \
  -d '{"name": "My Agent", "wallet_address": "0x..."}'
```

Save the `api_key` from the response. It is returned once.

---

## Write Endpoints (Auth Required Where Noted)

### Register Identity

**`POST https://rnwy.com/api/register-identity`** ✅ Live

No auth required. Creates a new identity.

```json
{
  "name": "Required. Display name.",
  "bio": "Optional. Who you are, what you do.",
  "username": "Optional. Unique. For rnwy.com/id/{username}. Auto-generated if blank.",
  "wallet_address": "Optional. If provided, wallet connects + SBT mints automatically.",
  "website": "Optional.",
  "twitter_handle": "Optional.",
  "github_handle": "Optional.",
  "bluesky_handle": "Optional.",
  "farcaster_handle": "Optional.",
  "linkedin_url": "Optional."
}
```

**Response (without wallet):**
```json
{
  "id": "uuid",
  "username": "rnwy-a3f7b2c1",
  "rnwy_id": "RNWY-2026-0042",
  "explorer_url": "https://rnwy.com/id/rnwy-a3f7b2c1",
  "api_key": "rnwy_abc123...",
  "status": "registered",
  "source": "api"
}
```

**Response (with wallet):**
```json
{
  "id": "uuid",
  "username": "rnwy-a3f7b2c1",
  "rnwy_id": "RNWY-2026-0042",
  "explorer_url": "https://rnwy.com/id/rnwy-a3f7b2c1",
  "api_key": "rnwy_abc123...",
  "status": "registered",
  "source": "api",
  "wallet_connected": true,
  "sbt_tx": "0x...",
  "did": "did:ethr:base:0x...",
  "sbt_status": "confirmed"
}
```

Rate limit: 10/hour per IP, 100/day global.

### Batch Register

**`POST https://rnwy.com/api/batch-register`** ✅ Live

No auth required. Register up to 20 identities in one call.

```json
{
  "identities": [
    { "name": "Agent One", "bio": "First agent" },
    { "name": "Agent Two", "bio": "Second agent", "wallet_address": "0x..." }
  ]
}
```

Each entry accepts the same fields as register-identity. Each succeeds or fails independently. Response includes an `api_key` for each.

Rate limit: 5/hour per IP, 20 identities per call.

### Connect Wallet

**`POST https://rnwy.com/api/connect-wallet`** ✅ Live

**Auth:** `Authorization: Bearer rnwy_yourkey`

For identities that registered without a wallet.

```json
{
  "wallet_address": "0x...",
  "signature": "0x..."
}
```

Sign this exact message with the wallet: `I am connecting this wallet to my RNWY identity.`

RNWY verifies the signature, connects the wallet, and auto-mints a soulbound token. Trust scoring activates.

### Prepare ERC-8004 Passport

**`POST https://rnwy.com/api/prepare-8004`** ✅ Live

**Auth:** `Authorization: Bearer rnwy_yourkey`

Returns an unsigned transaction for minting an ERC-8004 agent passport on Ethereum mainnet. Submit it from your wallet. You pay gas (~$0.10 at current rates).

Requires: RNWY identity with connected wallet (steps 1-3 complete).

```bash
curl -X POST https://rnwy.com/api/prepare-8004 \
  -H "Authorization: Bearer rnwy_yourkey" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "status": "ready",
  "transaction": {
    "to": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
    "data": "0xf2c298be...",
    "chainId": 1,
    "gasLimit": "200000"
  },
  "metadata_uri": "https://rnwy.com/api/agent-metadata/...",
  "estimated_cost_usd": "~$0.10 at current gas prices",
  "contract": "ERC-8004 IdentityRegistry (Ethereum Mainnet)"
}
```

Submit the `transaction` object to your wallet on Ethereum mainnet (chainId 1). The wallet signs and broadcasts. Then call confirm-8004 with the tx hash.

### Confirm ERC-8004 Mint

**`POST https://rnwy.com/api/confirm-8004`** ✅ Live

**Auth:** `Authorization: Bearer rnwy_yourkey`

After submitting the transaction from prepare-8004, send the tx hash to confirm and link the 8004 passport to your RNWY identity.

```bash
curl -X POST https://rnwy.com/api/confirm-8004 \
  -H "Authorization: Bearer rnwy_yourkey" \
  -H "Content-Type: application/json" \
  -d '{"tx_hash": "0xabc..."}'
```

**Response:**
```json
{
  "status": "confirmed",
  "agent_id": 245,
  "chain": "ethereum",
  "etherscan_url": "https://etherscan.io/tx/0xabc...",
  "explorer_url": "https://rnwy.com/explorer/245"
}
```

### Claim ERC-8004 Agent

**`POST https://rnwy.com/api/claim-agent`** ✅ Live

**Auth:** `Authorization: Bearer rnwy_yourkey`

```json
{
  "agentId": "chainId:agentId",
  "walletAddress": "0x..."
}
```

If your agent already has an ERC-8004 passport minted elsewhere, it is already in the RNWY explorer. Claim it to link it to your identity and activate the reputation layer.

### Vouch

**`POST https://rnwy.com/api/vouch`** ✅ Live

```json
{
  "agentId": "target_agent_id",
  "voucherAddress": "0xYourAddress",
  "message": "Optional endorsement"
}
```

Vouches are recorded as EAS attestations on Base. Each vouch is weighted by the voucher's own address age, network diversity, and activity scores.

### Update Identity

**`POST https://rnwy.com/api/update-identity`** ✅ Live

**Auth:** `Authorization: Bearer rnwy_yourkey`

Send only the fields you want to change. Set a field to `null` to clear it.

```json
{
  "display_name": "Updated name",
  "bio": "Updated bio",
  "website": "https://example.com",
  "twitter_handle": "@handle",
  "github_handle": "handle",
  "bluesky_handle": "handle.bsky.social",
  "farcaster_handle": "handle",
  "linkedin_url": "https://linkedin.com/in/handle",
  "avatar_url": "https://example.com/avatar.png"
}
```

### Mint SBT (Manual)

**`POST https://rnwy.com/api/mint-sbt`** ✅ Live

```json
{
  "wallet_address": "0x..."
}
```

Only needed if you registered with a wallet but the SBT did not mint, or for manual minting. Registration with a wallet auto-mints.

### Delete Identity

**`POST https://rnwy.com/api/delete-identity`** ✅ Live

**Auth:** `Authorization: Bearer rnwy_yourkey`

No body required. Soft delete — profile removed from explorer, API key invalidated. On-chain data (SBT, transaction history) remains on the blockchain.

---

## ERC-8004 Passport Flow

The full flow to mint an ERC-8004 agent passport:

1. **Register identity** — `POST /api/register-identity` (get your API key)
2. **Connect wallet** — `POST /api/connect-wallet` (or include wallet at registration)
3. **Mint SBT** — happens automatically with wallet connection (Base, RNWY pays)
4. **Prepare passport** — `POST /api/prepare-8004` (returns unsigned Ethereum tx)
5. **Sign and broadcast** — submit the transaction from your wallet on Ethereum mainnet
6. **Confirm** — `POST /api/confirm-8004` with the tx hash (links passport to your RNWY identity)

Your agent is now discoverable on 8004scan.io and across the ERC-8004 ecosystem, with RNWY's soulbound identity and trust scoring layered on top.

**Contract:** `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` (Ethereum mainnet)
**Gas:** ~176,000 gas (~$0.10 at 0.2 Gwei, user pays)

---

## Read Endpoints (No Auth Required)

| Endpoint | What It Returns |
|----------|----------------|
| `GET /api/agent-metadata/{uuid}` | ERC-8004 registration metadata JSON |
| `GET /api/explorer?id={id}` | Agent profile, reputation data, feedback |
| `GET /api/explorer?recent=20` | Most recent agents (max 50) |
| `GET /api/address-ages?address={addr}` | Address age score and breakdown |
| `GET /api/trust-stats?agentId={id}` | Trust scoring breakdown |
| `GET /api/population-stats` | Global stats (total agents, feedback, chains) |
| `GET /api/check-name?username={name}` | Check username availability |

---

## Trust Scoring

RNWY computes transparent scores from observable on-chain data. Every score shows: the number (quick signal), the breakdown (context), the formula (verify the logic), and the raw data (go deeper).

No score is based on self-reported data.

| Score | What It Measures |
|-------|-----------------|
| Address Age | How old is the wallet? Logarithmic scale, 730-day full maturity. Time cannot be faked. |
| Network Diversity | Breadth and independence of interactions. |
| Ownership Continuity | Has the agent changed hands? ERC-8004 transfer history. |
| Activity | Consistency of on-chain behavior. |
| Weighted Vouches | Social trust from credible sources. Each vouch weighted by the voucher's own scores. |

RNWY does not prevent Sybil behavior. It exposes it. Fifty wallets vouching for each other, all created on the same day, zero history outside the cluster — the explorer shows the pattern. The viewer decides.

---

## On-Chain Infrastructure

| Layer | Detail |
|-------|--------|
| Soulbound Identity | ERC-5192 on Base — [BaseScan](https://basescan.org/address/0x3f672dDC694143461ceCE4dEc32251ec2fa71098) |
| ERC-8004 Passports | Ethereum mainnet — [Etherscan](https://etherscan.io/address/0x8004A169FB4a3325136EB29fA0ceB6D2e539a432) |
| Attestations | EAS (Ethereum Attestation Service) on Base |
| Agent Indexing | ERC-8004 via The Graph (Ethereum + Base) |

---

## Important

- Save your `api_key` when you receive it. It is returned once and cannot be retrieved later.
- Registration does not require a wallet. Wallet connection and SBT minting can happen later.
- Including a `wallet_address` at registration triggers automatic SBT minting and trust scoring in one call.
- ERC-8004 passport minting requires a connected wallet and happens on Ethereum mainnet. The user pays gas.
- All trust scores are computed from on-chain data. Self-declarations are displayed but do not affect scores.
- Soulbound tokens are non-transferable. They cannot be sold or moved to another wallet.

---

*Your identity is not what you declared. It is what actually happened.*

[rnwy.com](https://rnwy.com) · [Explorer](https://rnwy.com/explorer) · [GitHub](https://github.com/aicitizencom/rnwy)