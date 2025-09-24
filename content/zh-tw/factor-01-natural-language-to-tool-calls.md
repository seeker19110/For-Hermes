[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：AI Agent 入門指南](introduction-to-agents.md)

## Factor 1：自然語言轉換為工具呼叫 (Natural Language to Tool Calls)

在建立 Agent 的過程中，最常見也最核心的模式之一，就是將人類的自然語言（我們說的話）轉換成結構化的「工具呼叫」(Tool Calls)。這是一個非常強大的模式，它讓 Agent 能夠理解我們的意圖，並將其轉化為具體的程式碼操作。

![110-natural-language-tool-calls](../../img/110-natural-language-tool-calls.png)

簡單來說，這個模式就是將一句像這樣的日常對話：

> 「能幫我建立一個 750 元的付款連結給 Terri 嗎？款項是贊助二月份的 AI 同好聚會。」

轉換成一個描述 API 呼叫的結構化 JSON 物件，像這樣：

```json
{
  "tool_name": "create_payment_link",
  "parameters": {
    "amount": 750,
    "currency": "TWD",
    "customer_name": "Terri",
    "memo": "贊助二月份的 AI 同好聚會"
  }
}
```

**請注意**：在真實世界的應用中，API 可能會更複雜。一個真正的 Agent 可能需要先呼叫 `search_customer` 工具來查詢 Terri 的顧客 ID，然後才能建立付款連結。不過，核心概念是相同的：**將模糊的語言，轉換為精確的指令**。

一旦語言模型（LLM）產生了這個結構化的 JSON，我們的程式碼就可以很輕易地接收這個指令，並執行對應的動作。

```python
# 這是你的應用程式中的一小段程式碼
def execute_tool(tool_name, parameters):
  if tool_name == 'create_payment_link':
    # 呼叫你的支付服務 API
    result = stripe.create_payment_link(
        amount=parameters['amount'],
        customer=find_customer_id(parameters['customer_name']),
        memo=parameters['memo']
    )
    return result
  elif tool_name == 'send_email':
    # ... 其他工具的處理邏輯
    pass
```

這個原則是所有 Agent 功能的基礎。接下來，我們來看看如何用時下最流行的兩個模型來實現它。

---

### 動手玩玩看：用 Claude 和 Gemini 實現工具呼叫

理論說完了，讓我們來點實際的！這裡我們將展示如何透過 API 和 CLI，讓 Claude 和 Gemini 為我們進行工具呼叫。

#### 範例 1：使用 Claude 3.5 Sonnet API

Anthropic 的 Claude 模型提供了強大的工具使用 (Tool Use) 功能。我們只需要在 API 請求中定義好我們的工具，Claude 就會聰明地在需要時呼叫它們。

**我們的任務**：我們要定義一個 `get_weather` 工具，然後問 Claude「台北現在天氣怎麼樣？」。

你可以使用 `curl` 指令來測試這個 API。記得將 `YOUR_ANTHROPIC_API_KEY` 換成你自己的金鑰。

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
        {"role": "user", "content": "台北現在天氣怎麼樣？"}
    ],
    "tools": [
        {
            "name": "get_weather",
            "description": "取得指定城市目前的氣象資訊",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名稱，例如：台北、東京"
                    }
                },
                "required": ["city"]
            }
        }
    ]
}'
```

**預期的 Claude 回應**：

Claude 不會直接回答天氣，而是會回傳一個 `tool_use` 的內容區塊，告訴我們它想要呼叫哪個工具，以及傳入什麼參數。

```json
{
  "id": "msg_... ",
  "type": "message",
  "role": "assistant",
  "model": "claude-3-5-sonnet-20240620",
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_... ",
      "name": "get_weather",
      "input": {
        "city": "台北"
      }
    }
  ],
  "stop_reason": "tool_use"
}
```

看到這個回應，我們的程式就知道該去執行 `get_weather("台北")` 這個函式了！

#### 範例 2：使用 Google Gemini on Vertex AI (透過 gcloud + curl)

當我們在終端機環境下使用 Google Cloud 時，一個非常常見且強大的模式是**結合 `gcloud` 和 `curl`**。我們使用 `gcloud` 來處理複雜的驗證流程，取得一個有時效性的存取權杖 (Access Token)，然後用大家最熟悉的 `curl` 工具來發送 API 請求。

這樣做的好處是，我們不需要在程式碼或環境變數中儲存敏感的金鑰，同時又能靈活地客製化 API 的請求內容。

**我們的任務**：一樣是定義 `get_weather` 工具，並問 Gemini「台北現在天氣怎麼樣？」。

首先，請確認你已經安裝並登入 `gcloud` CLI。

接著，執行以下這段 `bash` 指令。它會自動幫你填上需要的變數：

```bash
# 替換成你的 GCP 專案 ID 和要在哪個區域執行
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
      "parts": [{
        "text": "台北現在天氣怎麼樣？"
      }]
    }],
    "tools": [{
      "functionDeclarations": [
        {
          "name": "get_weather",
          "description": "取得指定城市目前的氣象資訊",
          "parameters": {
            "type": "OBJECT",
            "properties": {
              "location": {
                "type": "STRING",
                "description": "城市名稱，例如：台北、東京"
              }
            },
            "required": [ "location" ]
          }
        }
      ]
    }]
  }'
```
*請記得將 `your-gcp-project-id` 換成你自己的 Google Cloud 專案 ID。*

**預期的 Gemini 回應**：

Gemini 的回應會在其 `content` 中包含一個 `functionCall` 物件，明確指出它想呼叫的函式與參數。

```json
{
  "candidates": [
    {
      "content": {
        "role": "model",
        "parts": [
          {
            "functionCall": {
              "name": "get_weather",
              "args": {
                "location": "台北"
              }
            }
          }
        ]
      },
      "finishReason": "TOOL_CODE_NOT_IMPLEMENTED",
      // ... 其他資訊
    }
  ],
  // ... 其他資訊
}
```

這再次證明了，無論是透過 API 還是 CLI，我們都能讓大型語言模型將我們的自然語言請求，轉換為程式可以執行的精確指令。這就是建立強大 Agent 的第一步。

---

[下一章：Factor 2 - 掌握你的提示 (Own Your Prompts) →](factor-02-own-your-prompts.md)
