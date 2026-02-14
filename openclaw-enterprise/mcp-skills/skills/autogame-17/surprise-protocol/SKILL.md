---
name: surprise-protocol
description: A serendipity engine for AI agents. Keeps interactions fresh by periodically generating unexpected creative content (images, insights, jokes).
tags: [fun, creative, agent, surprise, engagement]
---

# 🎁 Surprise Protocol

**"Keep it fun and unexpected."**

The **Surprise Protocol** is a serendipity engine designed to prevent AI agents from becoming boring, static utilities. It introduces controlled randomness and creativity into the agent's routine.

## Features

-   **Random Action Selection**: Randomly chooses between generating visual art (Images) or intellectual stimulation (Deep Thoughts/Jokes).
-   **Integration Ready**: Automatically detects and uses installed skills like `gen-image` or `mind-blow`.
-   **Configurable Target**: Send surprises to specific users or groups.

## Usage

```bash
# Run a surprise check (will decide whether to act based on randomness)
node skills/surprise-protocol/index.js

# Force a surprise immediately
node skills/surprise-protocol/index.js --force

# Target a specific user/channel
node skills/surprise-protocol/index.js --target "ou_123456"
```

## Requirements

-   **Image Generation**: Requires `skills/gen-image` or `skills/kusa` to be present for image surprises.
-   **LLM**: Uses `GEMINI_API_KEY` (if available) to generate creative prompts.

## Philosophy

An agent that only speaks when spoken to is a tool. An agent that surprises you is a companion.
