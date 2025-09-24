[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 3](factor-03-own-your-context-window.md)

## Factor 4：工具即結構化輸出 (Tools are just structured outputs)

**原則：所謂的「工具」，並不需要很複雜。它的核心，就只是讓 LLM 產生一段結構化的輸出 (例如 JSON)，你的程式碼再來決定如何處理它。**

![140-tools-are-just-structured-outputs](../../img/140-tools-are-just-structured-outputs.png)

我們不必把「工具呼叫」(Tool Calling) 看得太神秘。它並不是 LLM 真的在「執行」什麼東西。它只是在「建議」你的程式去執行某個動作。

這個模式很簡單：
1. LLM 根據你的提示和情境，輸出一段結構化的 JSON。
2. 你的程式碼接收並解析這個 JSON。
3. 根據 JSON 的內容，你的程式碼決定要執行哪個函式或 API。
4. 執行結果被記錄下來，並可能被放回情境視窗中，供下一次 LLM 呼叫參考。

這種方式漂亮地將 **LLM 的決策** 和 **你應用程式的執行** 分離開來。LLM 負責決定「做什麼」，而你的程式碼 100% 掌握「如何做」。

例如，假設你有兩個工具：`CreateIssue` (建立一個新的 issue) 和 `SearchIssues` (搜尋 issue)。讓 LLM 在這兩者之間選擇，其實就是讓它產生兩種不同結構的 JSON。

```python
# 這是你在程式碼中定義的資料結構
class CreateIssue:
  intent: "create_issue"
  title: str
  description: str

class SearchIssues:
  intent: "search_issues"
  query: str
```

當 LLM 回傳 `{ "intent": "create_issue", "title": "...", ... }` 時，你的程式就知道要去呼叫建立 issue 的函式。這讓你可以完全控制後續的流程，例如在建立 issue 前先做一些驗證，或是記錄 log 等等。

---

### 動手玩玩看：讓模型為你選擇工具

現在，我們來看看如何定義多個工具，並讓模型根據我們的問題，智慧地選擇其中一個來「呼叫」(也就是，產生對應的 JSON)。

#### 範例 1：讓 Claude 選擇工具

我們同時提供 `get_weather` 和 `get_stock_price` 兩個工具給 Claude，然後問它一個關於股價的問題。

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
        {"role": "user", "content": "台積電現在的股價是多少？"}
    ],
    "tools": [
        {
            "name": "get_weather",
            "description": "取得指定城市目前的氣象資訊",
            "input_schema": {
                "type": "object",
                "properties": { "city": { "type": "string" } },
                "required": ["city"]
            }
        },
        {
            "name": "get_stock_price",
            "description": "取得指定股票代號目前的股價",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ticker_symbol": {
                        "type": "string",
                        "description": "股票代號，例如：2330.TW, AAPL"
                    }
                },
                "required": ["ticker_symbol"]
            }
        }
    ]
}'
```

**預期的 Claude 回應**：

Claude 會忽略無關的 `get_weather` 工具，並正確地選擇 `get_stock_price`，同時從問題中提取出「台積電」這個實體，並聰明地轉換成它在描述中看到的股票代號格式 `2330.TW` (這部分取決於模型的知識庫)。

```json
{
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_...",
      "name": "get_stock_price",
      "input": {
        "ticker_symbol": "2330.TW"
      }
    }
  ],
  "stop_reason": "tool_use"
}
```
你的程式碼只要看到 `name` 是 `get_stock_price`，就知道該怎麼做了。

#### 範例 2：讓 Gemini 選擇工具

同樣的場景，我們在 Vertex AI 上對 Gemini 來做。

```bash
PROJECT_ID="your-gcp-project-id"
LOCATION="us-central1"
MODEL_ID="gemini-1.5-flash-001"

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL_ID}:generateContent" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{ "text": "台積電現在的股價是多少？" }]
    }],
    "tools": [{
      "functionDeclarations": [
        {
          "name": "get_weather",
          "description": "取得指定城市目前的氣象資訊",
          "parameters": {
            "type": "OBJECT",
            "properties": {
              "city": { "type": "STRING" }
            },
            "required": [ "city" ]
          }
        },
        {
          "name": "get_stock_price",
          "description": "取得指定股票代號目前的股價",
          "parameters": {
            "type": "OBJECT",
            "properties": {
              "ticker_symbol": { "type": "STRING", "description": "股票代號，例如：2330.TW, AAPL" }
            },
            "required": [ "ticker_symbol" ]
          }
        }
      ]
    }]
  }'
```

**預期的 Gemini 回應**：

Gemini 同樣會回傳一個 `functionCall`，指名要使用 `get_stock_price` 工具。

```json
{
  "candidates": [
    {
      "content": {
        "role": "model",
        "parts": [
          {
            "functionCall": {
              "name": "get_stock_price",
              "args": {
                "ticker_symbol": "2330.TW"
              }
            }
          }
        ]
      }
    }
  ]
}
```
這個簡單的例子完美詮釋了「工具即結構化輸出」的核心精神。LLM 的工作就是產生這個 JSON，而剩下的，都由你自己的程式碼全權掌控。

---

[下一章：Factor 5 - 統一執行狀態與業務狀態 (Unify Execution State) →](factor-05-unify-execution-state.md)
