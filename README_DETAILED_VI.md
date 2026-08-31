# 🌟 Hermes Antigravity OAuth Plugin & Local Bridge

> **Plugin mở rộng cho Hermes Agent**, cho phép tích hợp và sử dụng toàn bộ tài nguyên mô hình AI cao cấp từ tài khoản **Google Antigravity OAuth** (Gemini 3.7 Flash, Claude Sonnet/Opus 4.6, GPT-OSS 120B) vào Hermes Agent — qua CLI, Telegram, Discord, Dashboard và mọi nền tảng khác.

**Phiên bản:** 1.0.0 — Cập nhật: 31/08/2026

---

## 📌 Tính Năng Nổi Bật

### Cốt lõi
- **🔑 OAuth PKCE Login** — Đăng nhập Google 1-click qua browser, giống hệt IDE thật
- **🔄 Token Auto-Refresh** — Tự động làm mới token khi sắp hết hạn (120s trước)
- **👥 Multi-Account Pool** — Xoay vòng nhiều tài khoản, auto-failover khi Rate Limit
- **🖥️ IDE Simulation** — Giả lập hoàn toàn môi trường Antigravity IDE (headers, fingerprint, API endpoint)
- **📡 Bridge Server** — Server cục bộ port 8100, API tương thích OpenAI format
- **🧠 9 Models** — Đồng bộ 100% danh mục mô hình từ Antigravity IDE thật
- **🔄 In-Account Model Fallback** — Tự động thử model dự phòng cùng tài khoản (Gemini 3.7 Flash → Claude Sonnet 4.6) khi model chính hết quota, trước khi xoay tài khoản hoặc dùng provider ngoài

### Tích hợp Dashboard
- **Tab Keys (`/env`):** Thẻ kết nối OAuth, hiển thị email, token, thời hạn
- **Tab System (`/system`):** Credential Pool multi-account
- **Tab Models (`/models`):** Chọn model 1-click trong SET MAIN MODEL
- **Chat Sidebar:** Model picker trực tiếp trong giao diện chat

### An toàn
- **🛡️ Bảo toàn khi nâng cấp** — Token + Plugin lưu ngoài git repo (`~/.hermes/`)
- **🔌 Daemon Auto-Wake** — Bridge tự khởi động khi gateway cần
- **🖼️ Vision Support** — Hỗ trợ gửi ảnh multimodal
- **🌊 SSE Streaming** — Stream response real-time

---

## 📂 Cấu Trúc Thư Mục

```
HERMES-ANTIGRAVITY PLUGIN/
├── README.md              # Tài liệu hướng dẫn (file này)
├── install.py             # Script cài đặt 1-Click tự động
├── manage.py              # CLI quản lý Bridge & OAuth
├── plugin/                # Hermes Model Provider Plugin
│   ├── plugin.yaml        # Metadata và danh mục models
│   └── __init__.py        # ProviderProfile (auto-wake + vision)
└── bridge/                # Runtime Engine
    ├── auth.py            # OAuth PKCE, Token Storage, Auto-refresh (622 lines)
    ├── client.py          # OpenAI ↔ Gemini Code Assist translator (818 lines)
    ├── server.py          # HTTP Server port 8100 (288 lines)
    └── __init__.py        # Module exports
```

---

## 📋 Danh Sách 9 Models (Khớp Antigravity IDE)

| # | Model ID | Tên Hiển Thị | Tier | Đặc Điểm |
|:-:|---|---|---|---|
| 1 | **`gemini-3.7-flash`** | Gemini 3.7 Flash High | Fast | Suy luận sâu mức High (Khuyên dùng Main Model) |
| 2 | **`gemini-3.7-flash-medium`** | Gemini 3.7 Flash Medium | Fast | Suy luận cân bằng Medium (Mặc định IDE) |
| 3 | **`gemini-3.7-flash-low`** | Gemini 3.7 Flash Low | Fast | Độ trễ thấp nhất, phản hồi siêu tốc |
| 4 | **`gemini-3.6-flash`** | Gemini 3.6 Flash Medium | Fast | Bản 3.6 ổn định |
| 5 | **`gemini-3.5-flash`** | Gemini 3.5 Flash Medium | Fast | Flash nhẹ nhàng |
| 6 | **`gemini-3.1-pro`** | Gemini 3.1 Pro Low | — | Chuyên phân tích & tái cấu trúc mã nguồn |
| 7 | **`claude-sonnet-4-6`** | Claude Sonnet 4.6 (Thinking) | — | Claude Sonnet kèm tư duy mở rộng |
| 8 | **`claude-opus-4-6`** | Claude Opus 4.6 (Thinking) | — | Claude Opus suy luận đỉnh cao |
| 9 | **`gpt-oss-120b`** | GPT-OSS 120B (Medium) | — | Mô hình mã nguồn mở 120B qua Google Cloud |

> **Lưu ý:** `gemini-3.7-pro` KHÔNG tồn tại trong Antigravity IDE và đã được loại bỏ.

---

## 🚀 Hướng Dẫn Cài Đặt

### Cách 1: Cài đặt tự động 1-Click (Khuyên Dùng)

```bash
cd "D:\AI DOCUMENT\HERMES\HERMES-ANTIGRAVITY PLUGIN"
python install.py
```

Script sẽ tự động:
1. Copy plugin → `~/.hermes/plugins/model-providers/antigravity/`
2. Copy bridge → `~/.hermes/bridge/antigravity/`
3. Đồng bộ với workspace hiện tại nếu đang trong Hermes Agent repo

### Cách 2: Quản lý qua CLI (`manage.py`)

```bash
# Kiểm tra trạng thái
python manage.py status

# Đăng nhập Google OAuth
python manage.py login

# Khởi động bridge daemon
python manage.py start

# Cấu hình Hermes dùng Antigravity
python manage.py setup --model gemini-3.7-flash

# Dừng bridge
python manage.py stop
```

### Cách 3: Đăng nhập qua Hermes CLI

```bash
hermes auth add antigravity
# → Chọn "2. OAuth login (authenticate via browser)"
# → Browser mở Google Consent → Đăng nhập → Done
```

---

## 🌐 Hướng Dẫn Sử Dụng Dashboard

### Bước 1: Đăng nhập OAuth

1. Truy cập Dashboard: `http://localhost:9119`
2. Vào tab **Keys & OAuth** (`/env`)
3. Tìm thẻ **Google Antigravity (OAuth)** → Bấm **[LOGIN]**
4. Browser mở Google Consent → Đồng ý → Dashboard tự lưu token

### Bước 2: Chọn Model

1. Vào tab **Models** (`/models`)
2. Bấm **SET MAIN MODEL**
3. Chọn **Google Antigravity (OAuth)**
4. Chọn model (ví dụ: `gemini-3.7-flash`) → **Switch**

### Bước 3: Sử dụng

Chat trực tiếp trên Dashboard, CLI, Telegram, Discord hoặc bất kỳ platform nào.

---

## 👥 Multi-Account & Failover

### Thêm tài khoản trên Dashboard (`/system`)

1. Truy cập `http://localhost:9119/system`
2. Cuộn xuống **Credential Pool**
3. Nhập: `PROVIDER: antigravity` / `API KEY: <access_token>` / `LABEL: email`
4. Bấm **ADD KEY**

Hermes sẽ tự động xoay sang tài khoản khác khi gặp Rate Limit 429.

### Thêm qua CLI

```bash
python manage.py login
# Chọn tài khoản Google thứ 2 → Token được lưu tự động
```

### Cấu hình trực tiếp `~/.hermes/auth.json`

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

## 🔬 Kiến Trúc Kỹ Thuật

### Luồng Hoạt Động

```
User Request (OpenAI format)
    ↓
Hermes Agent (cli/telegram/discord/tui)
    ↓
Antigravity Bridge (localhost:8100)
    ├── Resolve OAuth token (auto-refresh if needed)
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

### 7 Lớp Giả Lập IDE

Plugin giả lập hoàn toàn môi trường Antigravity IDE thật:

| Lớp | Chi tiết | Phân biệt được? |
|---|---|---|
| **1. OAuth Client ID** | Dùng public Client ID gốc của Google Antigravity | ❌ Không |
| **2. HTTP Headers** | `User-Agent: Antigravity/1.0.0`, `X-Goog-Api-Client: gccl/antigravity-ide` | ❌ Không |
| **3. Client Metadata** | `ideType: ANTIGRAVITY`, `pluginType: GEMINI` | ❌ Không |
| **4. API Endpoint** | `v1internal` (API nội bộ, không phải public API) | ❌ Không |
| **5. OAuth Scopes** | `cclog`, `experimentsandconfigs` (scopes đặc thù IDE) | ❌ Không |
| **6. PKCE Flow** | Port 51121, SHA-256 code challenge | ❌ Không |
| **7. Request Format** | Gemini Code Assist envelope + thoughtSignature | ❌ Không |

> **Từng request riêng lẻ không phân biệt được** với IDE thật.
> Rủi ro chỉ nằm ở **usage volume** nếu dùng quá nhiều (24/7 qua gateway).

### Xử Lý Đặc Biệt

- **thoughtSignature**: Nhận diện real signature vs fake `"skip_thought_signature_validator"` → chuyển tool calls không hợp lệ thành text format
- **Role Alternation**: Tự merge consecutive same-role messages (user/user → user)
- **Connection Reset**: Server không crash khi client đóng kết nối sớm
- **Model Alias**: Tự map model names không hợp lệ sang model gần nhất

---

## ☁️ Triển Khai Cloud / VPS

1. **Chuẩn bị Token** — Copy `~/.hermes/auth/antigravity_tokens.json` từ máy cá nhân lên VPS
2. **Cài đặt Plugin:**
   ```bash
   python install.py
   ```
3. **Khởi động:**
   ```bash
   python ~/.hermes/bridge/antigravity/manage.py start
   hermes gateway run
   ```

---

## ❓ FAQ

#### Q: Khi `git pull` hoặc cập nhật Hermes, plugin có bị mất?
> **A:** Hoàn toàn **KHÔNG**. Plugin lưu tại `~/.hermes/plugins/`, token tại `~/.hermes/auth/` — nằm ngoài git repo. Nếu cần đồng bộ lại, chạy `python install.py`.

#### Q: Bridge bị crash liên tục?
> **A:** Phiên bản 1.0.0 đã fix lỗi `ConnectionResetError`. Gateway sẽ tự khởi lại bridge qua `ensure_antigravity_bridge_running()`. Không cần restart thủ công.

#### Q: Làm sao ngắt kết nối?
> **A:** Dashboard → Tab Keys → **[DISCONNECT]** tại thẻ Antigravity. Hoặc xóa file `~/.hermes/auth/antigravity_tokens.json`.

#### Q: `hermes auth add antigravity` chỉ hỏi API key?
> **A:** Phiên bản 1.0.0 đã fix — giờ sẽ hỏi "API key hay OAuth?" → chọn OAuth → mở browser.

#### Q: Config fallback dùng model không có trong IDE?
> **A:** Bridge tự map model không hợp lệ (VD: `gemini-3.7-pro`) → `gemini-3-flash-agent`. Không gây lỗi.

---

## 📝 Changelog

### v1.0.0 (31/08/2026)
- ✅ Phiên bản đầu tiên tích hợp đầy đủ OAuth PKCE, bridge server cục bộ, auto-failover đa tài khoản.
- ✅ Thêm cơ chế **In-Account Model Fallback**: tự động chuyển đổi sang `claude-sonnet-4-6` khi hết quota Gemini trên cùng tài khoản Google trước khi xoay tài khoản trong pool.
- ✅ Tối ưu hóa **Priority Fallback**: tự động gộp cấu hình theo nhà cung cấp (provider-level deduplication) tránh trùng lặp model mặc định khi nâng cấp/cài đặt.
- ✅ Bảo toàn model tùy chỉnh của người dùng khi cài đè hoặc nâng cấp plugin.
- ✅ Bổ sung bộ test suite hoàn chỉnh bao gồm kiểm thử logic fallback và deduplication.
- ✅ Khắc phục hoàn toàn lỗi `thoughtSignature` và `ConnectionResetError` trong server bridge.
- ✅ Đồng bộ model catalog: 9 mô hình khớp hoàn chỉnh với danh mục IDE thật.

---

## 📄 License
Phát triển cho cộng đồng Hermes Agent & Antigravity.
Tương thích giấy phép MIT / Apache 2.0.
