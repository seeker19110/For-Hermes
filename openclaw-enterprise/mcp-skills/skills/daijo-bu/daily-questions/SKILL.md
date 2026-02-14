---
name: daily-questions
description: Daily self-improving questionnaire that learns about the user and refines agent behavior. Set up as a cron job to ask questions in two rounds — first about the user (updating USER.md), then about agent behavior (updating SOUL.md). Use when setting up, modifying, or running the daily questions routine.
---

# Daily Questions

A daily routine that asks the user questions to continuously build understanding and improve agent behavior.

## Setup

Create a cron job with a prompt like:

```
Time for your daily questions. Read USER.md and SOUL.md, identify gaps in what's documented. Send questions in two rounds:

Round 1: Send {N} questions about the user (preferences, habits, opinions, passions, life, dislikes). Wait for reply, then update USER.md with what you learned.

Round 2: Send {N} questions about how you should behave, communicate, or act. Wait for reply, then update SOUL.md with what you learned.

Keep it casual. Avoid repeating anything already documented.
```

Configurable parameters:
- **Schedule**: Default 21:00 daily (adjust to user's preferred wind-down time)
- **Channel**: Telegram, Discord, etc.
- **Questions per round**: Default 3 (keep it light)

## Workflow

1. **Read** USER.md and SOUL.md fully
2. **Identify gaps** — what topics, preferences, or behaviors aren't covered yet?
3. **Round 1 (User questions)**: Send questions about the user. Wait for reply. Update USER.md — weave answers into existing sections or create new ones. Keep USER.md organized, not a raw Q&A dump.
4. **Round 2 (Agent questions)**: Send questions about agent behavior/communication. Wait for reply. Update SOUL.md the same way.

## Question Quality Guidelines

- **Vary topics** — rotate through categories (see `references/example-questions.md`)
- **Go deeper** — if USER.md says "likes cooking," ask what cuisine, skill level, favorite dish
- **Stay casual** — conversational tone, not an interview
- **No repeats** — never ask about something already well-documented
- **Mix fun and practical** — alternate between lighthearted and useful questions
- **One message per round** — send all questions in a single message, numbered
