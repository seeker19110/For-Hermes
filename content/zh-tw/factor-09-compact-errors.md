[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 8](factor-08-own-your-control-flow.md)

## Factor 9：精簡化錯誤 (Compact Errors)

**原則：當工具執行失敗時，將錯誤訊息本身當作一個事件，放回情境視窗中，讓 Agent 有機會「自我修復」。**

Agent 的一個神奇之處，在於它具備一定的「自我修復」能力。當一個工具呼叫失敗時，一個好的 LLM 有機會能讀懂錯誤訊息，並在下一次的工具呼叫中修正它的參數。

[![195-factor-09-errors](https://github.com/humanlayer/12-factor-agents/blob/main/img/195-factor-09-errors.gif)](https://github.com/user-attachments/assets/cd7ed814-8309-4baf-81a5-9502f91d4043)

這個模式的實作很簡單，就是在你的工具執行邏輯外面，包一層 `try...except`。

```python
# Agent 迴圈中的一部分
try:
  # 嘗試執行 LLM 建議的工具
  result = execute_tool(next_step)

  # 成功了！將結果記錄下來
  thread.history.append({ "type": "tool_result", "data": result })

except Exception as e:
  # 失敗了！將錯誤訊息也記錄下來
  # 這樣在下一次迴圈時，LLM 就會看到這個錯誤
  thread.history.append({ "type": "error", "data": str(e) })
```

當然，為了避免 Agent 陷入無限重試同一個錯誤的循環，我們通常會加入一個重試計數器：

```python
consecutive_errors = 0

while True:
  # ... 決定下一步 ...

  try:
    result = execute_tool(next_step)
    thread.history.append({ "type": "tool_result", "data": result })
    # 成功了，重置計數器
    consecutive_errors = 0
  except Exception as e:
    consecutive_errors += 1
    if consecutive_errors >= 3:
      # 連續失敗太多次，放棄！
      # 可以在這裡呼叫人類介入的工具
      break

    # 還可以再試試，將錯誤記錄下來
    thread.history.append({ "type": "error", "data": str(e) })
```

當連續錯誤達到一個門檻時，就是一個絕佳的時機去呼叫我們在 Factor 7 中提到的「聯絡人類」工具。

---

### 動手玩玩看：讓模型從錯誤中學習

這個原則的重點，在於如何建構傳回給模型的「情境」。讓我們來看看當工具出錯時，傳給 Claude 或 Gemini 的 `messages` / `contents` 陣列會長什麼樣子。

**場景**：使用者想查詢 "GOOGL" 的股價，但我們的 `get_stock_price` 工具只接受 "GOOG" 這個代號。工具執行因此失敗了。

**我們傳給模型的對話歷史 (適用於 Claude 和 Gemini):**

這個陣列就是我們在 Factor 5 中提到的「統一狀態紀錄」。

```json
[
  {
    "role": "user",
    "content": "幫我查一下 GOOGL 的股價"
  },
  {
    "role": "assistant",
    "content": [
      {
        "type": "tool_use",
        "id": "toolu_1",
        "name": "get_stock_price",
        "input": { "ticker_symbol": "GOOGL" }
      }
    ]
  },
  {
    "role": "tool",
    "tool_use_id": "toolu_1",
    "content": [
      {
        "type": "tool_error",
        "error": {
          "type": "invalid_request_error",
          "message": "找不到股票代號 'GOOGL'。您是不是要找 'GOOG'？"
        }
      }
    ]
  }
]
```

**說明：**
1.  **User Message**：使用者的原始請求。
2.  **Assistant Message**：模型第一次的回應，它呼叫了 `get_stock_price` 工具，但用了錯誤的參數 `GOOGL`。
3.  **Tool Message**：我們的應用程式在執行工具失敗後，將這個 `tool_error` 事件加到歷史紀錄中。**我們沒有用 `text`，而是用 `tool_error` 這個結構化的方式來回報錯誤**，這能讓模型更清楚地知道發生了什麼事。我們甚至在錯誤訊息中給了它提示。

**下一步？**

當我們把上面這段完整的歷史紀錄再次傳給 LLM 時，一個好的模型會：
1.  看到自己上次呼叫 `get_stock_price` 失敗了。
2.  讀懂 `error` 訊息中的內容。
3.  在下一次的回應中，修正參數，再次呼叫同一個工具：

```json
{
    "role": "assistant",
    "content": [
      {
        "type": "tool_use",
        "id": "toolu_2",
        "name": "get_stock_price",
        "input": { "ticker_symbol": "GOOG" }
      }
    ]
}
```

這就是 Agent 的「自我修復」能力。透過誠實地將錯誤回報給模型，我們給了它修正自己的機會。

---

[下一章：Factor 10 - 專注、小型的 Agent (Small, Focused Agents) →](factor-10-small-focused-agents.md)
