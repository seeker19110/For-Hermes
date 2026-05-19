# 12-Factor Agents - 构建可靠 LLM 应用的原则

<div align="center">
<a href="https://www.apache.org/licenses/LICENSE-2.0">
        <img src="https://img.shields.io/badge/代码-Apache%202.0-blue.svg" alt="代码许可证: Apache 2.0"></a>
<a href="https://creativecommons.org/licenses/by-sa/4.0/">
        <img src="https://img.shields.io/badge/内容-CC%20BY--SA%204.0-lightgrey.svg" alt="内容许可证: CC BY-SA 4.0"></a>
<a href="https://humanlayer.dev/discord">
    <img src="https://img.shields.io/badge/chat-discord-5865F2" alt="Discord 服务器"></a>
<a href="https://www.youtube.com/watch?v=8kMaTybvDUw">
    <img src="https://img.shields.io/badge/aidotengineer-会议演讲_(17分钟)-white" alt="YouTube 深度解析"></a>
<a href="https://www.youtube.com/watch?v=yxJDyQ8v6P0">
    <img src="https://img.shields.io/badge/youtube-深度解析-crimson" alt="YouTube 深度解析"></a>

</div>

<p></p>

*致敬 [12 Factor Apps](https://12factor.net/)。本项目源码公开于 https://github.com/humanlayer/12-factor-agents，欢迎反馈与贡献。让我们共同探索！*

> [!TIP]
> 错过了 AI Engineer World's Fair？[点此观看演讲回放](https://www.youtube.com/watch?v=8kMaTybvDUw)
>
> 想了解上下文工程？[直接跳到第 3 条原则](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)
>
> 想为 `npx/uvx create-12-factor-agent` 做贡献？[查看讨论帖](https://github.com/humanlayer/12-factor-agents/discussions/61)


<img referrerpolicy="no-referrer-when-downgrade" src="https://static.scarf.sh/a.png?x-pxid=2acad99a-c2d9-48df-86f5-9ca8061b7bf9" />

<a href="#visual-nav"><img width="907" alt="Screenshot 2025-04-03 at 2 49 07 PM" src="https://github.com/user-attachments/assets/23286ad8-7bef-4902-b371-88ff6a22e998" /></a>


你好，我是 Dex。我[折腾](https://youtu.be/8bIHcttkOTE) [AI 智能体](https://theouterloop.substack.com)已经[有一段时间了](https://humanlayer.dev)。

**我尝试过所有主流的智能体框架**，从开箱即用的 crew/langchain，到号称"极简主义"的 smolagents，再到"生产级"的 langraph、griptape 等。

**我与很多真正厉害的创始人深入交流过**，其中不乏 YC 在孵的项目，他们都在用 AI 做出令人印象深刻的东西。而大多数人都选择自己搭建技术栈，我很少在面向客户的生产级智能体中看到框架的身影。

**令我惊讶的是**，市面上那些以"AI 智能体"为卖点的产品，其实并没有多少真正的"智能"。很多不过是以确定性代码为主，只在恰到好处的节点插入 LLM 调用，让体验魔法般地提升。

真正优秀的智能体，并不遵循["给个 prompt，配上一堆工具，循环到完成目标"](https://www.anthropic.com/engineering/building-effective-agents#agents)这种模式，它们的核心其实是软件工程。

于是，我开始思考：

> ### **我们能用哪些原则，来构建真正足以面向生产客户的 LLM 驱动软件？**

欢迎来到 12-factor agents。正如芝加哥每任市长都会把那句话挂在机场里，我们很高兴你在这里。

*特别感谢 [@iantbutler01](https://github.com/iantbutler01)、[@tnm](https://github.com/tnm)、[@hellovai](https://www.github.com/hellovai)、[@stantonk](https://www.github.com/stantonk)、[@balanceiskey](https://www.github.com/balanceiskey)、[@AdjectiveAllison](https://www.github.com/AdjectiveAllison)、[@pfbyjy](https://www.github.com/pfbyjy)、[@a-churchill](https://www.github.com/a-churchill)，以及 SF MLOps 社区对本指南的早期反馈。*

## 简短版本：12 条原则

即使 LLMs [持续以指数级速度变得更强大](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-10-small-focused-agents.md#what-if-llms-get-smarter)，也有一些核心工程技术能让 LLM 驱动的软件更可靠、更易扩展、更易维护。

- [我们如何走到今天：软件简史](https://github.com/humanlayer/12-factor-agents/blob/main/content/brief-history-of-software.md)
- [原则 1：自然语言转工具调用](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-01-natural-language-to-tool-calls.md)
- [原则 2：掌控你的 Prompt](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-02-own-your-prompts.md)
- [原则 3：掌控你的上下文窗口](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)
- [原则 4：工具调用不过是结构化输出](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-04-tools-are-structured-outputs.md)
- [原则 5：统一执行状态与业务状态](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md)
- [原则 6：用简单 API 实现启动/暂停/恢复](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md)
- [原则 7：通过工具调用联系人类](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md)
- [原则 8：掌控你的控制流](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md)
- [原则 9：将错误压缩进上下文窗口](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md)
- [原则 10：小而专注的智能体](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-10-small-focused-agents.md)
- [原则 11：随处触发，在用户所在的地方服务他们](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-11-trigger-from-anywhere.md)
- [原则 12：让你的智能体成为无状态的归约器](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-12-stateless-reducer.md)

### 可视化导航 {#visual-nav}

|    |    |    |
|----|----|-----|
|[![原则 1](https://github.com/humanlayer/12-factor-agents/blob/main/img/110-natural-language-tool-calls.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-01-natural-language-to-tool-calls.md) | [![原则 2](https://github.com/humanlayer/12-factor-agents/blob/main/img/120-own-your-prompts.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-02-own-your-prompts.md) | [![原则 3](https://github.com/humanlayer/12-factor-agents/blob/main/img/130-own-your-context-building.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md) |
|[![原则 4](https://github.com/humanlayer/12-factor-agents/blob/main/img/140-tools-are-just-structured-outputs.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-04-tools-are-structured-outputs.md) | [![原则 5](https://github.com/humanlayer/12-factor-agents/blob/main/img/150-unify-state.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md) | [![原则 6](https://github.com/humanlayer/12-factor-agents/blob/main/img/160-pause-resume-with-simple-apis.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md) |
| [![原则 7](https://github.com/humanlayer/12-factor-agents/blob/main/img/170-contact-humans-with-tools.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md) | [![原则 8](https://github.com/humanlayer/12-factor-agents/blob/main/img/180-control-flow.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md) | [![原则 9](https://github.com/humanlayer/12-factor-agents/blob/main/img/190-factor-9-errors-static.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md) |
| [![原则 10](https://github.com/humanlayer/12-factor-agents/blob/main/img/1a0-small-focused-agents.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-10-small-focused-agents.md) | [![原则 11](https://github.com/humanlayer/12-factor-agents/blob/main/img/1b0-trigger-from-anywhere.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-11-trigger-from-anywhere.md) | [![原则 12](https://github.com/humanlayer/12-factor-agents/blob/main/img/1c0-stateless-reducer.png)](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-12-stateless-reducer.md) |

## 我们如何走到今天

想深入了解我的智能体探索历程及本指南的背景，请查阅[软件简史](https://github.com/humanlayer/12-factor-agents/blob/main/content/brief-history-of-software.md)，这里是简要摘要：

### 智能体的承诺

我们将大量讨论有向图（DG）及其无环版本 DAG。首先，软件本身就是一张有向图——这也是我们过去习惯用流程图来表示程序的原因。

![010-software-dag](https://github.com/humanlayer/12-factor-agents/blob/main/img/010-software-dag.png)

### 从代码到 DAG

大约二十年前，DAG 编排器开始流行，例如经典的 [Airflow](https://airflow.apache.org/)、[Prefect](https://www.prefect.io/) 以及更新的 [Dagster](https://dagster.io/)、[Inngest](https://www.inngest.com/)、[Windmill](https://www.windmill.dev/)。它们沿用了同样的图模式，并额外提供了可观测性、模块化、重试、管理等特性。

![015-dag-orchestrators](https://github.com/humanlayer/12-factor-agents/blob/main/img/015-dag-orchestrators.png)

### 智能体的承诺（续）

[不只是我这么认为](https://youtu.be/Dc99-zTMyMg?si=bcT0hIwWij2mR-40&t=73)，我在了解智能体时最大的感受是：你可以把 DAG 扔掉了。不再需要工程师编写每一个步骤和边界情况，只需给智能体一个目标和一组状态转换：

![025-agent-dag](https://github.com/humanlayer/12-factor-agents/blob/main/img/025-agent-dag.png)

让 LLM 实时决策，自行找到执行路径：

![026-agent-dag-lines](https://github.com/humanlayer/12-factor-agents/blob/main/img/026-agent-dag-lines.png)

这里的承诺是：你写更少的代码，只需给 LLM 图的"边"，让它自己决定"节点"。可以从错误中恢复，可以写更少的代码，LLM 甚至可能找到你意想不到的新颖解法。

### 智能体即循环

我们后来发现，这种方式并不总是奏效。

深入一层——智能体本质上是一个包含三个步骤的循环：

1. LLM 决定工作流的下一步，输出结构化 JSON（"工具调用"）
2. 确定性代码执行工具调用
3. 结果附加到上下文窗口
4. 重复，直到下一步被判定为"完成"

```python
initial_event = {"message": "..."}
context = [initial_event]
while True:
  next_step = await llm.determine_next_step(context)
  context.append(next_step)

  if (next_step.intent === "done"):
    return next_step.final_answer

  result = await execute_step(next_step)
  context.append(result)
```

初始上下文仅是起始事件（可能是用户消息、定时任务触发、Webhook 等），我们请求 LLM 选择下一步工具，或判定任务已完成。

以下是一个多步骤示例：

[![027-agent-loop-animation](https://github.com/humanlayer/12-factor-agents/blob/main/img/027-agent-loop-animation.gif)](https://github.com/user-attachments/assets/3beb0966-fdb1-4c12-a47f-ed4e8240f8fd)

<details>
<summary><a href="https://github.com/humanlayer/12-factor-agents/blob/main/img/027-agent-loop-animation.gif">GIF 版本</a></summary>

![027-agent-loop-animation](https://github.com/humanlayer/12-factor-agents/blob/main/img/027-agent-loop-animation.gif)

</details>

## 为什么需要 12-factor agents？

归根结底，现有方式的效果并没有我们期待的那么好。

在构建 HumanLayer 的过程中，我与至少 100 位 SaaS 构建者（大多是技术型创始人）交流过，他们都希望让现有产品更具智能体特性。这段旅程通常是这样的：

1. 决定构建智能体
2. 产品设计、UX 规划、明确要解决的问题
3. 为了快速推进，选择 $某框架 然后开始构建
4. 达到 70-80% 的质量标准
5. 意识到 80% 对大多数面向客户的功能来说远远不够
6. 意识到突破 80% 需要对框架、Prompt、流程等进行逆向工程
7. 从头再来

<details>
<summary>几点免责声明</summary>

**免责声明**：我不确定在哪里说这话最合适，但这里看起来不错：**这绝无任何针对那些框架或在其上工作的聪明人的意思**。这些框架成就了令人惊叹的事情，加速了整个 AI 生态系统的发展。

我希望本文的一个成果是：智能体框架的构建者能从我和他人的经历中学习，让框架变得更好——尤其是对那些既想快速行动又需要深度控制的构建者。

**免责声明 2**：我不打算谈 MCP，相信你能想象它如何融入这里的体系。

**免责声明 3**：我主要使用 TypeScript，[原因在此](https://www.linkedin.com/posts/dexterihorthy_llms-typescript-aiagents-activity-7290858296679313408-Lh9e)，但这些原则同样适用于 Python 或任何你喜欢的语言。

好了，继续正题……

</details>

### 优秀 LLM 应用的设计模式

在深入研究数百个 AI 库、与数十位创始人合作之后，我得出了如下判断：

1. 有一些核心特质让智能体真正出色
2. 全押在某个框架上并进行本质上是全面重写的构建，可能适得其反
3. 有一些核心原则让智能体出色，如果你引入框架，你会得到其中大部分/全部
4. **但是**，我见过的让构建者最快将高质量 AI 软件交到客户手中的方式，是从智能体构建中提取小而模块化的概念，并将其融入现有产品
5. 这些模块化概念大多数技术熟练的软件工程师都能理解和应用，即使他们没有 AI 背景

> #### 让构建者最快将优秀 AI 软件交到客户手中的方式，是从智能体构建中提取小而模块化的概念，并将其融入现有产品

## 12 条原则（再次列出）

- [我们如何走到今天：软件简史](https://github.com/humanlayer/12-factor-agents/blob/main/content/brief-history-of-software.md)
- [原则 1：自然语言转工具调用](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-01-natural-language-to-tool-calls.md)
- [原则 2：掌控你的 Prompt](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-02-own-your-prompts.md)
- [原则 3：掌控你的上下文窗口](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)
- [原则 4：工具调用不过是结构化输出](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-04-tools-are-structured-outputs.md)
- [原则 5：统一执行状态与业务状态](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md)
- [原则 6：用简单 API 实现启动/暂停/恢复](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md)
- [原则 7：通过工具调用联系人类](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md)
- [原则 8：掌控你的控制流](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md)
- [原则 9：将错误压缩进上下文窗口](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md)
- [原则 10：小而专注的智能体](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-10-small-focused-agents.md)
- [原则 11：随处触发，在用户所在的地方服务他们](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-11-trigger-from-anywhere.md)
- [原则 12：让你的智能体成为无状态的归约器](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-12-stateless-reducer.md)

## 荣誉提名 / 其他建议

- [原则 13：预取所有可能需要的上下文](https://github.com/humanlayer/12-factor-agents/blob/main/content/appendix-13-pre-fetch.md)

## 相关资源

- 在[此处](https://github.com/humanlayer/12-factor-agents)为本指南做贡献
- [我在 2025 年 3 月的 Tool Use 播客上谈到了很多相关内容](https://youtu.be/8bIHcttkOTE)
- 我在 [The Outer Loop](https://theouterloop.substack.com) 上撰写关于这些话题的文章
- 我与 [@hellovai](https://github.com/hellovai) 合作开展[最大化 LLM 性能的网络研讨会](https://github.com/hellovai/ai-that-works/tree/main)
- 我们在 [got-agents/agents](https://github.com/got-agents/agents) 下用这套方法构建开源智能体
- 我们忽视了自己的建议，构建了一个[在 Kubernetes 上运行分布式智能体的框架](https://github.com/humanlayer/kubechain)
- 本指南中引用的其他链接：
  - [12 Factor Apps](https://12factor.net)
  - [Building Effective Agents（Anthropic）](https://www.anthropic.com/engineering/building-effective-agents#agents)
  - [Prompts are Functions](https://thedataexchange.media/baml-revolution-in-ai-engineering/)
  - [Library patterns: Why frameworks are evil](https://tomasp.net/blog/2015/library-frameworks/)
  - [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
  - [Mailcrew Agent](https://github.com/dexhorthy/mailcrew)
  - [Mailcrew Demo Video](https://www.youtube.com/watch?v=f_cKnoPC_Oo)
  - [Chainlit Demo](https://x.com/chainlit_io/status/1858613325921480922)
  - [TypeScript for LLMs](https://www.linkedin.com/posts/dexterihorthy_llms-typescript-aiagents-activity-7290858296679313408-Lh9e)
  - [Schema Aligned Parsing](https://www.boundaryml.com/blog/schema-aligned-parsing)
  - [Function Calling vs Structured Outputs vs JSON Mode](https://www.vellum.ai/blog/when-should-i-use-function-calling-structured-outputs-or-json-mode)
  - [BAML on GitHub](https://github.com/boundaryml/baml)
  - [OpenAI JSON vs Function Calling](https://docs.llamaindex.ai/en/stable/examples/llm/openai_json_vs_function_calling/)
  - [Outer Loop Agents](https://theouterloop.substack.com/p/openais-realtime-api-is-a-step-towards)
  - [Airflow](https://airflow.apache.org/)
  - [Prefect](https://www.prefect.io/)
  - [Dagster](https://dagster.io/)
  - [Inngest](https://www.inngest.com/)
  - [Windmill](https://www.windmill.dev/)
  - [The AI Agent Index (MIT)](https://aiagentindex.mit.edu/)
  - [NotebookLM on Finding Model Capability Boundaries](https://open.substack.com/pub/swyx/p/notebooklm?selection=08e1187c-cfee-4c63-93c9-71216640a5f8)

## 贡献者

感谢所有为 12-factor agents 做出贡献的朋友们！

[<img src="https://avatars.githubusercontent.com/u/3730605?v=4&s=80" width="80px" alt="dexhorthy" />](https://github.com/dexhorthy) [<img src="https://avatars.githubusercontent.com/u/50557586?v=4&s=80" width="80px" alt="Sypherd" />](https://github.com/Sypherd) [<img src="https://avatars.githubusercontent.com/u/66259401?v=4&s=80" width="80px" alt="tofaramususa" />](https://github.com/tofaramususa) [<img src="https://avatars.githubusercontent.com/u/18105223?v=4&s=80" width="80px" alt="a-churchill" />](https://github.com/a-churchill) [<img src="https://avatars.githubusercontent.com/u/4084885?v=4&s=80" width="80px" alt="Elijas" />](https://github.com/Elijas) [<img src="https://avatars.githubusercontent.com/u/39267118?v=4&s=80" width="80px" alt="hugolmn" />](https://github.com/hugolmn) [<img src="https://avatars.githubusercontent.com/u/1882972?v=4&s=80" width="80px" alt="jeremypeters" />](https://github.com/jeremypeters)

[<img src="https://avatars.githubusercontent.com/u/380402?v=4&s=80" width="80px" alt="kndl" />](https://github.com/kndl) [<img src="https://avatars.githubusercontent.com/u/16674643?v=4&s=80" width="80px" alt="maciejkos" />](https://github.com/maciejkos) [<img src="https://avatars.githubusercontent.com/u/85041180?v=4&s=80" width="80px" alt="pfbyjy" />](https://github.com/pfbyjy) [<img src="https://avatars.githubusercontent.com/u/36044389?v=4&s=80" width="80px" alt="0xRaduan" />](https://github.com/0xRaduan) [<img src="https://avatars.githubusercontent.com/u/7169731?v=4&s=80" width="80px" alt="zyuanlim" />](https://github.com/zyuanlim) [<img src="https://avatars.githubusercontent.com/u/15862501?v=4&s=80" width="80px" alt="lombardo-chcg" />](https://github.com/lombardo-chcg) [<img src="https://avatars.githubusercontent.com/u/160066852?v=4&s=80" width="80px" alt="sahanatvessel" />](https://github.com/sahanatvessel)

## 许可证

所有内容和图片使用 <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0 许可证</a>

代码使用 <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache 2.0 许可证</a>
