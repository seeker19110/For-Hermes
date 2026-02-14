# Example Reports

Copy and adapt these for your use case.

---

## 1. Freelance Weekly

**Purpose:** Track income and utilization

```markdown
# Freelance Weekly

## Metadata
- **Created:** 2024-02-13
- **Status:** active

## Schedule
- **Frequency:** weekly
- **Time:** 09:00
- **Day:** Monday

## Metrics

| Metric | Type | Input | Description |
|--------|------|-------|-------------|
| revenue | currency | prompt | Total invoiced |
| hours | number | prompt | Hours worked |
| clients | number | prompt | Active clients |
| pending | currency | prompt | Unpaid invoices |
| rate | calculated | revenue/hours | Effective rate |

## Format
- **Primary:** chat
- **Secondary:** pdf (monthly)

## Delivery
- **Channel:** telegram

## Alerts

| Metric | Condition | Level |
|--------|-----------|-------|
| revenue | < 2500 | high |
| pending | > 5000 | medium |

## Data Prompt
"Weekly freelance update: revenue, hours worked, active clients, pending invoices?"
```

**Sample output:**
```
📊 Freelance Weekly — Feb 12-18

• Revenue: $3,400 (↑8%)
• Hours: 34h
• Rate: $100/hr
• Clients: 4 active
• Pending: $2,100

✅ All metrics healthy
```

---

## 2. Daily Health Check

**Purpose:** Quick daily tracking

```markdown
# Daily Health

## Metadata
- **Created:** 2024-02-13
- **Status:** active

## Schedule
- **Frequency:** daily
- **Time:** 21:00

## Metrics

| Metric | Type | Input |
|--------|------|-------|
| weight | number | prompt |
| sleep | number | prompt |
| exercise | boolean | prompt |
| mood | number | prompt |

## Format
- **Primary:** chat

## Delivery
- **Channel:** telegram

## Data Prompt
"Evening check-in: weight, hours slept last night, exercise today (y/n), mood (1-5)?"
```

**Sample output:**
```
✅ Health logged — Feb 18

Weight: 81.2kg (↓0.3)
Sleep: 7.5h
Exercise: ✓
Mood: 4/5

Streak: 12 days logged
```

---

## 3. Monthly Business Review

**Purpose:** Comprehensive monthly summary

```markdown
# Monthly Business

## Metadata
- **Created:** 2024-02-13
- **Status:** active

## Schedule
- **Frequency:** monthly
- **Time:** 10:00
- **Day:** 1

## Metrics

| Metric | Type | Input |
|--------|------|-------|
| revenue | currency | api:stripe |
| expenses | currency | manual |
| new_clients | number | manual |
| churn | number | manual |
| nps | number | manual |

## Format
- **Primary:** pdf

## Delivery
- **Channel:** telegram
- **Secondary:** file (archive)

## Data Prompt
"Month-end review: total expenses, new clients, churned clients, NPS score?"
```

---

## 4. Project Progress

**Purpose:** Track side project momentum

```markdown
# Project: MyApp

## Metadata
- **Created:** 2024-02-13
- **Status:** active

## Schedule
- **Frequency:** weekly
- **Time:** 18:00
- **Day:** Sunday

## Metrics

| Metric | Type | Input |
|--------|------|-------|
| hours | number | prompt |
| tasks_done | number | prompt |
| tasks_left | number | prompt |
| blockers | text | prompt |
| progress | calculated | tasks_done/(tasks_done+tasks_left) |

## Format
- **Primary:** chat

## Delivery
- **Channel:** telegram

## Alerts

| Metric | Condition | Level |
|--------|-----------|-------|
| hours | < 3 | low |
| blockers | != "" | medium |

## Data Prompt
"Project check-in: hours this week, tasks completed, tasks remaining, any blockers?"
```

---

## 5. Daily Standup (Team)

**Purpose:** Async standup replacement

```markdown
# Daily Standup

## Schedule
- **Frequency:** daily
- **Time:** 09:30

## Metrics

| Metric | Type | Input |
|--------|------|-------|
| yesterday | text | prompt |
| today | text | prompt |
| blockers | text | prompt |

## Format
- **Primary:** chat

## Delivery
- **Channel:** telegram

## Data Prompt
"Standup time!
• What did you finish yesterday?
• What's the plan for today?
• Any blockers?"
```

---

## 6. Quarterly OKRs

**Purpose:** Track objectives and key results

```markdown
# Q1 OKRs

## Schedule
- **Frequency:** weekly
- **Time:** 09:00
- **Day:** Monday
- **Full review:** quarterly

## Metrics

| Metric | Type | Input | Target |
|--------|------|-------|--------|
| revenue | currency | api | $50,000 |
| users | number | api | 1,000 |
| nps | number | manual | 50 |
| features | number | manual | 5 |

## Format
- **Quick:** chat (weekly)
- **Full:** pdf (quarterly)

## Delivery
- **Channel:** telegram

## Alerts

| Metric | Condition | Level |
|--------|-----------|-------|
| * | < 50% of target at midpoint | high |
```

---

## Creating Your Own

1. Pick closest example
2. Modify metrics for your needs
3. Set schedule that works for you
4. Choose format (chat for quick, PDF for formal)
5. Test for one cycle, then adjust
