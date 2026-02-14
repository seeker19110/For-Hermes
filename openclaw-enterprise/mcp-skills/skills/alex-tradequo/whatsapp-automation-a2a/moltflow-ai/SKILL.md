---
name: moltflow-ai
description: "AI-powered WhatsApp features: auto-replies, voice transcription, RAG knowledge base, and style profiles. Use when: ai reply, transcribe voice, knowledge base, upload document, train style, learn mode."
source: "MoltFlow Team"
version: "2.1.0"
risk: safe
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
---

> **MoltFlow** -- WhatsApp Business automation for teams. Connect, monitor, and automate WhatsApp at scale.
> [Save up to 17% with yearly billing](https://molt.waiflow.app/checkout?plan=free) -- Free tier available, no credit card required.

# MoltFlow AI Features

AI-powered capabilities for WhatsApp automation: voice transcription, RAG knowledge base, style profile learning, and intelligent reply generation.

## When to Use

- "Transcribe a voice message" or "convert audio to text"
- "Upload a document to knowledge base" or "ingest PDF"
- "Search knowledge base" or "find in documents"
- "Train style profile" or "learn my writing style"
- "Generate an AI reply" or "auto-reply to customer"
- "Preview AI response" or "test reply generation"
- "List knowledge sources" or "delete document"

## Prerequisites

1. **MOLTFLOW_API_KEY** -- Generate from the [MoltFlow Dashboard](https://molt.waiflow.app) under Settings > API Keys
2. **Pro plan or higher** ($29.90/mo) -- AI features are not available on the Starter plan
3. Base URL: `https://apiv2.waiflow.app/api/v2`
4. All AI endpoints are under the `/ai` prefix

## Required API Key Scopes

| Scope | Access |
|-------|--------|
| `ai` | `read/manage` |

> **Chat History Access**: Reading chat history requires explicit tenant opt-in.
> Enable at **Settings > Account > Data Access** before using chat-related features.
> Sending messages does NOT require this consent — only reading history.

## Authentication

Every request must include one of:

```
Authorization: Bearer <jwt_token>
```

or

```
X-API-Key: <your_api_key>
```

---

## Voice Transcription

Transcribe WhatsApp voice messages using Whisper AI. Transcription runs asynchronously via a Celery worker.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/voice/transcribe` | Queue a voice message for transcription |
| GET | `/ai/voice/status/{task_id}` | Check transcription task status |
| GET | `/ai/messages/{message_id}/transcript` | Get the transcript for a message |

### Queue Transcription

**POST** `/ai/voice/transcribe`

```json
{
  "message_id": "msg-uuid-..."
}
```

**Response** `200 OK`:

```json
{
  "task_id": "celery-task-id-...",
  "message_id": "msg-uuid-...",
  "status": "queued"
}
```

### Check Status

**GET** `/ai/voice/status/{task_id}`

```json
{
  "task_id": "celery-task-id-...",
  "status": "completed",
  "result": {
    "transcript": "Hello, I wanted to ask about...",
    "language": "en",
    "confidence": 0.95
  }
}
```

Status values: `queued`, `processing`, `completed`, `failed`

### Get Transcript

**GET** `/ai/messages/{message_id}/transcript`

```json
{
  "message_id": "msg-uuid-...",
  "transcript": "Hello, I wanted to ask about...",
  "language": "en",
  "confidence": 0.95,
  "transcribed_at": "2026-02-11T10:05:00Z"
}
```

---

## RAG Knowledge Base

Upload documents to build a searchable knowledge base. The AI uses this context when generating replies, providing accurate answers grounded in your business data.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/knowledge/ingest` | Upload and index a document |
| POST | `/ai/knowledge/search` | Semantic search across documents |
| GET | `/ai/knowledge/sources` | List all indexed documents |
| DELETE | `/ai/knowledge/{source_id}` | Delete a document |

### Upload Document

**POST** `/ai/knowledge/ingest` (multipart/form-data)

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | PDF or TXT file (max 100MB) |

**Response** `200 OK`:

```json
{
  "id": "src-uuid-...",
  "name": "product-catalog.pdf",
  "source_type": "application/pdf",
  "chunk_count": 47,
  "status": "indexed",
  "task_id": "celery-task-id-..."
}
```

Supported file types: `application/pdf`, `text/plain` (`.pdf`, `.txt`)

### Search Knowledge Base

**POST** `/ai/knowledge/search`

```json
{
  "query": "What is the return policy?",
  "top_k": 5
}
```

**Response** `200 OK`:

```json
{
  "query": "What is the return policy?",
  "results": [
    {
      "source_id": "src-uuid-...",
      "content_type": "application/pdf",
      "content_preview": "Our return policy allows returns within 30 days...",
      "metadata": {"page": 12, "chunk": 3},
      "similarity": 0.92
    }
  ],
  "count": 1
}
```

Optional filters:

```json
{
  "query": "shipping costs",
  "filters": {"source_type": "application/pdf"},
  "top_k": 10
}
```

### List Documents

**GET** `/ai/knowledge/sources`

```json
[
  {
    "id": "src-uuid-...",
    "name": "product-catalog.pdf",
    "source_type": "application/pdf",
    "chunk_count": 47,
    "status": "indexed",
    "created_at": "2026-02-11T09:00:00Z",
    "indexed_at": "2026-02-11T09:02:00Z"
  }
]
```

Document status values: `processing`, `indexed`, `failed`

### Delete Document

**DELETE** `/ai/knowledge/{source_id}` -- Returns `204 No Content`

---

## Style Profiles (Learn Mode)

Train the AI to match your writing style by analyzing your message history from specific chats. Style profiles can be scoped to individual conversations (per-chat) or trained across all messages (general profile). The AI auto-selects the best matching profile when generating replies.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/style/train` | Start training a style profile |
| GET | `/ai/style/status/{task_id}` | Check training status |
| GET | `/ai/style/profile` | Get a style profile |
| GET | `/ai/style/profiles` | List all style profiles |
| DELETE | `/ai/style/profile/{profile_id}` | Delete a style profile |

### Train Style Profile

**POST** `/ai/style/train`

```json
{
  "session_id": "session-uuid-...",
  "wa_chat_id": "5511999999999@c.us",
  "name": "Sales"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contact_id` | string | No | Legacy — use `wa_chat_id` instead |
| `session_id` | UUID | No | Session to scope training to |
| `wa_chat_id` | string | No | Chat to scope training to (WhatsApp JID). Omit for general profile |
| `name` | string | No | Profile name (e.g., "Sales", "Support", "Family") |

**Note:** Omit both `session_id` and `wa_chat_id` to train a general profile from all messages.

**Response** `200 OK`:

```json
{
  "task_id": "celery-task-id-...",
  "tenant_id": "tenant-uuid-...",
  "contact_id": "5511999999999@c.us",
  "status": "queued"
}
```

Training runs asynchronously. Check progress with the status endpoint.

### Get Style Profile

**GET** `/ai/style/profile?contact_id=5511999999999@c.us`

```json
{
  "id": "profile-uuid-...",
  "tenant_id": "tenant-uuid-...",
  "contact_id": "5511999999999@c.us",
  "name": "Sales",
  "session_id": "session-uuid-...",
  "wa_chat_id": "5511999999999@c.us",
  "features": {
    "avg_sentence_length": 12.5,
    "formality_score": 0.7,
    "emoji_frequency": 0.15,
    "vocabulary_richness": 0.82
  },
  "sample_count": 150,
  "last_trained_at": "2026-02-11T09:30:00Z"
}
```

### List All Profiles

**GET** `/ai/style/profiles`

```json
[
  {
    "id": "profile-uuid-1",
    "tenant_id": "tenant-uuid-...",
    "name": "Sales",
    "session_id": "session-uuid-...",
    "wa_chat_id": "5511999999999@c.us",
    "features": { "formality_score": 0.7 },
    "sample_count": 150,
    "last_trained_at": "2026-02-11T09:30:00Z"
  },
  {
    "id": "profile-uuid-2",
    "tenant_id": "tenant-uuid-...",
    "name": "General",
    "session_id": null,
    "wa_chat_id": null,
    "features": { "formality_score": 0.5 },
    "sample_count": 420,
    "last_trained_at": "2026-02-11T10:00:00Z"
  }
]
```

### Delete Profile

**DELETE** `/ai/style/profile/{profile_id}` -- Returns `204 No Content`

---

## AI Reply Generation

Generate intelligent reply suggestions using RAG context and style profiles. The AI considers conversation history, knowledge base content, and your communication style.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/generate-reply` | Generate a reply suggestion |
| GET | `/ai/preview` | Preview a reply without tracking usage |

### Generate Reply

**POST** `/ai/generate-reply`

```json
{
  "contact_id": "5511999999999@c.us",
  "context": "Customer asks: Do you offer international shipping?",
  "use_rag": true,
  "apply_style": true,
  "profile_id": "profile-uuid-...",
  "session_id": "session-uuid-..."
}
```

**Response** `200 OK`:

```json
{
  "reply": "Yes, we ship internationally to over 50 countries! Shipping typically takes 7-14 business days. You can find our full shipping policy on our website.",
  "rag_sources": ["product-catalog.pdf"],
  "style_applied": true,
  "model": "gpt-4o-mini",
  "tokens_used": 245,
  "requires_approval": false
}
```

### Parameters

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `contact_id` | string | required | WhatsApp JID of the contact |
| `context` | string | required | Conversation context or customer question (max 2000 chars) |
| `use_rag` | boolean | `true` | Include knowledge base context in generation |
| `apply_style` | boolean | `true` | Apply trained style profile to response |
| `profile_id` | UUID | `null` | Specific style profile to use (skips auto-selection cascade) |
| `session_id` | UUID | `null` | Session for cascade profile resolution |
| `approved` | boolean | `false` | Set `true` to confirm an approval-required reply |

**Note:** If `profile_id` is omitted and `apply_style` is true, the API auto-selects the best profile using the cascade: exact chat match → session-level → tenant-level general → no style.

### Preview Reply

**GET** `/ai/preview?contact_id=5511999999999@c.us&context=What+are+your+hours&use_rag=true&apply_style=true`

Same response format as `generate-reply`, but does not count toward usage metrics.

### Safety Features

AI reply generation includes built-in safety:

- **Input sanitization** -- Detects and blocks prompt injection attempts
- **Intent verification** -- Flags ambiguous or high-risk intents for confirmation
- **Output filtering** -- Screens generated content for PII, secrets, and policy violations
- **Content policy** -- Tenant-configurable rules (see moltflow-a2a skill)

---

## Examples

### Upload a knowledge base document

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/ai/knowledge/ingest \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -F "file=@product-catalog.pdf"
```

### Generate an AI reply using RAG

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/ai/generate-reply \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "5511999999999@c.us",
    "context": "Customer asks: What is your return policy?",
    "use_rag": true,
    "apply_style": true
  }'
```

### Generate reply with specific profile

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/ai/generate-reply \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "5511999999999@c.us",
    "context": "Customer asks: What is your return policy?",
    "use_rag": true,
    "apply_style": true,
    "profile_id": "profile-uuid-..."
  }'
```

### Train a style profile

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/ai/style/train \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid-...",
    "wa_chat_id": "5511999999999@c.us",
    "name": "Sales"
  }'
```

---

## Plan Requirements

| Feature | Starter | Pro ($29.90/mo) | Business ($69.90/mo) |
|---------|---------|-----------------|------------|
| Voice Transcription | -- | Yes | Yes |
| RAG Knowledge Base | -- | Yes (10 docs) | Yes (unlimited) |
| Style Profiles | -- | Yes (3 profiles) | Yes (unlimited) |
| AI Reply Generation | -- | Yes | Yes |

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid input, unsupported file type) |
| 401 | Unauthorized (missing or invalid auth) |
| 403 | Forbidden (feature requires Pro plan or higher) |
| 404 | Resource not found (message, document, profile) |
| 413 | File too large (exceeds 100MB limit) |
| 429 | Rate limited |

---

## Related Skills

- **moltflow** -- Core API: sessions, messaging, groups, labels, webhooks
- **moltflow-outreach** -- Bulk Send, Scheduled Messages, Custom Groups
- **moltflow-leads** -- Lead detection, pipeline tracking, bulk operations, CSV/JSON export
- **moltflow-a2a** -- Agent-to-Agent protocol, encrypted messaging, content policy
- **moltflow-reviews** -- Review collection and testimonial management
- **moltflow-admin** -- Platform administration, user management, plan configuration
