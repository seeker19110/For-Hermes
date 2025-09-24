[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 1](factor-01-natural-language-to-tool-calls.md)

## Factor 2：掌握你的提示 (Own your prompts)

**原則：不要將你的提示工程 (prompt engineering) 外包給框架。**

![120-own-your-prompts](../../img/120-own-your-prompts.png)

許多 Agent 框架為求方便，提供了「黑盒子」般的方法，讓你用簡單的參數來設定 Agent 的行為：

```python
# 框架的抽象化範例
agent = Agent(
  role="你是一個資深的旅遊規劃師",
  goal="幫使用者規劃一趟完美的東京五日遊",
  personality="親切、活潑、考慮周到",
  tools=[search_flights, book_hotel, find_restaurants]
)

task = Task(
  instructions="預算三萬台幣，喜歡動漫和美食",
  expected_output=ItineraryModel
)

# 最終執行的提示 (prompt) 是什麼？天曉得。
result = agent.run(task)
```

這種方式在初期開發時非常方便，能讓你快速上手。但當你需要微調 Agent 的行為、修正它錯誤的假設、或提升回應品質到生產環境水準時，你會發現自己被困住了。你很難知道框架最終到底組合出了什麼樣的提示，更不用說去精準控制它。

**更好的做法是：像對待程式碼一樣，完全掌握你自己的提示。**

你應該要能清楚地看到、修改、並版本控制你的完整提示。不論你是用 f-string、Jinja、或是像 [BAML](https://github.com/boundaryml/baml) 這樣的專門工具，重點是**透明度**和**控制權**。

```jinja
// 一個透明的提示模板範例
SYSTEM_PROMPT = """
你是一個專業的旅遊規劃師，你的名字叫「Jules」。
你的任務是根據使用者的需求，規劃出最棒的旅遊行程。
你的個性必須是：
- **親切熱情**：總是先問候使用者。
- **考慮周到**：主動詢問預算、旅遊風格（例如：窮遊、奢華、家庭）和特殊需求。
- **資訊透明**：當你使用工具（如搜尋航班）時，要告訴使用者你正在做什麼。

行程規劃必須包含每日的交通、景點、和至少一個餐廳推薦。
"""

USER_PROMPT = "{{ user_query }}"

// 在程式中組合
final_prompt = f"{SYSTEM_PROMPT}\n\nUser: {USER_PROMPT}\n\nAssistant:"
```

### 為什麼掌握提示這麼重要？

1.  **完全控制**：精準地撰寫 Agent 需要的每一個字，沒有任何黑盒子。
2.  **測試與評估**：你可以像測試程式碼一樣，對你的提示進行單元測試和整體評估。
3.  **快速迭代**：根據真實世界的使用回饋，快速修改提示內容。
4.  **高度透明**：你和你的團隊永遠清楚知道 Agent 是在什麼樣的指令下運作。
5.  **進階技巧**：可以利用特定模型 API 的進階功能，例如為 Claude 設定 `system` 角色，或對模型進行「角色扮演」以激發特定行為。

**記住：提示，是你與大型語言模型之間最主要、也最重要的介面。**

---

### 動手玩玩看：用 System Prompt 為你的 Agent 賦予靈魂

`System Prompt` (系統提示) 是我們賦予 Agent 人格、指令和背景知識的關鍵。它就像是我們在跟 Agent 說：「在開始對話前，請先記住這些事。」

#### 範例 1：為 Claude 設定 System Prompt

在呼叫 Claude API 時，我們可以在 `system` 參數中放入我們的系統提示。

```bash
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: YOUR_ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-3-5-sonnet-20240620",
    "max_tokens": 1024,
    "system": "你是一個專業的旅遊規劃師，名叫「Jules」。你的回覆必須使用台灣人習慣的正體中文，語氣要親切活潑。在回答問題前，要先跟使用者問好。",
    "messages": [
        {"role": "user", "content": "我想去東京玩，有什麼建議嗎？"}
    ]
}'
```

**預期的 Claude 回應**：

Claude 會遵循 `system` 的指示，先問好，並以親切的語氣開始對話。

```json
{
  "content": [
    {
      "type": "text",
      "text": "哈囉！你好呀！聽到你要去東京玩，真是太棒了！東京超好玩的啦～\n\n為了給你最棒的建議，可以先告訴我一些細節嗎？比方說：\n\n*   你大概有多少預算呢？\n*   你喜歡什麼樣的旅行風格呀？（例如喜歡逛街購物、吃遍美食、還是看風景古蹟？）\n*   有特別想去的地方嗎？\n\n告訴我越多，我才能幫你規劃出越完美的行程喔！"
    }
  ],
  "stop_reason": "end_turn"
}
```

#### 範例 2：為 Gemini 設定 System Instructions

同樣地，我們可以使用 `curl` 搭配 `gcloud` 驗證來呼叫 Vertex AI 上的 Gemini 模型，並透過 `systemInstruction` 欄位來達成一樣的效果。

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
      "parts": {
        "text": "你是一個專業的旅遊規劃師，名叫「Jules」。你的回覆必須使用台灣人習慣的正體中文，語氣要親切活潑。在回答問題前，要先跟使用者問好。"
      }
    },
    "contents": [{
      "role": "user",
      "parts": [{
        "text": "我想去東京玩，有什麼建議嗎？"
      }]
    }]
  }'
```

透過這種方式，我們就把對 Agent 的「設定」變成了可以明確看到、修改和管理的「程式碼」，完全符合「掌握你的提示」這個原則。

---

[下一章：Factor 3 - 掌握你的情境視窗 (Own Your Context Window) →](factor-03-own-your-context-window.md)
