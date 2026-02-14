# auto-pricing-optimizer

Analyzes conversion data and competitor pricing to recommend optimal price points for each product.

## Overview

Uses Stripe conversion data, competitor analysis, and pricing psychology to suggest price changes that maximize revenue. Reports recommendations — never changes prices without human approval.

## Usage

-  - Analyze all products and suggest price changes
-  - Analyze a specific product
-  - Research competitor pricing

## Analysis Steps

### Step 1: Get Current Pricing Data


### Step 2: Analyze Conversion Metrics
For each product, calculate:
- Signup-to-paid conversion rate
- Trial-to-paid conversion rate
- Average revenue per user (ARPU)
- Churn rate (cancellations / active)
- Lifetime value estimate (ARPU / churn rate)

### Step 3: Competitor Research
Use web search to find competitor pricing:
- Search: "[tool type] pricing plans 2026"
- Compare features vs price for top 5 competitors
- Identify positioning (cheapest, mid-range, premium)

### Step 4: Generate Recommendations

## Pricing Strategy Rules

| Signal | Recommendation |
|--------|---------------|
| Conversion > 15% | Price may be too low — test +-3 increase |
| Conversion < 3% | Price may be too high — test -2 decrease or add free tier |
| Competitors average 2x our price | Significant room to increase |
| High churn after month 1 | Value perception issue — improve onboarding or add features |
| LTV < 0 | Consider annual plan with discount to lock in revenue |

## Pricing Tiers to Test

For micro-SaaS tools, recommend this tiering:
- **Free**: Limited usage (5 conversions/day) — drives traffic + SEO
- **Pro (-9/mo)**: Unlimited usage — main revenue driver
- **Team (9-29/mo)**: Multiple users + API access — upsell

## Report Format



## Important

- NEVER change prices automatically
- Always present as recommendations to the human
- Run analysis monthly or when triggered manually
- Factor in that new products need time to gather data (minimum 30 days)
