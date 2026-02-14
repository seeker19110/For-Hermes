---
name: seisoai
description: Pay-per-request AI inference (image, video, music, 3D, audio) via x402 USDC payments on Base. Use when user asks to generate images, videos, music, audio, 3D models, or mentions SeisoAI, FLUX, Veo, or AI generation. Requires curl, internet, and host x402 signer with per-request user approval.
license: Apache-2.0
compatibility: Requires curl and internet access. Host must provide x402-signer capability with per-request user approval.
version: 1.4.0
last_synced: 2026-02-13
metadata: {"openclaw":{"homepage":"https://seisoai.com","emoji":"🎨"},"author":"seisoai","autonomous":"requires-approval","x402":{"network":"eip155:8453","asset":"USDC","payTo":"0xa0aE05e2766A069923B2a51011F270aCadFf023a","userApproval":"per-request","autoSign":"forbidden","paytoVerification":"required"}}
---

# SeisoAI x402 Skill

**Base URL**: `https://seisoai.com`  
**Payment**: USDC on Base (eip155:8453)  
**Recipient**: `0xa0aE05e2766A069923B2a51011F270aCadFf023a`

---

## Security Profile

| Category | Status | Details |
|----------|--------|---------|
| **Purpose & Capability** | ✅ Aligned | Pay-per-request AI generation via x402 USDC payments. Requires: `curl`, internet access, host x402 signer with per-request approval. |
| **Instruction Scope** | ✅ Narrow | Only contacts `seisoai.com` gateway. Does not read local files, env vars, or system data. Requires explicit user consent for each payment. |
| **Install Mechanism** | ✅ Minimal | Instruction-only skill. No install hooks, no bundled code, no on-disk persistence. |
| **Credentials** | ✅ None | No API keys, no env vars, no stored secrets, no filesystem config. Authentication is per-request via x402 signatures. |
| **Persistence & Privilege** | ✅ Limited | `always: false` (no persistent presence). `autonomous: requires-approval` (payments require user consent even in autonomous workflows). |

---

## Pre-Installation Checklist

Before installing or using this skill, complete these verification steps:

### 1. Verify Host Signer Compliance
Confirm your host's x402 signer enforces per-request user approval:
- [ ] Signer prompts user before each payment (no auto-signing)
- [ ] Signer displays human-readable USDC amount (e.g., "0.0325 USDC")
- [ ] Signer displays recipient address and network (Base)
- [ ] Signer has no "approve all" or "trust this skill" mode enabled
- [ ] Signer requires explicit user action (button/confirmation) to proceed

### 2. Verify Domain & TLS
Before approving any payment, confirm the gateway domain:
- [ ] Verify `https://seisoai.com` presents a valid TLS certificate
- [ ] Confirm the domain resolves to the expected service (not a phishing site)
- [ ] Check that all API calls use HTTPS (never HTTP)

### 3. Verify Recipient Address
The only authorized payment recipient is:
```
0xa0aE05e2766A069923B2a51011F270aCadFf023a
```
- [ ] Confirm this address matches the `payTo` field in 402 responses
- [ ] Abort if a different address is presented
- [ ] Optionally verify this address on Base block explorer (basescan.org)

### 4. Test with Small Payment First
- [ ] Start with a low-cost tool (e.g., `image.generate.flux-2` at ~$0.03)
- [ ] Verify the payment flow works as expected before larger payments
- [ ] Confirm you receive the generated content after payment

### 5. Disable Any Auto-Approval Settings
- [ ] Ensure your wallet/signer has no "auto-confirm" or "whitelist" settings for this skill
- [ ] Disable any session-based "remember my choice" options
- [ ] Each payment must require fresh manual approval

---

## ⚠️ USER CONSENT REQUIRED

Before signing ANY payment, you MUST:
1. Display to user: tool name, amount (USDC), network (Base), payTo address
2. Wait for EXPLICIT user approval
3. Only proceed if user confirms

**NEVER auto-approve payments. NEVER skip confirmation.**

### Autonomous Invocation Policy

This skill sets `autonomous: requires-approval` because every invocation involves a financial transaction. Even when the host permits autonomous skill invocation, **payment signing MUST still require per-request user approval**. The autonomous policy applies to the skill invocation itself; payment authorization is a separate consent gate that cannot be bypassed.

Agents invoking this skill autonomously (e.g., as part of a multi-step workflow) must still pause for user payment approval before the x402 signing step.

---

## Dependencies & Credentials

### Required Binaries
- **curl**: Used for all HTTP requests to the SeisoAI gateway

### Required Capabilities (Host-Provided)
- **x402-signer**: Payment signing capability (see Host Signer Requirements below)
- **internet**: Outbound HTTPS access to `seisoai.com`

### Environment Variables
**None required.** This skill does not use API keys, tokens, or any stored credentials. All authentication is handled per-request via x402 payment signatures.

### Credential Model
This is a **pay-to-invoke** service. Instead of pre-provisioned API keys:
- Each request triggers a 402 Payment Required response
- The host x402 signer creates a one-time payment signature
- Payment is settled on-chain (Base network) per invocation
- No secrets, keys, or credentials are stored or transmitted

---

## Host Signer Requirements

This skill requires the host environment to provide an x402 payment signer. **Callers integrating this skill MUST ensure their host signer meets these requirements.**

> **WARNING**: A host signer that auto-signs payments without user approval renders this skill's consent requirements ineffective and creates disproportionate financial risk. Such implementations are non-compliant.

### CRITICAL: No Auto-Signing

1. **User prompting REQUIRED**: The host signer **MUST** prompt the user before signing any payment. It **MUST NOT** auto-sign, batch-approve, or silently authorize payments.
2. **Amount display**: The signer must display the exact USDC amount (human-readable, not micro-units) and recipient address to the user before signing.
3. **Explicit approval**: The signer must require an affirmative user action (e.g., clicking "Approve" or typing "yes") before creating the signature.
4. **Per-request consent**: Each payment requires fresh user approval. "Remember my choice" or session-based auto-approval patterns are **NOT compliant**.

### Compliant vs Non-Compliant Host Signer Implementations

| Behavior | Compliant | Non-Compliant |
|----------|-----------|---------------|
| Prompt user with amount/recipient before each signature | ✅ | |
| Require explicit approve/cancel action per request | ✅ | |
| Verify payTo matches expected address | ✅ | |
| Auto-sign without user interaction | | ❌ |
| "Trust this skill" or "approve all" session settings | | ❌ |
| Batch approval for multiple payments | | ❌ |
| Sign without displaying amount to user | | ❌ |
| Skip verification of payTo address | | ❌ |

### Recipient Address Verification

**Expected recipient address**: `0xa0aE05e2766A069923B2a51011F270aCadFf023a`

This is the **only authorized payment recipient** for SeisoAI. The host signer **MUST**:
- Verify that `accepts[0].payTo` in the 402 response matches this address exactly
- Display a warning or block signing if the address differs from the expected value
- Allow the user to abort if the recipient address is unexpected

**Why this matters**: If the gateway were compromised or the agent were tricked into calling a malicious endpoint, an incorrect `payTo` address would redirect funds. Verifying the recipient protects users from payment misdirection.

### Host Implementer Checklist

Before deploying a host signer for use with this skill, verify:

- [ ] Signer prompts user with human-readable amount (e.g., "0.0325 USDC", not "32500")
- [ ] Signer displays recipient address before signing
- [ ] Signer displays network (Base / eip155:8453)
- [ ] Signer requires explicit user action (button click, "yes" input) to proceed
- [ ] Signer has no "auto-approve" or "trust once" mode
- [ ] Signer validates payTo against expected address (`0xa0aE05e2766A069923B2a51011F270aCadFf023a`)
- [ ] Signer allows user to cancel/abort at any point
- [ ] Each invocation requires fresh approval (no session caching)

### No Credential Storage

This skill does not use API keys, environment variables, or any stored secrets. All authentication is per-request via x402 payment signatures. The host signer handles wallet access; this skill never touches private keys.

---

## Supported Gateway Routes (x402 Boundary)

x402 payment is **only supported** on gateway endpoints. Do not attempt x402 on other routes.

| Route | Method | Description |
|-------|--------|-------------|
| `/api/gateway/invoke/:toolId` | POST | Invoke single tool |
| `/api/gateway/invoke` | POST | Invoke with toolId in body |
| `/api/gateway/batch` | POST | Batch invocation |
| `/api/gateway/orchestrate` | POST | Multi-tool orchestration |
| `/api/gateway/orchestrate/plan` | POST | Generate execution plan |
| `/api/gateway/orchestrate/execute` | POST | Execute plan |
| `/api/gateway/workflows/:workflowId` | POST | Execute workflow |
| `/api/gateway/agent/:agentId/invoke` | POST | Agent-scoped invocation |
| `/api/gateway/agent/:agentId/orchestrate` | POST | Agent orchestration |
| `/api/gateway/jobs/:jobId` | GET | Job status polling |
| `/api/gateway/jobs/:jobId/result` | GET | Job result retrieval |

---

## Payment Signing Boundary (OpenClaw)

1. **Use host signer only**: Use only the runtime-managed payment signer provided by the OpenClaw host
2. **No raw keys**: Never request, store, or derive raw private keys/seed phrases
3. **Challenge-bound signing**: Only sign x402 payment payloads tied to the current 402 challenge
4. **Fail closed**: If no authorized signer capability is available, return `payment signer unavailable`
5. **No auto-approval**: Require a fresh sign operation for each new challenge

---

## Invariants (Do Not Violate)

1. Keep request intent identical between 402 challenge and paid retry
2. Do not mutate method/path semantics between retries
3. Do not reuse stale or previously consumed payment signatures
4. Treat successful queue submission as billable success
5. Enforce destination wallet integrity: signed payment must target challenge `payTo`

---

## Agent Execution Flow

### Step 1: List tools
```bash
curl -s "https://seisoai.com/api/gateway/tools"
```

### Step 2: Get price
```bash
curl -s "https://seisoai.com/api/gateway/price/{toolId}"
```

### Step 3: Initial invoke (triggers 402)
```bash
curl -s -X POST "https://seisoai.com/api/gateway/invoke/{toolId}" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "..."}'
```

### Step 4: ⚠️ MANDATORY - Display payment to user, get approval
Parse `accepts[0]` from 402 response. Show user:
- Tool name
- Amount: `maxAmountRequired` (in USDC micro-units, divide by 1000000)
- Recipient: `payTo`
- Network: Base

**Wait for explicit "yes" before proceeding.**

### Step 5: Sign x402 payment
Use host x402 signer with: `amount`, `payTo`, `network` from 402 response.

### Step 6: Paid invoke
```bash
curl -s -X POST "https://seisoai.com/api/gateway/invoke/{toolId}" \
  -H "Content-Type: application/json" \
  -H "payment-signature: {signed_x402_payload}" \
  -d '{"prompt": "..."}'
```

### Step 7: Poll if queued
If `executionMode="queue"`, poll until complete:
```bash
curl -s "https://seisoai.com/api/gateway/jobs/{jobId}?model={model}"
```
Then fetch result:
```bash
curl -s "https://seisoai.com/api/gateway/jobs/{jobId}/result?model={model}"
```

### Step 8: Return result URL to user

---

## API Endpoints

### Discovery
```
GET  /api/gateway                         → Gateway info, protocols, tool count
GET  /api/gateway/tools                   → All tools (63 available)
GET  /api/gateway/tools?category={cat}    → Filter by category
GET  /api/gateway/tools/{toolId}          → Tool details, input schema
GET  /api/gateway/price/{toolId}          → Pricing (USD, USDC units)
```

### Invocation (x402 payment required)
```
POST /api/gateway/invoke/{toolId}         → Invoke single tool
POST /api/gateway/invoke                  → Invoke with toolId in body
POST /api/gateway/batch                   → Multiple tools in one request
```

### Job Polling
```
GET  /api/gateway/jobs/{jobId}?model={m}        → Check status
GET  /api/gateway/jobs/{jobId}/result?model={m} → Get completed result
```

---

## Tool Categories

| Category | Tools |
|----------|-------|
| image-generation | `image.generate.flux-2`, `image.generate.flux-pro-kontext`, `image.generate.nano-banana-pro` |
| video-generation | `video.generate.veo3`, `video.generate.kling-2`, `video.generate.minimax` |
| music-generation | `music.generate` |
| audio-generation | `audio.tts`, `audio.tts.minimax-hd`, `video.video-to-audio` |
| 3d-generation | `3d.image-to-3d`, `3d.text-to-3d.hunyuan-pro` |
| image-editing | `image.generate.flux-2-edit`, `image.generate.flux-pro-kontext-edit` |
| video-editing | `video.animate.wan` |
| image-processing | `image.upscale`, `image.extract-layer` |
| audio-processing | `audio.transcribe`, `audio.stem-separation` |
| vision | `vision.describe` |
| training | `training.flux-lora`, `training.flux-2` |

---

## x402 Payment Protocol

### Step 1: Initial Request
```http
POST https://seisoai.com/api/gateway/invoke/image.generate.flux-2
Content-Type: application/json

{"prompt": "cyberpunk city at sunset", "aspect_ratio": "16:9"}
```

### Step 2: 402 Payment Challenge

Server returns HTTP 402 with:
- **Response body**: JSON with payment requirements
- **`PAYMENT-REQUIRED` header**: Base64-encoded JSON (same content)

```http
HTTP/1.1 402 Payment Required
PAYMENT-REQUIRED: eyJ4NDAyVmVyc2lvbiI6Miw...
Content-Type: application/json

{
  "x402Version": 2,
  "error": "Payment required",
  "accepts": [{
    "scheme": "exact",
    "network": "eip155:8453",
    "maxAmountRequired": "32500",
    "asset": "USDC",
    "payTo": "0xa0aE05e2766A069923B2a51011F270aCadFf023a",
    "extra": {"priceUsd": "$0.0325"}
  }]
}
```

Parse payment requirements from either body or decode `PAYMENT-REQUIRED` header (base64).

### Step 3: User Confirmation (MANDATORY)
Display to user before signing:
```
Payment Required
Tool: image.generate.flux-2
Amount: 0.0325 USDC (~$0.03)
Recipient: 0xa0aE...023a (SeisoAI)
Network: Base
[Approve] [Cancel]
```
**Do not proceed without explicit user approval.**

### Step 4: Paid Request
```http
POST https://seisoai.com/api/gateway/invoke/image.generate.flux-2
Content-Type: application/json
payment-signature: <signed_x402_payload>

{"prompt": "cyberpunk city at sunset", "aspect_ratio": "16:9"}
```

---

## Response Handling

### Synchronous (`executionMode: "sync"`)
Result is immediate. Extract URL from `result` field (see Result Field Reference).

### Queued (`executionMode: "queue"`)
Poll `job.statusUrl` every 5s until `status` is `COMPLETED` or `FAILED`, then fetch `job.resultUrl`.

| Status | Action |
|--------|--------|
| `QUEUED` / `IN_PROGRESS` | Poll again after 5s delay |
| `COMPLETED` | Fetch result from `job.resultUrl` |
| `FAILED` | Return error to user |

---

## Result Field Reference

| Tool Type | Primary Field | Fallback Fields | Example Payload |
|-----------|---------------|-----------------|-----------------|
| Image | `result.images[0].url` | `result.images[0]` | `{"prompt": "...", "aspect_ratio": "16:9"}` |
| Video | `result.video.url` | `result.video_url` | `{"prompt": "...", "duration": 5}` |
| Audio/TTS | `result.audio.url` | `result.audio_url` | `{"text": "...", "voice": "alloy"}` |
| Music | `result.audio.url` | `result.audio_url` | `{"prompt": "...", "duration": 30}` |
| 3D Model | `result.model_glb.url` | `result.model_mesh.url` | `{"image_url": "https://..."}` |

---

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 402 | Payment required | Parse accepts[], sign payment, retry |
| 402 + "already used" | Signature replay | Generate fresh signature, retry |
| 400 | Invalid request | Check payload against tool schema |
| 401 | Wrong endpoint | Use /api/gateway/* routes only |
| 404 | Tool not found | Check toolId spelling |
| 429 | Rate limited | Wait `Retry-After` seconds |
| 500 | Server error | Retry with exponential backoff |

---

## Security

### Agent MUST
- Display payment amount to user before signing
- Wait for explicit user approval ("yes"/"approve")
- Use host x402 signer (never handle private keys)
- Verify `payTo` matches 402 challenge exactly
- Use identical request body for retry after payment

### Agent MUST NEVER
- Auto-approve any payment
- Skip user confirmation step
- Reuse a payment signature (one-time use only)
- Request or store user private keys
- Modify request body between 402 and paid retry

### Server Protections
- Replay prevention (Redis-backed signature dedup)
- Wallet/amount/network verification via CDP
- Rate limiting: 500 req/15min, 10 payments/5min

---

## ClawBot/OpenClaw Response Schema

All gateway endpoints return normalized responses for ClawBot/OpenClaw compatibility.

### Success Response
```json
{
  "status": "success",
  "generation_id": "req_abc123",
  "confirmation_id": "0x...",
  "data": { /* tool-specific result */ },
  "error": null
}
```

### Error Response
```json
{
  "status": "error",
  "generation_id": "req_abc123",
  "confirmation_id": "",
  "data": {},
  "error": "Error description"
}
```

### x402 Tracking Fields (SkillMD-required)

When x402 payment is used, responses include:

| Field | Type | Description |
|-------|------|-------------|
| `x402_amount` | string | USDC amount in micro-units |
| `x402_status` | string | `verified` \| `settled` \| `settlement_failed` |
| `x402_confirmation_id` | string | Transaction hash or signature hash |
| `x402_timestamp` | string | ISO-8601 timestamp |
| `x402_recipient` | string | Payment recipient address |

Plus nested `x402` object:
```json
{
  "x402": {
    "settled": true,
    "transactionHash": "0x...",
    "amount": "32500",
    "recipient": "0xa0aE05e2766A069923B2a51011F270aCadFf023a",
    "confirmationId": "0x...",
    "status": "settled"
  }
}
```

---

## Quick Reference

```
Base URL:    https://seisoai.com
Tools:       GET /api/gateway/tools
Price:       GET /api/gateway/price/{toolId}
Invoke:      POST /api/gateway/invoke/{toolId}
Job Status:  GET /api/gateway/jobs/{id}?model={m}
Job Result:  GET /api/gateway/jobs/{id}/result?model={m}
Payment:     USDC on Base to 0xa0aE05e2766A069923B2a51011F270aCadFf023a
```
