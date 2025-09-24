[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 11](factor-11-trigger-from-anywhere.md)

## Factor 12：將你的 Agent 當作一個無狀態的 Reducer (Stateless Reducer)

**原則：將你的整個 Agent 運作流程，想像成一個函數式程式設計中的「Reducer」或「Fold」操作。**

如果你對函數式程式設計 (Functional Programming) 不熟，別擔心，這個概念其實很簡單。

想像一下你要對一個數字列表 `[1, 2, 3, 4, 5]` 進行加總。一個 `reducer` 函式的運作方式如下：
- 初始狀態：`0`
- 第一步：`reducer(0, 1)` -> 回傳 `1`
- 第二步：`reducer(1, 2)` -> 回傳 `3`
- 第三步：`reducer(3, 3)` -> 回傳 `6`
- 第四步：`reducer(6, 4)` -> 回傳 `10`
- 第五步：`reducer(10, 5)` -> 回傳 `15`

這個 `reducer` 函式，只接收「**當前的狀態**」和「**下一個項目**」，然後回傳「**新的狀態**」。它本身是**無狀態的 (stateless)**，它不記得過去發生了什麼，所有的資訊都在傳給它的「當前狀態」裡。

---

**這跟我們的 Agent 架構，簡直一模一樣！**

![1c5-agent-foldl](../../img/1c5-agent-foldl.png)

讓我們來對應一下：
- **當前的狀態 (Accumulator)**：就是我們在 Factor 5 中定義的「**事件歷史紀錄 (Event History)**」。
- **下一個項目 (Item)**：就是一個「**新的外部事件**」（例如：使用者的訊息、工具的執行結果、Webhook 的請求）。
- **Reducer 函式**：就是我們的「**Agent 核心邏輯**」。

所以，我們的 Agent 運作流程可以被抽象成一個優雅的函式：

`new_history = agent_reducer(current_history, new_event)`

### 動手玩玩看：用 Reducer 函式來思考

讓我們把之前所有 Factor 的概念，濃縮到這個最終的模式中。

```python
# 這是我們 Agent 的核心，一個純粹、無狀態的函式
def agent_reducer(current_history, new_event):
    """
    接收當前的歷史紀錄和一個新事件，回傳包含 LLM 新決策的完整歷史紀錄。

    Args:
        current_history (list): 到目前為止的所有事件。
        new_event (dict): 剛剛發生的新事件。

    Returns:
        list: 包含了新事件和 LLM 新回應的完整歷史。
    """

    # 1. 將新事件加入歷史
    next_history = current_history + [new_event]

    # 2. 根據完整的歷史，呼叫 LLM 進行下一步決策
    #    這個 call_llm 函式內部可以是用 Claude 或 Gemini 的 API
    llm_decision = call_llm(next_history)

    # 3. 將 LLM 的決策也加入歷史
    final_history = next_history + [llm_decision]

    return final_history

# --- 在你的應用程式中如何使用它 ---

# 1. 一個新請求進來了 (Factor 11)
github_event = {"type": "github_comment", "user": "Jules", "text": "@bot help me"}
current_history = [] # 因為是新的 session，所以歷史是空的

# 2. 第一次呼叫 reducer
history_after_step_1 = agent_reducer(current_history, github_event)
# >> history_after_step_1 現在可能包含了一個 tool_use 事件

# 3. 你的應用程式根據 history_after_step_1 的最後一個事件去執行工具 (Factor 8)
#    ... 執行工具 ...
tool_result_event = {"type": "tool_result", "output": "..."}

# 4. 第二次呼叫 reducer
history_after_step_2 = agent_reducer(history_after_step_1, tool_result_event)

# ... 這個循環不斷重複 ...
```
這個 Reducer 模式，就是前面 11 個 Factor 的集大成者。它強迫我們：
- 將所有狀態統一管理 (Factor 5)
- 透過傳遞歷史來建構情境 (Factor 3)
- 將 LLM 的回應視為結構化資料 (Factor 4)
- 讓整個流程可以輕易地被外部事件觸發、暫停和恢復 (Factor 6, 7, 11)

### 總結

恭喜你！走完這 12 個原則，你已經學會了一套不依賴任何特定框架、健壯、可擴展、且完全在你自己掌控之下的 Agent 架構方法論。

這套方法的核心精神是「**回歸軟體工程的本質**」，將 LLM 視為一個強大的、但仍需被良好工程實踐所約束的「函式呼叫」。

希望這份指南對你的 Agent 開發之旅有所幫助！

---

[返回中文版 README](../../README.zh-tw.md)
