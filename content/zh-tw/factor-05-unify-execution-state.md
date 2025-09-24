[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 4](factor-04-tools-are-structured-outputs.md)

## Factor 5：統一執行狀態與業務狀態 (Unify execution state and business state)

**原則：盡可能地將「執行狀態」與「業務狀態」統一。一個 Agent 的所有狀態，都應該能從單一的事件歷史紀錄中推斷出來。**

在軟體系統中，我們常常會區分兩種狀態：
- **業務狀態 (Business State)**：指應用程式中「發生了什麼事」。例如，在一個 Agent 的對話中，這就是所有的使用者訊息、工具呼叫、工具執行結果的歷史紀錄。
- **執行狀態 (Execution State)**：指應用程式「現在正在做什麼」。例如：`AWAITING_USER_INPUT` (等待使用者輸入)、`CALLING_TOOL` (正在呼叫工具)、`RETRYING_API_CALL` (正在重試 API) 等。

許多框架會用複雜的狀態機來分別管理這兩種狀態。但這往往會讓系統變得過於複雜。

一個更簡單、更強大的模式是：**只儲存「業務狀態」(也就是那份不可變的事件歷史紀錄)，並從中「推斷」出目前的「執行狀態」。**

[![155-unify-state](https://github.com/humanlayer/12-factor-agents/blob/main/img/155-unify-state-animation.gif)](https://github.com/user-attachments/assets/e5a851db-f58f-43d8-8b0c-1926c99fc68d)

### 範例：一個外送 Agent 的事件紀錄

想像一個點餐 Agent。它的所有狀態，都可以被記錄成一個簡單的事件陣列 (array of events)：

```json
[
  { "type": "USER_SAID", "text": "我想訂一份麥當勞歡樂送" },
  { "type": "TOOL_CALL", "tool_name": "search_restaurants", "params": {"keyword": "麥當勞"} },
  { "type": "TOOL_RESULT", "tool_name": "search_restaurants", "output": [{ "id": "rest_123", "name": "麥當勞-信義店" }] },
  { "type": "USER_SAID", "text": "就信義店吧" },
  { "type": "TOOL_CALL", "tool_name": "get_menu", "params": {"restaurant_id": "rest_123"} },
  { "type": "TOOL_ERROR", "tool_name": "get_menu", "error": "API timeout" },
  { "type": "TOOL_CALL", "tool_name": "get_menu", "params": {"restaurant_id": "rest_123"} }
]
```

從這份紀錄，我們可以**推斷**出目前的執行狀態：
- 因為最後一個事件是 `TOOL_CALL`，所以現在的狀態是 `WAITING_FOR_TOOL_RESULT` (等待工具執行結果)。
- 我們也可以看到，前一次的 `get_menu` 呼叫失敗了，所以這是一次重試 (retry)。

我們不需要一個獨立的變數 `current_state = "WAITING_FOR_TOOL_RESULT"`。所有的資訊都在這份歷史紀錄裡了。

### 這跟 Claude / Gemini 有什麼關係？

這個原則與我們在 **Factor 3** 中學到的「掌握情境視窗」息息相關。

我們傳送給 Claude 或 Gemini 的 `messages` 或 `contents` 陣列，**它本身就是一份完美的「統一狀態紀錄」**。

**標準的 API 呼叫模式，本身就在實踐這個原則：**

1.  **準備狀態**：你會從資料庫 (例如：PostgreSQL, Redis) 中讀取某個 `conversation_id` 的所有歷史訊息。
2.  **附加新訊息**：將使用者最新的問題加到這個陣列的最後。
3.  **呼叫 LLM**：將整個陣列（也就是完整的「業務狀態」）傳給 LLM。
4.  **LLM 回應 (決策)**：LLM 回傳一個新的 `assistant` 訊息（可能包含 `tool_use`）。
5.  **儲存狀態**：你將 LLM 的回應也存進資料庫，加到歷史紀錄的最後面。
6.  **推斷執行狀態**：你的應用程式檢查剛剛存入的 `assistant` 訊息。
    - 如果它包含 `tool_use`，那麼「執行狀態」就是 `CALLING_TOOL`。你的程式接著去執行該工具。
    - 如果它只包含 `text`，那麼「執行狀態」就是 `WAITING_FOR_USER_INPUT`。你的程式將文字顯示給使用者。

你看，我們完全不需要一個獨立的狀態機。整個 Agent 的流程，都是由「**讀取歷史 -> 做出決策 -> 將決策加入歷史**」這個簡單的循環所驅動的。

### 統一狀態的好處

1.  **簡單**：所有狀態只有一個來源。
2.  **易於序列化**：整個對話歷史可以輕易地被存成 JSON，放進任何資料庫。
3.  **方便除錯**：一目了然地看到所有發生過的事，沒有隱藏的狀態。
4.  **高靈活性**：要增加新的狀態？只要定義一種新的事件類型就好。
5.  **易於恢復**：從任何時間點恢復對話，只需要把歷史紀錄載入回來就行。

---

[下一章：Factor 6 - 透過簡單的 API 啟動/暫停/恢復 (Launch/Pause/Resume) →](factor-06-launch-pause-resume.md)
