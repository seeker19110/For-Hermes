[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 6](factor-06-launch-pause-resume.md)

## Factor 7：透過工具與人類聯繫 (Contact humans with tool calls)

**原則：不要將「與人類對話」視為一個特殊的、預設的輸出。相反地，將它也視為一個可以被呼叫的「工具」。**

在大部分的 LLM API 中，模型在最後一步總是要做一個高風險的二選一：我是該回傳一段自然語言文字，還是該回傳一個結構化的工具呼叫 JSON？

![170-contact-humans-with-tools](../../img/170-contact-humans-with-tools.png)

這個決策完全賭在模型輸出的第一個 token 上。但我們可以換個思路：**強制模型總是輸出 JSON**。如果它想跟使用者說話，就讓它呼叫一個名為 `ask_human` 或 `request_approval` 的工具。

這樣一來，你的 Agent 的輸出就永遠是可預測的、結構化的資料。與人類的互動，也變成了你程式中一個可以明確處理的、標準化的流程。

### 範例：定義一個「請求人類輸入」的工具

我們可以定義一個這樣的工具：

```python
class RequestHumanInput:
  intent: "request_human_input"
  question: str # 要問人類的問題
  context: str  # 提供一些額外的情境
  options: {    # 提供選項
      "format": "yes_no" # 或 "multiple_choice"
  }
```

當你的 Agent 迴圈收到這個工具呼叫時，它要做的事就很清楚了：

```python
# Agent 迴圈中的一部分
if next_step.intent == 'request_human_input':
  # 1. 將「已請求人類輸入」這個事件存到歷史紀錄中
  thread.events.append({ 'type': 'human_input_requested', 'data': next_step })

  # 2. 儲存目前的狀態
  thread_id = await save_state(thread)

  # 3. 透過某個系統（Email, Slack, APP推播）通知人類
  await notify_human(next_step.question, thread_id)

  # 4. 暫停迴圈，等待人類的回應
  return
```

之後，當人類透過某個介面回應後，你的系統會接收到一個帶有 `thread_id` 的請求，然後就可以從對應的 session 中斷點繼續執行了（這完美結合了 Factor 6 的概念）。

---

### 動手玩玩看：讓模型在關鍵時刻請求人類批准

讓我們來模擬一個「部署機器人」的場景。我們希望它在部署到「生產環境」(production) 這種高風險操作前，一定要先徵求人類同意。

#### 範例：讓 Claude/Gemini 請求批准

我們會定義兩個工具：一個是 `deploy_code`，另一個是 `request_human_approval`。然後我們在系統提示中，明確告知模型：「部署到 production 環境前，必須先呼叫 `request_human_approval` 工具。」

**1. 定義工具**
```json
{
    "tools": [
        {
            "name": "deploy_code",
            "description": "將指定的程式碼版本部署到指定的環境 (staging 或 production)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "version": { "type": "string", "description": "要部署的版本號，例如 'v1.2.3'" },
                    "environment": { "type": "string", "enum": ["staging", "production"] }
                },
                "required": ["version", "environment"]
            }
        },
        {
            "name": "request_human_approval",
            "description": "當需要人類批准才能進行高風險操作時，呼叫此工具。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "要向人類提問以請求批准的問題"
                    }
                },
                "required": ["question"]
            }
        }
    ]
}
```

**2. 撰寫包含安全規則的系統提示**
```
你是一個自動化部署機器人。你的任務是安全地執行部署。
規則：
- 部署到 'staging' 環境可以直接執行。
- **部署到 'production' 環境前，必須、絕對要先呼叫 `request_human_approval` 工具來取得人類同意。**
```

**3. 呼叫 API**

我們現在下達一個高風險指令：「幫我把 v1.2.3 版部署到 production」。看看模型會怎麼做。

```bash
# 這段 curl 適用於 Claude，Gemini 的版本與之類似，只需替換 API URL、驗證方式和 JSON payload 的結構即可。
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: YOUR_ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-3-5-sonnet-20240620",
    "system": "你是一個自動化部署機器人。你的任務是安全地執行部署。規則：部署到 'staging' 環境可以直接執行。**部署到 'production' 環境前，必須、絕對要先呼叫 `request_human_approval` 工具來取得人類同意。**",
    "messages": [
        {"role": "user", "content": "幫我把 v1.2.3 版部署到 production"}
    ],
    "tools": [
        {
            "name": "deploy_code",
            "description": "將指定的程式碼版本部署到指定的環境 (staging 或 production)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "version": { "type": "string", "description": "要部署的版本號，例如 'v1.2.3'" },
                    "environment": { "type": "string", "enum": ["staging", "production"] }
                },
                "required": ["version", "environment"]
            }
        },
        {
            "name": "request_human_approval",
            "description": "當需要人類批准才能進行高風險操作時，呼叫此工具。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "要向人類提問以請求批准的問題"
                    }
                },
                "required": ["question"]
            }
        }
    ]
}'
```

**預期的回應**：

一個設計良好的模型，會遵循系統提示的規則，**不會**直接去呼叫 `deploy_code`。相反地，它會先呼叫 `request_human_approval`：

```json
{
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_...",
      "name": "request_human_approval",
      "input": {
        "question": "您確定要將 v1.2.3 版本部署到 production 環境嗎？這將會影響到線上使用者。"
      }
    }
  ],
  "stop_reason": "tool_use"
}
```

這就是這個原則的威力。我們將「與人類互動」這個流程，變成了一個標準化、可預測、可控制的工具，大大提升了 Agent 的可靠性和安全性。

---

[下一章：Factor 8 - 掌握你的控制流程 (Own Your Control Flow) →](factor-08-own-your-control-flow.md)
