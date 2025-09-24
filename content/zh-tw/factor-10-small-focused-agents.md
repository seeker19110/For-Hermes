[← 返回 README.zh-tw.md](../../README.zh-tw.md) | [← 上一章：Factor 9](factor-09-compact-errors.md)

## Factor 10：專注、小型的 Agent (Small, Focused Agents)

**原則：與其打造一個試圖包山包海的巨型 Agent，不如打造一群各自專精於單一領域的小型 Agent。**

這個原則，其實就是軟體工程界喊了多年的「微服務 (Microservices) vs. 單體式應用 (Monolith)」架構之爭，在 Agent 設計上的體現。

![1a0-small-focused-agents](../../img/1a0-small-focused-agents.png)

為什麼這很重要？因為 LLM 的一大限制是：**情境視窗越長，模型就越容易迷失方向、忘記初衷**。一個需要上百個步驟才能完成的複雜任務，會產生一個極其冗長的對話歷史。在這種情況下，即使是今天最強大的模型，其表現也會急遽下降。

透過將大型任務拆解，讓每個 Agent 只專注在 3-10 個步驟內就能完成的子任務，我們能有效地將情境視窗維持在一個可控的範圍內，從而確保 LLM 的決策品質。

### 範例：一家由多個 Agent 組成的旅行社

與其打造一個什麼都會的「萬能旅遊 Agent」，不如設計一個團隊：

- **機票 Agent (`FlightBookingAgent`)**
  - **職責**：只負責處理跟機票有關的一切。
  - **工具**：`search_flights`, `book_flight`, `check_booking_status`。
  - **知識**：對航空公司代碼、機場縮寫、艙等瞭若指掌。

- **飯店 Agent (`HotelBookingAgent`)**
  - **職責**：只負責訂房。
  - **工具**：`search_hotels`, `book_room`, `get_hotel_reviews`。
  - **知識**：懂房型、飯店設施、訂房網站的術語。

- **行程規劃 Agent (`ItineraryPlanningAgent`)**
  - **職責**：擔任總指揮。負責與使用者溝通、理解整體需求，並將訂機票、訂飯店的任務「委派」給對應的專家 Agent。
  - **工具**：`call_flight_agent`, `call_hotel_agent`。
  - **知識**：擅長規劃時間、安排景點、估算預算。

這種設計的好處是，當 `FlightBookingAgent` 在工作時，它的情境視窗裡完全不會被飯店或行程的資訊所干擾，讓它可以百分之百專注在自己的任務上。

---

### 動手玩玩看：為不同 Agent 設計專屬提示

這個原則的精髓體現在你為不同 Agent 設計的「系統提示 (System Prompt)」和「工具集 (Tools)」上。

#### 1. 專家 Agent 的提示 (以 `FlightBookingAgent` 為例)

它的系統提示會非常專注且詳細，充滿了該領域的專業知識。

```
你是一個專業的機票預訂專家。你的任務是協助使用者找到並預訂最適合的機票。
你必須嚴格遵守以下規則：
1. 在搜尋前，必須問清楚出發地、目的地、出發日期、回程日期、以及乘客人數。
2. 絕對不能自己假設機場代碼，不確定的時候要反問使用者。
3. 搜尋到結果後，要條列式地呈現至少三個選項，包含航空公司、價格和轉機次數。
```

#### 2. 總監 Agent 的提示 (以 `ItineraryPlanningAgent` 為例)

它的系統提示則更偏向於理解使用者意圖和任務拆解。

```
你是一個首席旅遊規劃師。你的任務是理解使用者的整體旅遊需求，並協調底下的專家團隊來完成任務。
- 當使用者提到跟「機票」有關的需求時，你應該呼叫 `call_flight_agent` 工具。
- 當使用者提到跟「住宿」或「飯店」有關的需求時，你應該呼叫 `call_hotel_agent` 工具。
- 你自己的任務是將所有資訊彙整，產生一份完整的行程表。
```

#### 3. 總監 Agent 的工具定義 (Claude / Gemini 適用)

`ItineraryPlanningAgent` 的工具定義，就是用來呼叫其他 Agent 的。

```json
{
    "tools": [
        {
            "name": "call_flight_agent",
            "description": "當需要搜尋或預訂機票時，呼叫此工具來啟動機票專家 Agent。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_request": {
                        "type": "string",
                        "description": "使用者關於機票的原始請求，例如：'幫我找下週去東京的機票'"
                    }
                },
                "required": ["user_request"]
            }
        },
        {
            "name": "call_hotel_agent",
            "description": "當需要搜尋或預訂飯店時，呼叫此工具來啟動飯店專家 Agent。",
            "input_schema": { ... }
        }
    ]
}
```
當 `ItineraryPlanningAgent` 呼叫 `call_flight_agent` 時，你的應用程式就會知道，該啟動一個新的、獨立的 `FlightBookingAgent` 工作流程了。

這種「化整為零」的策略，是建構複雜、可靠、且可維護的 Agent 系統的關鍵。

---

[下一章：Factor 11 - 從任何地方觸發 (Trigger From Anywhere) →](factor-11-trigger-from-anywhere.md)
