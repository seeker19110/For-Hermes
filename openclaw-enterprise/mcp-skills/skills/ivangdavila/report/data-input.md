# Data Input Methods

How data gets into reports.

---

## Manual

User provides data anytime:

```
"Revenue this week was $3,400"
"Update freelance: hours 34, clients 4"
"Log weight 81.2"
```

Agent parses, validates, stores.

---

## Prompted

Agent asks before report generates.

**Config:**
```markdown
## Data Prompt
"Weekly update: hours worked, revenue, active clients?"
```

**Flow:**
1. Prompt runs before report time (e.g., Sunday 8pm)
2. User responds with data
3. Data stored in `data.jsonl`
4. Report generates with fresh data (Monday 9am)

---

## API

Automatic fetch if credentials exist.

**Supported (with credentials):**
| Source | Key | Data |
|--------|-----|------|
| Stripe | `stripe_api_key` | Revenue, subs |
| GitHub | `github_token` | Commits, PRs |

**Config:**
```markdown
| Metric | Type | Input |
|--------|------|-------|
| revenue | currency | api:stripe |
```

**Fallback:** If API fails, prompt user instead.

---

## Calculated

Derived from other metrics:

```markdown
| Metric | Type | Input | Formula |
|--------|------|-------|---------|
| rate | calculated | revenue/hours | - |
| utilization | calculated | hours/40 | - |
| growth | calculated | (current-previous)/previous | - |
```

Calculated after base metrics collected.

---

## Storage

**data.jsonl** — Append-only history:
```json
{"ts": "2024-02-13T20:00:00Z", "revenue": 3400, "hours": 34}
{"ts": "2024-02-06T20:00:00Z", "revenue": 3150, "hours": 32}
```

**latest.json** — Current values with trends:
```json
{
  "updated": "2024-02-13T20:00:00Z",
  "metrics": {
    "revenue": {"value": 3400, "previous": 3150, "change": 0.08}
  }
}
```

---

## Validation

Before storing:
- Type matches (number, currency, etc.)
- Value reasonable (flag outliers)
- Required metrics present

If suspicious:
```
⚠️ Revenue $50,000 is 15x your average. Confirm?
```
