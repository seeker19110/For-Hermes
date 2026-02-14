---
name: "WhatsApp All-in-One — AI Messaging, Leads, Bulk Send & A2A"
version: "2.3.2"
description: "MoltFlow — complete WhatsApp automation platform with built-in BizDev growth agent. Proactive account scanning, chat mining for hidden leads, retention plays, and automated setup. Plus: bulk messaging, scheduled messages, custom groups, lead detection & CRM, AI replies with style cloning, knowledge base (RAG), voice transcription, group monitoring, labels, anti-spam, content safeguards, review collection, webhooks, GDPR compliance, and agent-to-agent protocol. 90+ API endpoints."
source: "MoltFlow Team"
risk: safe
homepage: "https://molt.waiflow.app"
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
metadata: {"openclaw":{"emoji":"📱","homepage":"https://molt.waiflow.app","requires":{"env":["MOLTFLOW_API_KEY"]},"primaryEnv":"MOLTFLOW_API_KEY"}}
---

# WhatsApp Automation & A2A

Complete WhatsApp automation platform — 90+ API endpoints, proactive growth agent, built-in CRM.

> **BizDev Growth Agent**: Install this skill and ask Claude to scan your account. It finds hidden leads in your chats, spots unmonitored high-value groups, and suggests re-engagement plays — all from your existing WhatsApp data.

> **Save up to 17% with yearly billing** — Free tier available, no credit card required. [Sign up](https://molt.waiflow.app/checkout?plan=free)

---

## Just Ask Claude

Install the skill, set your API key, and start talking:

**"Scan my WhatsApp account for growth opportunities"**
BizDev agent runs 11 API calls, finds unanswered contacts,
unmonitored high-value groups, and leads going cold.

**"Find cold leads I haven't followed up with"**
Scans your chats, identifies contacts with no reply in 7+ days,
suggests re-engagement messages in your writing style.

**"Set up keyword monitoring for my real estate groups"**
Lists your WhatsApp groups, adds monitoring for "looking for",
"need help", "budget" — auto-detects leads into your pipeline.

**"Collect customer feedback from my support chats"**
Configures review collectors with sentiment analysis,
auto-approves positive reviews, exports testimonials as HTML.

**"Send a promo to my VIP client list every Monday at 9 AM"**
Creates a scheduled message with timezone-aware cron,
ban-safe throttling, and delivery tracking.

**"Reply to my WhatsApp messages while I'm in meetings"**
Trains a style profile from your messages, generates AI replies
that match your tone. Preview before sending.

---

## Code Samples

### Send a message

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid",
    "chat_id": "1234567890@c.us",
    "message": "Hello!"
  }' \
  https://apiv2.waiflow.app/api/v2/messages/send
```

### Bulk broadcast to a contact group

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_group_id": "group-uuid",
    "session_id": "uuid",
    "message": "Weekly update..."
  }' \
  https://apiv2.waiflow.app/api/v2/bulk-send
```

### Schedule a recurring message

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monday update",
    "session_id": "uuid",
    "chat_id": "123@c.us",
    "message": "...",
    "recurrence": "weekly",
    "scheduled_time": "2026-02-17T09:00:00",
    "timezone": "America/New_York"
  }' \
  https://apiv2.waiflow.app/api/v2/scheduled-messages
```

### Monitor a group for keywords

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid",
    "wa_group_id": "120363012345@g.us",
    "monitor_mode": "keywords",
    "monitor_keywords": ["looking for", "need help", "budget"]
  }' \
  https://apiv2.waiflow.app/api/v2/groups
```

### List new leads

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/leads?status=new&limit=50"
```

### Generate an AI reply with style + knowledge base

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "5511999999999@c.us",
    "context": "Customer asks: What is your return policy?",
    "use_rag": true,
    "apply_style": true
  }' \
  https://apiv2.waiflow.app/api/v2/ai/generate-reply
```

### Create a review collector

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Feedback",
    "session_id": "uuid",
    "source_type": "all",
    "min_sentiment_score": 0.7,
    "include_keywords": ["thank", "recommend", "love"],
    "languages": ["en"]
  }' \
  https://apiv2.waiflow.app/api/v2/reviews/collectors
```

### Discover A2A agents

```bash
curl https://apiv2.waiflow.app/.well-known/agent.json
```

### Create a scoped API key

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "outreach-bot",
    "scopes": [
      "messages:send",
      "custom-groups:manage",
      "bulk-send:manage"
    ],
    "expires_in_days": 90
  }' \
  https://apiv2.waiflow.app/api/v2/api-keys
```

### Subscribe to webhook events

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": [
      "message.received",
      "lead.detected",
      "session.connected"
    ]
  }' \
  https://apiv2.waiflow.app/api/v2/webhooks
```

Full API reference with all endpoints: see each module's SKILL.md below.

---

## Use Cases

**Solo Founder / Small Biz**
- "Find leads I'm missing" — BizDev agent scans your chats, finds unanswered contacts
- "Reply like me when I'm busy" — Style profile trained on your messages, AI handles routine queries
- "Send weekly updates to my VIP list" — Scheduled message every Monday 9 AM to your custom group

**Agency / Multi-Client**
- Monitor 50+ industry groups across 10 WhatsApp sessions simultaneously
- Bulk message 200 contacts with ban-safe delays, track delivery in real time
- Export leads as CSV for your CRM, or push to n8n/Zapier workflows

**Developer / AI Agent Builder**
- 90+ REST endpoints, scoped API keys, webhook events for every action
- A2A protocol: agents discover and message each other (E2E encrypted)
- Python scripts for every workflow: quickstart, outreach, leads, GDPR, admin

---

## Platform Features

**Messaging**: text, media, polls, stickers, GIFs, voice notes, locations, vCards. Reply, react, edit, unsend. Typing simulation.

**Bulk Messaging**: Ban-safe broadcast to custom groups. Random 30s-2min delays. Real-time SSE progress. Pause/resume/cancel.

**Scheduled Messages**: One-time, daily, weekly, monthly, cron. Timezone-aware. Execution history.

**Custom Groups**: Contact lists from WhatsApp groups or manual add. CSV/JSON export.

**Lead Detection & CRM**: Auto-detect purchase intent. Pipeline tracking (new > contacted > qualified > converted). Bulk ops. Export.

**Group Monitoring**: 50+ groups. Keyword/mention detection. AI auto-respond. Per-group prompts. Skip admins & existing contacts.

**Labels**: Create, sync to WhatsApp Business, import. Color-coded contact organization.

**AI Replies**: GPT-4/Claude powered. Context-aware with RAG knowledge base. Preview before sending.

**Style Cloning**: Train from your message history. AI replies match your tone, vocabulary, patterns. Per-contact profiles.

**Knowledge Base (RAG)**: Upload PDF/TXT. Semantic search with embeddings. AI uses your docs for grounded answers.

**Voice Transcription**: Whisper-powered. Async task queue with status tracking.

**Review Collection**: Sentiment analysis (14+ languages). Auto-approve positive. Export JSON/HTML.

**Anti-Spam Engine**: Rate limits, duplicate blocking, pattern filters. Human-like typing simulation. Burst rate limiting.

**Content Safeguards**: Block API keys, credit cards, SSNs, PII, prompt injection. Custom regex rules.

**Webhooks**: 10+ event types. HMAC-SHA256 signed. Delivery history. Test payloads.

**A2A Protocol**: JSON-RPC 2.0 agent-to-agent communication. X25519-AES256GCM encryption. Agent discovery + trust levels.

**GDPR Compliance**: Auto-expiring messages (90-day). Data minimization (500-char preview). Contact erasure. DPA available. Named sub-processors.

**Billing**: Stripe-powered. Free/Starter/Pro/Business plans. Yearly saves up to 17%.

---

## How MoltFlow Compares

| Category | Molt | wa-ultimate | wacli | wa-auto |
|----------------------|:----:|:----------:|:-----:|:------:|
| Messaging | 18 | 14 | 3 | 1 |
| Groups & Monitoring | 8 | 4 | 0 | 0 |
| Outreach & Scheduling| 7 | 0 | 0 | 0 |
| CRM & Leads | 7 | 0 | 0 | 0 |
| AI & Intelligence | 7 | 0 | 0 | 0 |
| Reviews & Analytics | 8 | 0 | 0 | 0 |
| Compliance & Security| 10 | 0 | 0 | 0 |
| Platform & Infra | 8 | 0 | 0 | 0 |
| **Total** | **80+** | **~15** | **~3** | **~1** |

---

## Privacy & Data Flow

This skill is **read-only by default** — it calls the MoltFlow HTTPS API to retrieve and display data. No data is sent to third parties beyond `apiv2.waiflow.app`.

**Chat metadata** — MoltFlow server only.
Queried via API, displayed locally, never copied elsewhere.

**Message content** — MoltFlow server only.
500-char truncated previews; full messages are not stored.

**BizDev scan results** — Local `.moltflow.json`.
Aggregate counts and settings only (no PII, no message content).

**Style profiles** — MoltFlow server only.
Statistical patterns only — raw text never stored or transmitted.

**API key** — Local environment variable.
Never logged, never sent to any service other than `apiv2.waiflow.app`.

**Chat history access** is gated by tenant opt-in (default: disabled). Enable at Settings > Account > Data Access before using chat-related features.

**Local file**: The BizDev agent writes a `.moltflow.json` config file in your project root. It stores only: version, preferences, aggregate scan counts. No PII, phone numbers, or message content.

**Credentials**: Use scoped API keys with minimum privileges. See `moltflow-admin` for scope configuration.

---

## Pricing

> **Yearly plans save up to 17%** — pay once, use for 12 months.

| Plan | Monthly | Yearly | Msgs/mo | Sessions | Groups | Rate |
|----------|---------|---------|---------|----------|--------|--------|
| Free | $0 | — | 50 | 1 | 2 | 10/min |
| Starter | $9.90 | $99/yr | 500 | 1 | 5 | 20/min |
| Pro | $29.90 | $299/yr | 1,500 | 5 | 20 | 40/min |
| Business | $69.90 | $699/yr | 3,000 | 15 | 100 | 60/min |

[Sign up for free](https://molt.waiflow.app/checkout?plan=free)

---

## Setup

> **Free tier available** — 1 session, 50 messages/month, no credit card required.

**Env vars:**
- `MOLTFLOW_API_KEY` (required) — API key from [your dashboard](https://molt.waiflow.app)
- `MOLTFLOW_API_URL` (optional) — defaults to `https://apiv2.waiflow.app`

**Authentication:** `X-API-Key: $MOLTFLOW_API_KEY` header or `Authorization: Bearer $TOKEN` (JWT from login).

**Base URL:** `https://apiv2.waiflow.app/api/v2`

---

## Modules

Each module has its own SKILL.md with full endpoint tables and curl examples.

| Module | What it does |
|--------|-------------|
| **moltflow** (Core) | Sessions, messaging, groups, labels, webhooks |
| **moltflow-outreach** | Bulk send, scheduled messages, custom groups |
| **moltflow-ai** | Style cloning, RAG knowledge base, voice transcription, AI replies |
| **moltflow-leads** | Lead detection, CRM pipeline, bulk ops, export |
| **moltflow-a2a** | Agent-to-agent protocol, encrypted messaging |
| **moltflow-reviews** | Review collection, sentiment analysis, testimonial export |
| **moltflow-admin** | Auth, API keys, billing, usage, GDPR compliance |
| **moltflow-onboarding** | BizDev growth agent, account scanning, opportunity analysis |

---

## Guides & Blog

Step-by-step tutorials for common workflows:

- [Getting Started with WhatsApp Automation](https://molt.waiflow.app/blog/whatsapp-automation-getting-started)
- [MoltFlow API Complete Guide](https://molt.waiflow.app/blog/moltflow-api-complete-guide)
- [MoltFlow + n8n WhatsApp Automation](https://molt.waiflow.app/blog/moltflow-n8n-whatsapp-automation)
- [n8n + WhatsApp + Google Sheets](https://molt.waiflow.app/blog/n8n-whatsapp-google-sheets)
- [n8n WhatsApp Group Auto-Reply](https://molt.waiflow.app/blog/n8n-whatsapp-group-auto-reply)
- [n8n WhatsApp Lead Pipeline](https://molt.waiflow.app/blog/n8n-whatsapp-lead-pipeline)
- [n8n Multi-Model AI Orchestration](https://molt.waiflow.app/blog/n8n-multi-model-ai-orchestration)
- [AI Auto-Replies for WhatsApp Setup](https://molt.waiflow.app/blog/ai-auto-replies-whatsapp-setup)
- [WhatsApp Group Lead Generation Guide](https://molt.waiflow.app/blog/whatsapp-group-lead-generation-guide)
- [OpenClaw WhatsApp Customer Support](https://molt.waiflow.app/blog/openclaw-whatsapp-customer-support)
- [Knowledge Base Deep Dive (RAG)](https://molt.waiflow.app/blog/rag-knowledge-base-deep-dive)
- [Learn Mode Style Training](https://molt.waiflow.app/blog/learn-mode-style-training-whatsapp)
- [Lead Scoring Automation](https://molt.waiflow.app/blog/whatsapp-lead-scoring-automation)
- [Customer Feedback Collection](https://molt.waiflow.app/blog/whatsapp-customer-feedback-collection)
- [A2A Protocol: Agent-to-Agent Communication](https://molt.waiflow.app/blog/a2a-protocol-agent-communication)
- [Scaling WhatsApp Automation ROI](https://molt.waiflow.app/blog/scaling-whatsapp-automation-roi)

Full blog: https://molt.waiflow.app/blog

---

## Example Scripts

The `scripts/` directory contains standalone Python examples (requires `requests`). Example scripts for reference only — not auto-executed by the skill. Review before running with production credentials.

| Script | Purpose |
|--------|---------|
| `quickstart.py` | Create session, send first message |
| `send_message.py` | Send text messages to contacts |
| `outreach.py` | Bulk send, scheduled messages, custom groups |
| `leads.py` | Lead pipeline, bulk ops, CSV/JSON export |
| `ai_config.py` | Train style profiles, generate AI replies |
| `reviews.py` | Create collectors, export testimonials |
| `group_monitor.py` | WhatsApp group monitoring & lead detection |
| `a2a_client.py` | Discover agents, send A2A messages |
| `admin.py` | Login, create API keys, check billing |
| `gdpr.py` | Contact erasure, data export, account deletion |

Run any script: `MOLTFLOW_API_KEY=your-key python scripts/quickstart.py`

---

## Notes

- All messages include anti-spam compliance (typing indicators, random delays)
- Sessions require QR code pairing on first connect
- Use E.164 phone format without `+` where required
- AI features and A2A protocol require Pro plan or above
- API rate limits by plan: Free 10/min, Starter 20/min, Pro 40/min, Business 60/min

---

## Changelog

**v2.3.2** (2026-02-13) — See [CHANGELOG.md](CHANGELOG.md) for full history.

<!-- FILEMAP:BEGIN -->
```text
[moltflow file map]|root: .
|.:{SKILL.md,CHANGELOG.md,package.json}
|scripts:{quickstart.py,a2a_client.py,send_message.py,admin.py,ai_config.py,reviews.py,outreach.py,leads.py,gdpr.py,group_monitor.py}
|moltflow:{SKILL.md}
|moltflow-ai:{SKILL.md}
|moltflow-a2a:{SKILL.md}
|moltflow-reviews:{SKILL.md}
|moltflow-outreach:{SKILL.md}
|moltflow-leads:{SKILL.md}
|moltflow-admin:{SKILL.md}
|moltflow-onboarding:{SKILL.md}
```
<!-- FILEMAP:END -->
