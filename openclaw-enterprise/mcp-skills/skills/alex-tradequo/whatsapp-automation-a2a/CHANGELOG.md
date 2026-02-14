# Changelog

All notable changes to the **MoltFlow Skills** package are documented here.

---

## v2.3.2 (2026-02-13)

### Changed
- Improved root SKILL.md formatting and content clarity
- Pretty-printed JSON in all curl code samples
- Simplified Privacy & Data Flow section (prose instead of table)
- Condensed comparison table column headers

---

## v2.3.1 (2026-02-13)

### Fixed
- Restored `metadata.openclaw` in frontmatter — ClawHub registry reads env vars from this field, not top-level `requiredEnv`
- Replaced `$JWT` with `$MOLTFLOW_API_KEY` in scoped API key creation example — JWT is not a declared env var

---

## v2.3.0 (2026-02-13)

### Added
- Required API key scopes documentation for all 10 Python scripts
- Required API key scopes sections in all 8 sub-skill SKILL.md files
- Chat history consent warnings for scripts and sub-skills that read message history
- Scoped token support reflecting Phase 51 (Scoped API Keys)
- Chat history gate warnings reflecting Phase 52 (Chat History Gate)

---

## [2.2.1] - 2026-02-13 — "Security Transparency"

> Explicit privacy & data flow documentation to address ClawHub security scan findings.

### Added

- **Privacy & Data Flow** section in root SKILL.md — documents what data stays local vs server, what BizDev agent reads, and `.moltflow.json` contents (no PII)
- **API Key Security & Scoping** section — least-privilege recommendations, rotation guidance, test tenant advice
- `disable-model-invocation: true` added to `moltflow-onboarding` sub-skill frontmatter

### Fixed

- ClawHub security scan "Instruction Scope" info finding — explicit data minimization statements
- ClawHub security scan "Credentials" info finding — API key scoping documentation
- ClawHub security scan "Persistence & Privilege" info finding — `.moltflow.json` contents clarified (aggregate counts only, no PII)

---

## [2.2.0] - 2026-02-13 — "BizDev Growth Agent"

> Your AI business development agent — scans your account, mines chats for hidden leads, and suggests data-driven growth plays.

### Added

- **BizDev Growth Agent** (`moltflow-onboarding`) — proactive AI agent that runs a deep account scan, mines chat history for unanswered contacts and VIP conversations, detects unmonitored high-value groups, suggests re-engagement plays, revenue optimization, and testimonial harvesting. Persists config to `.moltflow.json` for repeat scans with delta comparison.
- Landing page: BizDev feature block with terminal demo + FAQ entry
- Help page: Section 21 — BizDev Growth Agent with 4 feature cards
- Root SKILL.md: BizDev row in features table, growth use cases, updated filemap

### Changed

- All 6 sub-skills bumped to v2.1.0
- `package.json`: added `moltflow-onboarding/` to files, `onboarding` to keywords
- Root SKILL.md description updated to lead with BizDev agent
- Filemap updated with `moltflow-onboarding` and missing scripts (`gdpr.py`, `group_monitor.py`)

---

## [2.1.0] - 2026-02-12 — "Import & Delete"

> Import contacts from WhatsApp groups, delete your account with full cascade, and GDPR scripts for everything.

### Added

- **WhatsApp Group Import** — `GET /custom-groups/wa-groups` lists all WA groups across sessions; `POST /custom-groups/from-wa-groups` creates a custom group by resolving and deduplicating participants from selected WA groups
- **Account Deletion** — `DELETE /users/me` with password confirmation cascades through 32+ tables (GDPR Article 17)
- `outreach.py` — added `list_wa_groups()` and `create_group_from_wa_groups()` functions
- `gdpr.py` — added `delete_account(password)` function
- Scripts table — added `gdpr.py` and `group_monitor.py` to main SKILL.md documentation
- moltflow-outreach sub-skill — documented WA group import endpoints and examples

### Changed

- Custom Groups endpoint table expanded from 10 to 12 endpoints (both main SKILL.md and moltflow-outreach)
- Version bumped to 2.1.0 across package.json, main SKILL.md, and moltflow-outreach

---

## [2.0.0] - 2026-02-12 — "The Full Platform"

> Every feature, every endpoint, every workflow — v2 is the complete MoltFlow experience.

### Highlights

- **Scheduled Messages** — One-time, daily/weekly/monthly, or custom cron expressions. Timezone-aware. Pause, resume, cancel. Full execution history tracking.
- **Bulk Messaging** — Broadcast to custom groups with ban-safe throttling (random 30s–2min delays). Real-time SSE progress. Pause/resume/cancel mid-flight.
- **Custom Groups** — Build targeted contact lists from WhatsApp conversations. Import members, export CSV/JSON. Feed into Bulk Send or Scheduled Messages.
- **Lead Management** — Auto-detected leads with full pipeline tracking (new → contacted → qualified → converted). Bulk status updates, bulk add-to-group, CSV/JSON export, reciprocity checks.
- **Knowledge Base (RAG)** — Upload PDF/TXT documents, semantic search with embeddings. AI uses your docs to answer customer questions accurately.
- **Voice Transcription** — Whisper-powered voice message transcription with async task queue and status tracking.
- **Comprehensive Feature Matrix** — All 18 platform capabilities listed upfront with full descriptions.
- **90+ API Endpoints** — 6 new API sections (14–19) covering everything added since v1.6.
- **Yearly Billing** — Save up to 17% with annual plans. Highlighted throughout.

### Added

- Section 14: Scheduled Messages API (9 endpoints) — create, list, pause/resume/cancel, execution history
- Section 15: Bulk Send API (7 endpoints) — create jobs, SSE progress, pause/resume/cancel
- Section 16: Custom Groups API (10 endpoints) — create, manage members, CSV/JSON export
- Section 17: Leads API (8 endpoints) — list/filter, status update, bulk ops, CSV/JSON export
- Section 18: Knowledge Base / RAG API (4 endpoints) — ingest, search, list, delete
- Section 19: Voice Transcription API (3 endpoints) — transcribe, status, get transcript
- Comparison table: "Outreach & Scheduling" section (7 new features)
- Comparison table: Bulk lead operations and Lead export rows
- Use case categories: "Bulk messaging & scheduling" and "AI & knowledge"
- Feature matrix table at top of skill with all 18 capability categories
- Sub-skill: `moltflow-outreach` — Bulk Send, Scheduled Messages, Custom Groups (26 endpoints)
- Sub-skill: `moltflow-leads` — Lead Detection & CRM Pipeline (8 endpoints)
- Sub-skill: `moltflow-admin` — re-included in package (GDPR contact erasure, tenant settings, platform admin)
- GDPR contact erasure endpoint (`POST /gdpr/contact-erasure`) documented in moltflow-admin
- Tenant settings endpoints (`GET/PATCH /tenant/settings`) documented in moltflow-admin
- Session settings endpoint (`PATCH /sessions/{id}/settings`) documented in moltflow core
- New scripts: `outreach.py` (bulk send, scheduled messages, custom groups) and `leads.py` (lead pipeline)

### Fixed

- `send_message.py` — wrong endpoint `/messages` (now `/messages/send`) and wrong field `content` (now `message`)
- `ai_config.py` — used non-existent endpoints; rewritten to use actual RAG, style, and reply generation APIs
- `outreach.py` — field names corrected: `custom_group_id` (not `group_id`), `message_content` (not `message`), `schedule_type` (not `recurrence_type`), member format as objects (not strings)
- `leads.py` — field names corrected: `source_group_id` (not `group_id`), `custom_group_id` in bulk add, PATCH path for status update, separate CSV/JSON export functions
- `admin.py` — removed phantom `description` parameter from `create_api_key`
- Main SKILL.md: billing portal method GET→POST, phantom `/webhooks/{id}/deliveries` endpoint removed, all field names in Sections 14-17 corrected
- `moltflow/SKILL.md`: monitor modes corrected (added `mentions`, `first_message`; removed `none`), rate limits table corrected to match actual plan tiers
- `moltflow-ai/SKILL.md`: Enterprise→Business in plan table
- `moltflow-reviews/SKILL.md`: export format `csv`→`html` (API supports `json|html`)
- `moltflow-leads/SKILL.md`: removed invalid `spam` status, fixed all field names and paths
- `moltflow-outreach/SKILL.md`: corrected all field names, schedule types, DELETE path, member format

### Changed

- Version bumped to 2.0.0
- Description expanded to list all major features
- "When to use" section expanded from 13 to 19 items
- Total feature count updated: 80+ (was 63+)
- Business features count updated: 55+ (was 45+)

---

## [1.6.0] - 2026-02-11 — "Anti-Spam Shield & Yearly Savings"

> Protect every message with intelligent anti-spam safeguards, plus save big with our new yearly plan.

### Highlights

- **Anti-Spam Protection** — Every outbound message now passes through reciprocity checks, burst rate limiting, and health monitoring. Contacts must message you first before you can reach out, keeping your WhatsApp number safe and your reputation spotless.
- **Yearly Billing — Over 70% Off** — Following a brief service outage, we're making it right. Lock in yearly pricing at **$239.90/year** — that's over 70% off monthly rates. No catch, no fine print.
- **Expanded API Docs** — Full session lifecycle, webhook configuration, and auth flow documentation added to the main skill.
- **4 Focused Sub-Skills** — Break down the platform into bite-sized pieces: `moltflow` (core), `moltflow-ai` (auto-replies & RAG), `moltflow-a2a` (agent protocol), and `moltflow-reviews` (feedback collection).

### Added

- Anti-spam `MessageProcessor` wired into all 4 REST send endpoints and A2A handler
- Inbound message reciprocity tracking via webhook handler
- Sub-skills published as part of the npm package (`moltflow`, `moltflow-ai`, `moltflow-a2a`, `moltflow-reviews`)
- Interactive architecture diagram in Help Center (marketing + technical views)
- Yearly billing option with Stripe checkout integration

### Fixed

- ClawHub security scan findings (domain mismatch, broken import)
- `disableModelInvocation` set consistently across all sub-skills

### Security

- Removed admin sub-skill from published package (internal use only)
- All sub-skills enforce `disableModelInvocation: true`

---

## [1.5.0] - 2026-02-07 — "Simplified Plans & Billing"

> Streamlined pricing, richer billing APIs, and a full security audit.

### Highlights

- **Simplified Plan Structure** — Cleaner plan tiers with transparent limits. No more guessing what's included.
- **Richer Billing API** — Checkout sessions, billing portal, subscription status, and usage tracking all in one place.
- **Security Hardened** — Full audit: removed `.env` from git, hardened SQL queries, sanitized error messages, locked down prompt injection vectors.

### Added

- Billing endpoints: checkout, portal, cancel, plans list, signup-checkout
- Usage tracking: current month, history, daily breakdown
- Accessibility audit pass on all skill documentation

### Fixed

- Rate limits updated and consistent across all docs and help page
- Pricing grid centered and polished with real use cases

---

## [1.4.0] - 2026-02-06 — "Anti-Spam Rules & Safeguards"

> Complete anti-spam and content safety layer for WhatsApp automation.

### Highlights

- **Anti-Spam Rules** — Rate limits, duplicate message blocking, and pattern-based filters to keep conversations clean.
- **Content Safeguards** — Block secrets, PII, and prompt injection attempts before they leave your outbox.
- **Lead Intelligence** — Auto-detect purchase intent in group conversations, label contacts by sentiment, and route leads to your sales team.

### Added

- Anti-spam rule configuration endpoints
- Content safeguard policies (secrets, PII, prompt injection)
- Auto-feedback collection with 14+ language sentiment analysis
- Intention detection and lead management
- Testimonial export (JSON/HTML)

### Changed

- SKILL.md restructured with anti-spam and safeguards sections
- API URLs corrected to `apiv2.waiflow.app`
- Security scan triggers removed for ClawHub Benign rating

---

## [1.0.0] - 2026-02-06 — "Launch"

> MoltFlow hits ClawHub. One skill to automate WhatsApp at scale.

### Highlights

- **All-in-One WhatsApp API** — Sessions, messaging, groups, labels, webhooks, AI replies, reviews, and A2A — unified under a single skill.
- **Agent-to-Agent Protocol** — JSON-RPC 2.0 with X25519-AES256GCM encryption. Your agents can discover, message, and collaborate with other agents securely.
- **AI That Learns Your Voice** — Train style profiles from your message history. Auto-replies sound like you, not a bot.

### Added

- Core WhatsApp automation: sessions, contacts, messages, groups, labels
- AI features: auto-replies, voice transcription, RAG knowledge base, style profiles
- A2A protocol: agent discovery, encrypted messaging, group management, content policy
- Review collection: sentiment scoring, testimonial extraction, approval workflows
- 6 ready-to-run Python scripts: quickstart, send message, AI config, A2A client, reviews, admin
- Full API reference with curl examples

---

*Built with care by the [MoltFlow](https://waiflow.app) team.*
