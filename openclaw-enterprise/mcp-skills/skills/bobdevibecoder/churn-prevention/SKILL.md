# churn-prevention

Detects at-risk subscribers and triggers win-back flows to reduce churn.

## Overview

Monitors subscription events for cancellation signals, identifies at-risk customers, and generates retention emails and offers. Goal: reduce monthly churn rate below 5%.

## Usage

- "churn check" - Analyze all subscribers for churn risk
- "churn at-risk" - List customers flagged as at-risk
- "churn winback PRODUCT-SLUG" - Generate win-back email sequence
- "churn report" - Monthly churn analysis report

## Churn Risk Signals

| Signal | Risk Level | Source |
|--------|-----------|--------|
| Payment failed 2+ times | HIGH | Stripe events |
| Subscription downgraded | MEDIUM | Stripe events |
| No logins in 14+ days | MEDIUM | Analytics (if tracked) |
| Support complaint filed | MEDIUM | Feedback collector |
| Cancellation initiated | HIGH | Stripe events |
| Trial ending, no upgrade | MEDIUM | Stripe events |

## Detection

Check Stripe for churn signals:
POST http://host.docker.internal:18790/stripe-query
Headers: Content-Type: application/json, X-Bridge-Secret: DEPLOY_BRIDGE_SECRET
Body: { "type": "at-risk", "daysInactive": 14 }

Also check:
- Subscriptions with past_due status
- Customers with failed charges in last 30 days
- Subscriptions set to cancel at period end

## Win-Back Flows

### For Payment Failures (involuntary churn)
1. Day 0: "Your payment failed" - link to update card
2. Day 3: "Still having trouble?" - alternative payment methods
3. Day 7: "We miss you" - extend access for 7 more days free
4. Day 14: Account paused, offer 50% off for 3 months to return

### For Cancellations (voluntary churn)
1. Immediate: Exit survey - "Why are you leaving?"
2. Day 1: "Before you go" - offer 30% off for 3 months
3. Day 7: "New feature just launched" - highlight recent improvements
4. Day 30: "We've improved" - summary of changes since they left

### For Trial Expiring
1. Day -3: "Your trial ends in 3 days" - highlight value received
2. Day -1: "Last day of trial" - special launch price offer
3. Day 0: "Trial ended" - extend 7 more days if they start upgrade
4. Day +3: "Still thinking?" - comparison with alternatives (we win)

## Output

Generate win-back email drafts in:
/home/milad/.openclaw/workspace/skills/churn-prevention/winback/PRODUCT-SLUG/

## Metrics to Track

- Monthly churn rate (target: under 5%)
- Win-back success rate
- Revenue recovered from win-back flows
- Average customer lifetime (target: 6+ months)

## Rules

- NEVER send win-back emails automatically - generate drafts for human review
- Maximum 4 emails per win-back sequence
- Respect unsubscribes immediately
- Log all churn events for trend analysis
- Report monthly churn metrics in the weekly revenue report

## Integration

- Uses stripe-webhook-monitor for real-time cancellation events
- Uses user-feedback-collector for complaint signals
- Feeds into revenue-tracker for churn rate calculations
- Generates emails via email-outreach format standards
