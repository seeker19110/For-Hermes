---
name: reverse-prompt
description: Based on what I know about the user and their goals, suggest tasks I can do to get us closer to our missions. Use when the user wants proactive suggestions for tasks aligned with their objectives, or when they ask what I can do to help advance their goals.
---

# Reverse Prompt Skill

This skill generates proactive task suggestions based on user context and stated missions.

## Process

1. **Recall existing knowledge** — Search memory for:
   - User's stated goals and missions
   - Current projects
   - Past preferences and decisions
   - Recent activities and context

2. **Identify gaps** — What's missing or unclear:
   - Unknown mission details
   - Unstated priorities
   - Missing context

3. **Generate suggestions** — Based on knowledge level:

### If missions are known:
Suggest specific, actionable tasks that directly advance those goals:
- Automation opportunities
- Research tasks
- Monitoring setups
- Content creation
- Data organization

### If missions are unclear:
Ask clarifying questions:
- "What are you working on?"
- "What would 'powerful' look like for your use case?"
- "What's your domain? (business, coding, research, personal productivity)"

## Example Output

When missions are unknown:
> "I need context to suggest the right tasks. Quick options:
> 1. **Business/startup** — market monitoring, competitor tracking
> 2. **Coding/dev** — codebase management, CI/CD hooks
> 3. **Research** — web scraping, trend analysis
> 4. **Personal productivity** — calendar management, reminders
> What's your domain?"

When missions are known (e.g., "building a SaaS"):
> "Based on your SaaS goal, here are tasks I can handle:
> - Monitor Reddit/HN for micro-SaaS opportunities
> - Track competitor pricing changes
> - Automate weekly user feedback reports
> - Set up cron jobs for usage analytics"
