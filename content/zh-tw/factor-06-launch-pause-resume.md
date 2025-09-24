[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 5](factor-05-unify-execution-state.md)

## Factor 6：透過簡單的 API 啟動/暫停/恢復 (Launch/Pause/Resume with simple APIs)

**原則：Agent 也只是一個程式。我們應該能透過簡單、可預測的 API 來控制它的生命週期：啟動、查詢狀態、暫停，以及從暫停中恢復。**

[![pause-resume animation](https://github.com/humanlayer/12-factor-agents/blob/main/img/165-pause-resume-animation.gif)](https://github.com/user-attachments/assets/feb1a425-cb96-4009-a133-8bd29480f21f)

想像一下，如果一個 Agent 需要等待一個長達數小時的外部任務（例如：訓練一個機器學習模型），或是需要等待人類的批准才能進行下一步，我們總不能讓這個 Agent 的程式一直空轉、佔用資源吧？

這就是為什麼「暫停」和「恢復」如此重要。一個設計良好的 Agent 系統，應該要能：
- **啟動 (Launch)**：透過一個簡單的 API 呼叫，就能根據一個初始輸入（例如：一則 Slack 訊息）來啟動一個新的 Agent 工作流程。
- **暫停 (Pause)**：當 Agent 需要等待時（例如：等待工具執行結果、等待人類回覆），它應該能夠自動「暫停」。在我們的架構中，這根本不需要特別做什麼，因為當 LLM 回傳 `tool_use` 或需要人類輸入的指令後，程式的執行就自然停下來了，而所有的狀態都已經被保存在前一個 Factor 提到的「事件歷史紀錄」中了。
- **恢復 (Resume)**：當外部事件完成時（例如：工具執行完畢、人類點擊了批准按鈕），應該要有另一個簡單的 API，可以接收這個新的資訊，將其作為一個新事件加入歷史紀錄，並觸發 Agent 繼續往下執行。

這個原則的實現，高度依賴我們在 **Factor 5** 中建立的「統一狀態」模型。正因為所有的狀態都在一份可序列化的歷史紀錄中，我們才能輕易地儲存它、讀取它，並從任何一點繼續執行。

---

### 動手玩玩看：設計 Agent 的生命週期 API

這個原則比較偏向應用程式的架構設計，而非單一的 LLM API 呼叫。讓我們用 Python 的 Flask 框架來寫一段虛擬碼，看看這個 API 會長什麼樣子。

我們假設有一個非常簡單的記憶體內資料庫 `SESSIONS`，用來儲存所有 Agent 的對話歷史。

```python
from flask import Flask, request, jsonify
import uuid

# 偽資料庫，用一個字典來儲存所有 session 的歷史紀錄
# 在真實世界中，這會是 Redis, PostgreSQL, 或其他資料庫
SESSIONS = {}

# 這是一個虛構的函式，代表了呼叫 Claude 或 Gemini 的邏輯
def call_llm(messages):
    # ... 根據 messages 呼叫 Claude/Gemini API ...
    # ... 回傳模型的回應 ...
    # 為了範例，我們假設它總是要求呼叫工具
    return {"role": "assistant", "content": [{"type": "tool_use", "name": "some_tool", "input": {}}]}

# 這也是一個虛構的函式，代表執行工具的邏輯
def execute_tool(tool_call):
    # ... 根據 tool_call 的內容執行對應的工具 ...
    return {"type": "tool_result", "tool_name": tool_call["name"], "output": "some result"}


app = Flask(__name__)

# 1. 啟動 (Launch)
@app.route("/sessions", methods=["POST"])
def launch_session():
    session_id = str(uuid.uuid4())
    user_input = request.json.get("input")

    # 建立第一筆歷史紀錄
    history = [{"role": "user", "content": user_input}]

    # 第一次呼叫 LLM
    assistant_response = call_llm(history)
    history.append(assistant_response)

    # 儲存 session
    SESSIONS[session_id] = history

    # Agent 在呼叫工具後「暫停」了
    return jsonify({"session_id": session_id, "status": "paused", "next_action": "execute_tool", "tool_call": assistant_response["content"][0]})

# 2. 恢復 (Resume)
@app.route("/sessions/<session_id>/resume", methods=["POST"])
def resume_session(session_id):
    # 取得外部事件的結果（例如工具執行的結果）
    event_result = request.json.get("result")

    # 讀取歷史紀錄
    history = SESSIONS.get(session_id)
    if not history:
        return "Session not found", 404

    # 將新事件的結果加入歷史
    history.append(event_result)

    # 再次呼叫 LLM，讓它根據新的資訊決定下一步
    assistant_response = call_llm(history)
    history.append(assistant_response)

    # 更新並儲存 session
    SESSIONS[session_id] = history

    # Agent 再次「暫停」
    return jsonify({"session_id": session_id, "status": "paused", "next_action": "execute_tool", "tool_call": assistant_response["content"][0]})

# 3. 查詢狀態 (Query)
@app.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    history = SESSIONS.get(session_id)
    if not history:
        return "Session not found", 404
    return jsonify(history)

```
在這個範例中：
- `POST /sessions` 啟動了一個新的 Agent，進行了一次 LLM 呼叫，然後就**暫停**了，等待外部系統來執行工具。
- `POST /sessions/{id}/resume` 接收工具的執行結果，將其加入歷史，並再次呼叫 LLM，然後又**暫停**了。

整個 Agent 的運作被分解成了一系列無狀態、可預測的 API 呼叫。這讓我們的系統變得非常健壯、可擴展，並且易於與其他系統（包括人類）整合。

---

[下一章：Factor 7 - 透過工具與人類聯繫 (Contact Humans With Tools) →](factor-07-contact-humans-with-tools.md)
