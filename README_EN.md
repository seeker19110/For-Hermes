# 🌟 Hermes Antigravity OAuth Plugin & Local Bridge

> **Extension plugin for Hermes Agent** that integrates premium AI models from **Google Antigravity OAuth** (Gemini 3.7 Flash, Claude Sonnet/Opus 4.6, GPT-OSS 120B) into Hermes Agent — across CLI, Telegram, Discord, Dashboard, and every other platform.

**Version:** 1.0.0 — Updated: 31/08/2026

---

## 📌 Key Features

### Core
- **🔑 OAuth PKCE Login** — One-click Google sign-in via browser, identical to real IDE flow
- **🔄 Token Auto-Refresh** — Automatically refreshes tokens 120 seconds before expiry
- **👥 Multi-Account Pool** — Rotates multiple accounts with auto-failover on Rate Limit
- **🖥️ Full IDE Simulation** — Complete emulation of Antigravity IDE environment (headers, fingerprint, API endpoint)
- **📡 Bridge Server** — Local server on port 8100, OpenAI-compatible API format
- **🧠 9 Models** — 100% synced with the real Antigravity IDE model catalog

### Dashboard Integration
- **Keys Tab (`/env`):** OAuth connection card showing email, token, and expiry
- **System Tab (`/system`):** Multi-account Credential Pool management
- **Models Tab (`/models`):** One-click model selection in SET MAIN MODEL dialog
- **Chat Sidebar:** Direct model picker in the chat interface

### Reliability
- **🛡️ Upgrade-Proof** — Tokens and plugin stored outside git repo (`~/.hermes/`)
- **🔌 Daemon Auto-Wake** — Bridge automatically starts when gateway needs it
- **🖼️ Vision Support** — Multimodal image input support
- **🌊 SSE Streaming** — Real-time streamed responses

---

## 📂 Directory Structure

```
HERMES-ANTIGRAVITY PLUGIN/
├── README.md              # Documentation (Vietnamese)
├── README_EN.md           # Documentation (English — this file)
├── install.py             # One-click automated installer
├── manage.py              # CLI management tool for Bridge & OAuth
├── plugin/                # Hermes Model Provider Plugin
│   ├── plugin.yaml        # Plugin metadata and model catalog
│   └── __init__.py        # ProviderProfile (auto-wake + vision)
└── bridge/                # Runtime Engine
    ├── auth.py            # OAuth PKCE, Token Storage, Auto-refresh (622 lines)
    ├── client.py          # OpenAI ↔ Gemini Code Assist translator (818 lines)
    ├── server.py          # HTTP Server on port 8100 (288 lines)
    └── __init__.py        # Module exports
```

---

## 📋 Supported Models (Matching Antigravity IDE)

| # | Model ID | Display Name | Tier | Best For |
|:-:|---|---|---|---|
| 1 | **`gemini-3.7-flash`** | Gemini 3.7 Flash High | Fast | Deep reasoning, full tool use (Recommended Main Model) |
| 2 | **`gemini-3.7-flash-medium`** | Gemini 3.7 Flash Medium | Fast | Balanced reasoning (IDE Default) |
| 3 | **`gemini-3.7-flash-low`** | Gemini 3.7 Flash Low | Fast | Lowest latency, ultra-fast responses |
| 4 | **`gemini-3.6-flash`** | Gemini 3.6 Flash Medium | Fast | Stable 3.6 release |
| 5 | **`gemini-3.5-flash`** | Gemini 3.5 Flash Medium | Fast | Lightweight daily driver |
| 6 | **`gemini-3.1-pro`** | Gemini 3.1 Pro Low | — | Architecture analysis & refactoring |
| 7 | **`claude-sonnet-4-6`** | Claude Sonnet 4.6 (Thinking) | — | Extended thinking with Claude |
| 8 | **`claude-opus-4-6`** | Claude Opus 4.6 (Thinking) | — | Peak reasoning with Claude |
| 9 | **`gpt-oss-120b`** | GPT-OSS 120B (Medium) | — | Open-weights 120B model on Google Cloud |

> **Note:** `gemini-3.7-pro` does NOT exist in Antigravity IDE and has been removed.

---

## 🚀 Installation Guide

### Option 1: One-Click Install (Recommended)

```bash
cd "HERMES-ANTIGRAVITY PLUGIN"
python install.py
```

The installer will automatically:
1. Copy the plugin → `~/.hermes/plugins/model-providers/antigravity/`
2. Copy the bridge → `~/.hermes/bridge/antigravity/`
3. Sync with the current workspace if inside a Hermes Agent repo

### Option 2: CLI Management (`manage.py`)

```bash
# Check connection status
python manage.py status

# Login with Google OAuth
python manage.py login

# Start bridge daemon
python manage.py start

# Configure Hermes to use Antigravity
python manage.py setup --model gemini-3.7-flash

# Stop bridge
python manage.py stop
```

### Option 3: Hermes CLI Auth

```bash
hermes auth add antigravity
# → Select "2. OAuth login (authenticate via browser)"
# → Browser opens Google Consent → Sign in → Done
```

---

## 🌐 Dashboard Usage Guide

### Step 1: OAuth Login

1. Open Dashboard: `http://localhost:9119`
2. Go to **Keys & OAuth** tab (`/env`)
3. Find **Google Antigravity (OAuth)** card → Click **[LOGIN]**
4. Browser opens Google Consent → Approve → Dashboard saves token automatically

### Step 2: Select Model

1. Go to **Models** tab (`/models`)
2. Click **SET MAIN MODEL**
3. Select **Google Antigravity (OAuth)**
4. Choose a model (e.g. `gemini-3.7-flash`) → **Switch**

### Step 3: Start Using

Chat directly on Dashboard, CLI, Telegram, Discord, or any other platform.

---

## 👥 Multi-Account & Failover

### Add Accounts via Dashboard (`/system`)

1. Navigate to `http://localhost:9119/system`
2. Scroll to **Credential Pool**
3. Enter: `PROVIDER: antigravity` / `API KEY: <access_token>` / `LABEL: email`
4. Click **ADD KEY**

Hermes will automatically rotate to the next account when hitting Rate Limit 429.

### Add via CLI

```bash
python manage.py login
# Select your second Google account → Token saved automatically
```

### Direct Configuration in `~/.hermes/auth.json`

```json
{
  "credential_pool": {
    "antigravity": [
      {
        "id": "acc_1",
        "auth_type": "oauth",
        "access_token": "ya29.xxx...",
        "refresh_token": "1//04xxx...",
        "label": "user1@gmail.com"
      },
      {
        "id": "acc_2",
        "auth_type": "oauth",
        "access_token": "ya29.yyy...",
        "refresh_token": "1//04yyy...",
        "label": "user2@gmail.com"
      }
    ]
  }
}
```

---

## 🔬 Technical Architecture

### Request Flow

```
User Request (OpenAI format)
    ↓
Hermes Agent (cli / telegram / discord / tui)
    ↓
Antigravity Bridge (localhost:8100)
    ├── Resolve OAuth token (auto-refresh if expiring)
    ├── Translate OpenAI → Gemini Code Assist format
    ├── Build IDE headers (User-Agent, Client-Metadata, X-Goog)
    └── POST → https://daily-cloudcode-pa.googleapis.com/v1internal
                    ↓
            Google Code Assist Backend
                    ↓
            Gemini 3.7 / Claude / GPT-OSS
                    ↓
            Response → Translate back to OpenAI format
                    ↓
            Hermes Agent → User
```

### 7-Layer IDE Simulation

The plugin fully emulates the real Antigravity IDE environment:

| Layer | Detail | Detectable? |
|---|---|---|
| **1. OAuth Client ID** | Uses Google Antigravity's public Client ID | ❌ No |
| **2. HTTP Headers** | `User-Agent: Antigravity/1.0.0`, `X-Goog-Api-Client: gccl/antigravity-ide` | ❌ No |
| **3. Client Metadata** | `ideType: ANTIGRAVITY`, `pluginType: GEMINI` | ❌ No |
| **4. API Endpoint** | `v1internal` (internal API, not public Gemini API) | ❌ No |
| **5. OAuth Scopes** | `cclog`, `experimentsandconfigs` (IDE-specific scopes) | ❌ No |
| **6. PKCE Flow** | Port 51121, SHA-256 code challenge (same as IDE) | ❌ No |
| **7. Request Format** | Gemini Code Assist envelope + thoughtSignature handling | ❌ No |

> **Individual requests are indistinguishable** from the real IDE.
> Risk only lies in **usage volume** if heavily used (24/7 via gateway).

### Special Handling

- **thoughtSignature**: Detects real signatures vs fake `"skip_thought_signature_validator"` → converts invalid tool calls to text format
- **Role Alternation**: Auto-merges consecutive same-role messages (user/user → user)
- **Connection Reset**: Server gracefully handles client disconnection without crashing
- **Model Alias**: Auto-maps invalid model names to the nearest valid model

---

## ☁️ Cloud / VPS Deployment

1. **Prepare Tokens** — Copy `~/.hermes/auth/antigravity_tokens.json` from your local machine to VPS
2. **Install Plugin:**
   ```bash
   python install.py
   ```
3. **Start Services:**
   ```bash
   python ~/.hermes/bridge/antigravity/manage.py start
   hermes gateway run
   ```

---

## ❓ FAQ

#### Q: Will the plugin break when running `git pull` or updating Hermes?
> **A:** Absolutely **NO**. Plugin is stored at `~/.hermes/plugins/`, tokens at `~/.hermes/auth/` — outside the git repo. If you need to re-sync after a fresh install, just run `python install.py`.

#### Q: The bridge keeps crashing?
> **A:** Version 1.0.0 fixed the `ConnectionResetError` crash. The gateway will auto-restart the bridge via `ensure_antigravity_bridge_running()`. No manual restart needed.

#### Q: How do I disconnect my Google account?
> **A:** Dashboard → Keys tab → **[DISCONNECT]** on the Antigravity card. Or delete `~/.hermes/auth/antigravity_tokens.json`.

#### Q: `hermes auth add antigravity` only asks for API key?
> **A:** Fixed in v1.0.0 — it now offers "API key or OAuth?" → select OAuth → opens browser.

#### Q: My config uses a model that doesn't exist in IDE?
> **A:** The bridge auto-maps invalid model names (e.g. `gemini-3.7-pro`) → `gemini-3-flash-agent`. No errors will occur.

---

## 📝 Changelog

### v1.0.0 (31/08/2026)
- ✅ Initial release with OAuth PKCE, bridge server, and multi-account pool.
- ✅ Added **In-Account Model Fallback**: auto-switch to `claude-sonnet-4-6` on Gemini quota exhaustion on the same Google account.
- ✅ Optimized **Priority Fallback**: provider-level deduplication to prevent duplicate default models and preserve user customizations.
- ✅ Full test suite covering failover, model rotation, and fallback deduplication.
- ✅ Fixed `thoughtSignature` handling and `ConnectionResetError` crash.
- ✅ Synced model catalog: 9 models matching real IDE.
