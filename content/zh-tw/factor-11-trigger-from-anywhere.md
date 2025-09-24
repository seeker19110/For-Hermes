[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 10](factor-10-small-focused-agents.md)

## Factor 11：從任何地方觸發 (Trigger From Anywhere)

**原則：不要把你的 Agent 關在一個小小的聊天視窗裡。要讓它能從各種不同的管道被啟動，並且能透過同樣的管道來回應。**

一個真正強大的 Agent，應該要能融入我們現有的工作流程中。它應該像一個真正的數位同事，我們可以在 Slack 上 @ 它，可以寄 Email 給它，甚至可以讓它在每天早上九點自動開始工作。

![1b0-trigger-from-anywhere](../../img/1b0-trigger-from-anywhere.png)

這就是「隨處觸發」的核心概念。你的 Agent 應該要有一個統一的、標準化的入口（也就是我們在 Factor 6 設計的 `/sessions` API），而你的應用程式則應該有多個「適配器」(Adapters)，負責將來自不同管道的事件，轉換成對這個標準入口的呼叫。

### 範例：一個無所不在的「GitHub Issue 小幫手」

想像一個 Agent，它的核心任務是「協助處理 GitHub issue」。這個 Agent 可以被以下幾種方式觸發：

- **Webhook 觸發**：當有人在一個 issue 上留言「@bot help」時，GitHub 發送一個 webhook 到我們的系統。系統的「GitHub 適配器」接收到這個請求，解析出 issue 內容和使用者是誰，然後呼叫 `POST /sessions` 來啟動一個 Agent 來處理這個 issue。
- **Email 觸發**：使用者可以寄一封 Email 到 `bugs@mycompany.com`。郵件伺服器會將這封信轉發給我們的「Email 適配器」，它會解析郵件主旨和內容，然後同樣去呼叫 `POST /sessions` 來建立一個新的 issue。
- **定時任務觸發**：一個每天半夜執行的排程作業 (Cron Job)，會掃描所有超過 14 天沒有更新的 issue。每找到一個，它就去呼叫 `POST /sessions`，啟動一個 Agent 來詢問 issue 的負責人是否還需要這個 issue。

不論觸發來源是什麼，最終它們都匯集到了同一個 Agent 核心邏輯。而當 Agent 需要回覆時，它也可以透過呼叫 `send_slack_message` 或 `send_email` 等工具，在對應的管道上與使用者互動。

---

### 動手玩玩看：為 Agent 建立多個入口

這個原則的實踐，在於編寫那些「適配器」。讓我們再次擴充我們的 Flask 應用程式，為它加上兩個新的入口：一個接收 GitHub Webhook，一個給定時任務呼叫。

```python
# ... (Factor 6 的 Flask app 和 SESSIONS 依然存在) ...

# 這是我們在 Factor 6 設計的核心 API
# 不論來源是什麼，最後都會呼叫它
def launch_new_agent_session(initial_input):
    session_id = str(uuid.uuid4())
    history = [{"role": "user", "content": initial_input}]
    # ... 後續的 LLM 呼叫和儲存邏輯 ...
    print(f"新的 Agent Session 已啟動: {session_id}")
    return session_id

# === 適配器 1：GitHub Webhook 入口 ===
@app.route("/webhooks/github", methods=["POST"])
def handle_github_webhook():
    payload = request.json

    # 假設我們只關心 issue comment
    if "issue" in payload and "comment" in payload:
        comment_body = payload["comment"]["body"]
        issue_title = payload["issue"]["title"]

        # 簡單的判斷，如果留言包含 @bot
        if "@bot" in comment_body:
            # 將 webhook payload 轉換成 Agent 的初始輸入
            initial_input = f"GitHub Issue '{issue_title}' 有新的留言需要處理：\n\n{comment_body}"

            # 呼叫核心的 Agent 啟動函式
            launch_new_agent_session(initial_input)

    return "OK", 200

# === 適配器 2：每日任務入口 ===
@app.route("/tasks/daily-scan", methods=["POST"])
def handle_daily_scan():
    # 這裡的邏輯會是去資料庫撈出所有符合條件的 issue
    old_issues = [{"title": "按鈕顏色不對"}, {"title": "API 文件有錯字"}] # 虛構資料

    for issue in old_issues:
        initial_input = f"你好，這是一個自動提醒。Issue '{issue['title']}' 已經超過 14 天沒有更新了，請問還需要處理嗎？"

        # 為每一個舊 issue 啟動一個獨立的 Agent session
        launch_new_agent_session(initial_input)

    return jsonify({"status": "ok", "triggered_agents": len(old_issues)})

```
這個範例清楚地展示了：
- **關注點分離**：`handle_github_webhook` 和 `handle_daily_scan` 只負責「翻譯」外部事件，它們不關心 Agent 的內部邏輯。
- **單一入口**：所有的外部事件，最終都透過呼叫 `launch_new_agent_session` 這個標準化的函式，來與核心 Agent 互動。

這種架構讓你的 Agent 系統變得極具彈性，未來要支援新的管道（例如：Line, Telegram），你只需要再多寫一個「適配器」就行了，完全不需要改動核心的 Agent 邏輯。這也正是前幾個 Factor 為我們打下的良好基礎所帶來的回報。

---

[下一章：Factor 12 - 將你的 Agent 當作一個無狀態的 Reducer (Stateless Reducer) →](factor-12-stateless-reducer.md)
