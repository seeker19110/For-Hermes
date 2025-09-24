# 12-Factor Agents - 寫給初學者的可靠 LLM 應用程式開發指南 (正體中文版)

<div align="center">
<a href="https://www.apache.org/licenses/LICENSE-2.0">
        <img src="https://img.shields.io/badge/Code-Apache%202.0-blue.svg" alt="Code License: Apache 2.0"></a>
<a href="https://creativecommons.org/licenses/by-sa/4.0/">
        <img src="https://img.shields.io/badge/Content-CC%20BY--SA%204.0-lightgrey.svg" alt="Content License: CC BY-SA 4.0"></a>
<a href="https://humanlayer.dev/discord">
    <img src="https://img.shields.io/badge/chat-discord-5865F2" alt="Discord Server"></a>
</div>

<p></p>

哈囉，你好！歡迎來到「12-Factor Agent」的中文世界。

本專案的原作者是 [Dex](https://github.com/dexhorthy)，他提出了 12 個關於建構可靠、可擴展、可維護的 LLM 應用程式的設計原則，深受軟體工程界的經典「[12 Factor Apps](https://12factor.net/zh_cn/)」所啟發。

這個 repo 的 `zh-tw` 版本，旨在將這些寶貴的原則，以更**適合初學者**、更**貼近台灣開發者習慣**的方式呈現。我們不僅會用正體中文來說明，更會加入使用 **Claude** 和 **Gemini** 等最新模型的**動手實作範例**，讓你從零開始，一步步學會如何打造高品質的 AI Agent。

## 學習路徑

我們建議你按照以下順序學習：

1.  **[AI Agent 入門指南：寫給完全初學者的第一堂課](./content/zh-tw/introduction-to-agents.md)**
    *   在開始之前，我們先用最簡單的方式搞懂什麼是 AI Agent。

2.  **The 12 Factors (12 個原則)**
    *   接下來，我們會逐一探索這 12 個核心原則。每個原則都會有概念說明和程式碼範例。

*   **[Factor 1：自然語言轉換為工具呼叫](./content/zh-tw/factor-01-natural-language-to-tool-calls.md)**
*   **[Factor 2：掌握你的提示](./content/zh-tw/factor-02-own-your-prompts.md)**
*   **[Factor 3：掌握你的情境視窗](./content/zh-tw/factor-03-own-your-context-window.md)**
*   **[Factor 4：工具即結構化輸出](./content/zh-tw/factor-04-tools-are-structured-outputs.md)**
*   **[Factor 5：統一執行狀態與業務狀態](./content/zh-tw/factor-05-unify-execution-state.md)**
*   **[Factor 6：透過簡單的 API 啟動/暫停/恢復](./content/zh-tw/factor-06-launch-pause-resume.md)**
*   **[Factor 7：透過工具與人類聯繫](./content/zh-tw/factor-07-contact-humans-with-tools.md)**
*   **[Factor 8：掌握你的控制流程](./content/zh-tw/factor-08-own-your-control-flow.md)**
*   **[Factor 9：精簡化錯誤](./content/zh-tw/factor-09-compact-errors.md)**
*   **[Factor 10：專注、小型的 Agent](./content/zh-tw/factor-10-small-focused-agents.md)**
*   **[Factor 11：從任何地方觸發](./content/zh-tw/factor-11-trigger-from-anywhere.md)**
*   **[Factor 12：將你的 Agent 當作一個無狀態的 Reducer](./content/zh-tw/factor-12-stateless-reducer.md)**

## 為什麼要關心這個？

你是否也曾滿腔熱血地想打造一個 AI Agent，卻發現：
- 隨便套用一個現成的 Agent 框架，效果不如預期？
- 想微調 Agent 的行為，卻不知從何下手？
- Agent 的表現時好時壞，非常不穩定？

這份指南就是為了解決這些問題而生。我們相信，與其追求一個能解決所有問題的萬能框架，不如回歸軟體工程的本質，掌握那些能讓你的 LLM 應用程式變得更可靠、更強大的核心原則。

準備好開始了嗎？讓我們一起動手，打造出真正能上線服務的 AI Agent 吧！
