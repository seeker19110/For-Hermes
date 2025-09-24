[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 2](factor-02-own-your-prompts.md)

## Factor 3：掌握你的情境視窗 (Own your context window)

**原則：LLM 的每一次呼叫，都是一次「情境工程」(Context Engineering)。你送進去的，決定了你能得到的。**

大型語言模型 (LLM) 本質上是「無狀態的函式」(stateless functions)。你給它什麼輸入 (Input)，它就給你對應的輸出 (Output)。它沒有記憶。我們感受到的「記憶」或「對話的連續性」，其實是我們在每一次呼叫時，都把先前的對話歷史當作「情境」(Context) 一併送給了它。

> **在 Agent 的任何一個時間點，你送給 LLM 的輸入，其實都在說：「到目前為止發生了這些事，下一步該怎麼辦？」**

所謂的「情境工程」，就是精心設計這個輸入的過程。好的情境包含：
- **系統提示與指令** (我們在 Factor 2 討論過的)
- **外部資料** (例如透過 RAG 檢索的文件)
- **過去的狀態** (例如先前的工具呼叫、執行結果、錯誤訊息)
- **相關的歷史對話** (也就是「記憶」)
- **關於輸出格式的指示**

![Context Engineering](../../img/220-context-engineering.png)

### 標準格式 vs. 自訂格式

大部分的 API Client 都遵循一個標準的、基於「角色」的對話格式：

```json
[
  { "role": "system", "content": "你是一個很棒的助理..." },
  { "role": "user", "content": "可以部署後端嗎？" },
  { "role": "assistant", "tool_calls": [{...}] },
  { "role": "tool", "content": "{...}" }
]
```

這個格式很通用，但在追求極致效能時，它未必是最好的選擇。因為它可能包含了許多重複的、對模型來說不夠「資訊密集」的內容。

另一種做法，是**打造你自己的情境格式**，將所有資訊壓縮、整理後，放進一個（或多個）訊息中。例如，把整段歷史塞進一個 `user` 訊息裡：

```xml
<!-- 這整段文字，會被當作單一的 user message 送給 LLM -->
到目前為止的對話紀錄如下：

<slack_message>
    From: @alex
    Channel: #deployments
    Text: 可以部署後端嗎？
</slack_message>

<tool_call name="list_git_tags" />

<tool_result name="list_git_tags">
    tags:
      - name: "v1.2.3"
      - name: "v1.2.2"
</tool_result>

下一步該怎麼辦？
```

這種 XML 標籤風格的格式，只是其中一種範例。重點是，你可以自由實驗，找出對你的應用程式來說，資訊密度最高、最省 Token、模型最能理解的格式。

### 為什麼要掌握情境視窗？
1.  **資訊密度**：用最精簡的方式傳達最豐富的資訊。
2.  **錯誤處理**：可以決定如何向模型呈現錯誤，甚至在錯誤解決後將其從情境中移除。
3.  **安全性**：完全控制哪些敏感資訊會被傳送給 LLM。
4.  **靈活性**：隨時根據實驗結果調整你的情境建構策略。
5.  **Token 效率**：省錢，還可能因為更精簡的情境而獲得更好的效能。

---

### 動手玩玩看：建構你自己的對話歷史

#### 範例 1：使用 Claude API 管理對話

Claude 的 Messages API 很自然地支援多輪對話。你只需要把 `user` 和 `assistant` 的訊息輪流放進 `messages` 陣列中即可。

**標準做法 (多輪對話格式):**

```bash
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: YOUR_ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-3-5-sonnet-20240620",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "我的名字是 Jules。"},
        {"role": "assistant", "content": "你好，Jules！很高興認識你。"},
        {"role": "user", "content": "你還記得我叫什麼名字嗎？"}
    ]
}'
```
Claude 會因為看到完整的對話歷史，而能正確回答你的名字。

**自訂格式做法 (單一 User 訊息):**

現在，我們來實踐 Factor 3 的精神，將歷史「壓平」成單一的 user message。

```bash
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: YOUR_ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-3-5-sonnet-20240620",
    "max_tokens": 1024,
    "system": "你正在跟一位使用者對話，請根據以下的對話紀錄回答問題。",
    "messages": [
        {"role": "user", "content": "對話紀錄：\n\n人類：我的名字是 Jules。\nAI：你好，Jules！很高興認識你。\n\n---\n\n新的問題：你還記得我叫什麼名字嗎？"}
    ]
}'
```
這種方式讓你有完全的控制權，可以決定歷史要怎麼呈現，例如可以加上時間戳、過濾掉不重要的訊息、或用更精簡的格式來節省 token。

#### 範例 2：為 Gemini 建構對話歷史

Gemini 的作法非常類似，`contents` 陣列就是用來存放多輪對話歷史的地方。

**標準做法 (多輪 `contents`):**
```bash
PROJECT_ID="your-gcp-project-id"
LOCATION="us-central1"
MODEL_ID="gemini-1.5-flash-001"

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL_ID}:generateContent" \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [{"text": "我的名字是 Jules。"}]
      },
      {
        "role": "model",
        "parts": [{"text": "你好，Jules！很高興認識你。"}]
      },
      {
        "role": "user",
        "parts": [{"text": "你還記得我叫什麼名字嗎？"}]
      }
    ]
  }'
```

**自訂格式做法 (單一 `contents` 項目):**
```bash
PROJECT_ID="your-gcp-project-id"
LOCATION="us-central1"
MODEL_ID="gemini-1.5-flash-001"

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL_ID}:generateContent" \
  -d '{
    "systemInstruction": {
      "parts": { "text": "你正在跟一位使用者對話，請根據以下的對話紀錄回答問題。" }
    },
    "contents": [{
      "role": "user",
      "parts": [{
        "text": "對話紀錄：\n\n人類：我的名字是 Jules。\nAI：你好，Jules！很高興認識你。\n\n---\n\n新的問題：你還記得我叫什麼名字嗎？"
      }]
    }]
  }'
```
這再次證明，無論你用哪種模型，**你，而且只有你，應該要能 100% 掌握模型看到的所有資訊**。

---

[下一章：Factor 4 - 工具即結構化輸出 (Tools Are Structured Outputs) →](factor-04-tools-are-structured-outputs.md)
