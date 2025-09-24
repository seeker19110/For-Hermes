[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 7](factor-07-contact-humans-with-tools.md)

## Factor 8：掌握你的控制流程 (Own Your Control Flow)

**原則：不要被「Agent 迴圈」給綁架了。你應該要能完全掌握 LLM 呼叫之後的程式碼流程。**

![180-control-flow](../../img/180-control-flow.png)

一個最天真的 Agent 實作，可能長得像這樣：
```python
while True:
  # 1. 呼叫 LLM
  next_step = call_llm(history)

  # 2. 如果 LLM 說結束了，就跳出迴圈
  if next_step.intent == "done":
    break

  # 3. 盲目地執行 LLM 給的工具
  result = execute_tool(next_step)

  # 4. 把結果加回歷史
  history.append(result)
```
這個簡單的迴圈，在很多情況下都很有用。但當你需要建構更複雜、更可靠的系統時，你會發現它完全不夠用。

「掌握你的控制流程」意味著，在 LLM 做出決策（也就是回傳一個工具呼叫的 JSON）**之後**，你的程式碼要能根據這個決策的「類型」，來決定下一步的流程。

- **這個工具需要人類批准嗎？** -> 那就應該**跳出 (break)** 迴圈，去發送通知並等待 webhook 回應。
- **這個工具只是一個簡單的資料查詢嗎？** -> 那就應該同步執行它，把結果加回歷史，然後**繼續 (continue)** 迴圈，立刻再問 LLM 下一步是什麼。
- **這個工具的執行需要很長的時間嗎？** -> 那就應該把它丟到一個背景任務佇列中，然後**跳出 (break)** 迴圈。

### 範例：一個更聰明的 Agent 迴圈

讓我們看看一個更強大的 Agent 迴圈會是什麼樣子。

```python
def handle_next_step(thread):
  # 這裡不一定需要一個 while True 迴圈，
  # 每次的執行都可以是一個獨立的、無狀態的函式呼叫。
  # 為了說明，我們還是用迴圈來表示。

  # 1. 根據目前的歷史，決定下一步
  next_step = determine_next_step(thread.history)
  thread.history.append(next_step) # 先把「意圖」記錄下來

  # 2. 根據 LLM 的意圖，決定控制流程
  if next_step.intent == 'request_clarification':
      # 意圖：需要跟使用者確認更多資訊
      # 流程：跳出迴圈，等待人類回應
      send_message_to_human(next_step.question)
      save_thread_to_db(thread)
      return # Break

  elif next_step.intent == 'fetch_open_issues':
      # 意圖：查詢一個內部 API (速度很快)
      # 流程：同步執行，將結果加回歷史，並立刻進行下一步
      issues = linear_client.issues()
      thread.history.append({ "type": "tool_result", "data": issues })
      # 再次呼叫 handle_next_step 來進行下一次的 LLM 決策
      return handle_next_step(thread) # Continue

  elif next_step.intent == 'create_issue':
      # 意圖：執行一個高風險操作
      # 流程：跳出迴圈，請求人類批准
      request_human_approval(next_step.details)
      save_thread_to_db(thread)
      return # Break
```

這個模式讓你能夠彈性地中斷和恢復你的 Agent 流程，打造出更自然、更可靠的工作流。這也正是 Factor 5 (統一狀態) 和 Factor 6 (啟動/暫停/恢復) 帶來的巨大好處。

---

### 動手玩玩看：在我們的 API 中加入控制流程

這個原則同樣是關於應用程式架構的。讓我們來擴充在 Factor 6 中寫的 Flask API 範例。

我們來修改 `/resume` 這個端點。原本的實作很天真，就是盲目地執行工具。現在我們讓它變得更聰明，能夠根據 LLM 的「意圖」(tool_name) 來決定不同的流程。

```python
# ... (其他 Flask 程式碼和虛構函式與 Factor 6 相同) ...

# 2. 恢復 (Resume) - 智慧版
@app.route("/sessions/<session_id>/resume", methods=["POST"])
def resume_session(session_id):
    event_result = request.json.get("result")
    history = SESSIONS.get(session_id)
    if not history:
        return "Session not found", 404

    history.append(event_result)

    # 呼叫 LLM 取得下一步的意圖
    next_step = call_llm(history) # 假設 call_llm 回傳 {"role": "assistant", "content": [{"type": "tool_use", "name": "...", ...}]}
    history.append(next_step)

    tool_name = next_step["content"][0]["name"]

    # === 核心控制流程 ===
    if tool_name == "search_internal_kb":
        # 這是一個同步、低風險的工具
        # 我們可以直接執行它，並把結果加回歷史，然後立刻進行下一步
        tool_result = execute_tool(next_step["content"][0])
        history.append(tool_result)

        # 再次呼叫 LLM 進行下一次決策
        final_step = call_llm(history)
        history.append(final_step)

        # 更新 session 狀態
        SESSIONS[session_id] = history
        return jsonify({"session_id": session_id, "status": "paused", "response": final_step})

    elif tool_name == "request_human_approval":
        # 這是一個需要人類介入的非同步工具
        # 我們只要儲存好狀態，然後就結束這次的請求，等待 webhook 回應
        SESSIONS[session_id] = history
        return jsonify({"session_id": session_id, "status": "paused_waiting_for_human", "question": next_step["content"][0]["input"]["question"]})

    else:
        # 其他所有工具，我們都先假設它們是非同步的
        # 先儲存狀態，然後回傳，等待外部 worker 來處理
        SESSIONS[session_id] = history
        return jsonify({"session_id": session_id, "status": "paused", "next_action": "execute_tool", "tool_call": next_step["content"][0]})

```
透過在你的核心應用程式中加入這樣的 `if/elif/else` 判斷，你就從 LLM 手中奪回了「控制流程」的主導權。LLM 依然負責動腦，但你的程式碼才是老大，決定了事情實際該如何被執行。

---

[下一章：Factor 9 - 精簡化錯誤 (Compact Errors) →](factor-09-compact-errors.md)
