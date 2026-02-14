---
name: Report
description: Configure custom recurring reports with flexible schedules, data sources, and delivery formats.
---

## What This Skill Does

Set up **any number of reports** that run automatically at **any frequency** in **any format** you want.

Examples:
- Weekly freelance income summary → Telegram every Monday
- Daily health check-in → prompt + log
- Monthly project progress → PDF on the 1st
- Real-time alerts → when thresholds crossed

---

## Quick Reference

| Task | Load |
|------|------|
| Report configuration schema | `schema.md` |
| Output formats (chat, PDF, HTML, JSON) | `formats.md` |
| Delivery channels and scheduling | `delivery.md` |
| Data collection methods | `data-input.md` |
| Alert and threshold rules | `alerts.md` |
| Example reports | `examples.md` |

---

## Creating a Report

User says what they want to track. Agent gathers:

1. **Name** — Short identifier
2. **Metrics** — What data to include
3. **Schedule** — When to generate (daily, weekly, monthly, on-demand)
4. **Format** — How to present (chat message, PDF, HTML)
5. **Delivery** — Where to send (Telegram, file, email)
6. **Alerts** — Optional thresholds for notifications

Then creates config in `~/reports/{name}/config.md`.

---

## Report Storage

```
~/reports/
├── index.md                    # List of all reports
├── {name}/
│   ├── config.md               # Report configuration
│   ├── data.jsonl              # Historical data
│   ├── latest.json             # Most recent values
│   └── generated/              # Past reports (PDF, HTML)
```

---

## Scheduling Options

| Frequency | Cron Expression | Example |
|-----------|-----------------|---------|
| Daily | `0 9 * * *` | 9am every day |
| Weekly | `0 9 * * 1` | Monday 9am |
| Biweekly | `0 9 * * 1/2` | Every other Monday |
| Monthly | `0 9 1 * *` | 1st of month |
| Quarterly | `0 9 1 1,4,7,10 *` | Jan/Apr/Jul/Oct |
| On-demand | - | When user asks |

Multiple schedules per report allowed:
- Quick update: daily chat
- Full report: weekly PDF

---

## Data Input

Reports can pull data from:
- **Manual** — User provides values
- **Prompted** — Agent asks at scheduled time
- **API** — Automatic fetch (if credentials exist)
- **Calculated** — Derived from other metrics

See `data-input.md` for details.

---

## Format Options

| Format | Best For |
|--------|----------|
| Chat message | Quick updates, alerts |
| PDF | Formal reports, sharing |
| HTML | Detailed analysis, archival |
| JSON | Data export, integrations |

See `formats.md` for templates.

---

## Example Interaction

**Setup:**
```
User: "I want a weekly report of my consulting hours and revenue"
Agent: Creates ~/reports/consulting/config.md
       Schedules: Every Monday 9am
       Prompts: Sunday evening for data
```

**Weekly flow:**
```
Sunday 8pm — Agent: "Time for your consulting update. Hours? Revenue?"
User: "32 hours, $4,800"
Agent: "✓ Logged. Report generates tomorrow 9am."

Monday 9am — Agent sends:
📊 Consulting Report — Week 7
• Hours: 32h (↑4h vs last week)
• Revenue: $4,800 (↑$600)
• Effective rate: $150/hr
```

---

## Managing Reports

```
"List my reports" → Shows all configured reports
"Pause health report" → Stops generation temporarily
"Change consulting to biweekly" → Updates schedule
"Delete old-project report" → Removes config and data
"Run consulting report now" → Generates on-demand
```

---

### Active Reports
<!-- Auto-updated list of configured reports -->

### Delivery Preferences
<!-- Default formats and channels -->

### Schedule Overview
<!-- When each report runs -->
