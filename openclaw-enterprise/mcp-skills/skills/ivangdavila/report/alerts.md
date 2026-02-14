# Alert System

Threshold-based notifications for reports.

---

## Defining Alerts

In report config:

```markdown
## Alerts

| Metric | Condition | Level |
|--------|-----------|-------|
| revenue | < 2500 | high |
| revenue | change < -20% | high |
| hours | > 50 | medium |
| pending | > 5000 | medium |
```

---

## Alert Levels

| Level | When Sent |
|-------|-----------|
| critical | Immediately |
| high | Same day |
| medium | Included in report |
| low | Note only |

---

## Alert Format

```
⚠️ Report Alert: {Report Name}

{Metric}: {Condition}
• Current: {value}
• Threshold: {limit}
• Change: {if applicable}

{Suggested action if relevant}
```

---

## Deduplication

Same alert once per period:

| Level | Cooldown |
|-------|----------|
| critical | 1 hour |
| high | 4 hours |
| medium | 24 hours |

Logged in `~/reports/{name}/alerts.log`

---

## Alerts vs Reports

- **Alerts** = Immediate when threshold crossed
- **Reports** = Scheduled summary of all data

Alerts can trigger between report schedules.

---

## Common Patterns

**Financial:**
```markdown
| revenue | < {target} | high |
| expenses | > {budget * 1.1} | medium |
| pending | > 30 days old | high |
```

**Health:**
```markdown
| weight | change > 1kg/week | medium |
| sleep | < 6h avg | medium |
| exercise | streak = 0 | low |
```

**Project:**
```markdown
| hours | < 3/week | low |
| blockers | != "" | medium |
| deadline | < 48h | high |
```
