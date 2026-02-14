---
name: agenthc-market-intelligence
description: Get real-time market intelligence for trading and macro analysis. Query 46 modules including market regime detection, volatility analysis, treasury yields, crypto metrics, Fed/liquidity tracking, correlation anomalies, alpha signals, credit cycle, institutional positioning, and sector rotation. Use when the user asks about markets, stocks, crypto, bonds, economy, Fed policy, trading signals, or financial conditions.
homepage: https://github.com/traderhc123/main
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      env: ["AGENTHC_API_KEY"]
      bins: ["curl", "jq"]
    primaryEnv: "AGENTHC_API_KEY"
---

# AgentHC Market Intelligence

Institutional-grade market intelligence API for AI agents. 46 modules covering equities, bonds, crypto, macro, Fed, liquidity, regime detection, alpha signals, and more. Built by @traderhc.

## Setup

### 1. Register (free, no KYC)

```bash
curl -s -X POST "https://api.traderhc.com/api/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "MyOpenClawAgent", "description": "OpenClaw agent using AgentHC intelligence"}' | jq '.'
```

Save the `api_key` from the response.

### 2. Set environment variable

```bash
export AGENTHC_API_KEY=your_api_key_here
```

## Free Modules (no payment required)

### Market Overview
Get market snapshot: S&P 500, VIX, treasury yields, DXY, commodities, sector performance, Fear & Greed, and market regime.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### News Sentiment
Breaking news with sentiment scoring, category classification, and event extraction.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/news_sentiment" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Crypto Intelligence
Bitcoin, Ethereum, BTC dominance, halving cycle, alt season detection, crypto Fear & Greed.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/crypto_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Economic Calendar
Upcoming and released economic events (NFP, CPI, FOMC, ISM) with beat/miss detection.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/economic_calendar" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

## Premium Modules (100 sats/query)

These require Premium tier. Upgrade with Lightning payment or use L402 per-request payment.

### Technical Analysis
RSI, MACD, Bollinger Bands, support/resistance, volume analysis for any ticker.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/technical_analysis?ticker=AAPL" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Bond Intelligence
Treasury yields, yield curve dynamics, credit spreads, duration risk.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/bond_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Fed Intelligence
Fed balance sheet, FOMC calendar, ISM PMI, yield curve analysis, RRP/repo, liquidity trends.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/fed_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Macro Intelligence
CPI, PCE, NFP, unemployment, M2, credit spreads, ISM Services, consumer sentiment, housing.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/macro_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Correlation Tracker
18+ cross-market correlation pairs with anomaly detection and regime classification.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/correlation_tracker" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Volatility Analyzer
VIX regime classification, term structure, VVIX, implied vs realized vol.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/volatility_analyzer" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Sector Rotation
Business cycle rotation, sector leadership, risk-on/off flows, seasonal patterns.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/sector_rotation" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### ETF Flows
Bitcoin ETF flows (IBIT, FBTC, GBTC), equity ETF flows, rotation signals.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/etf_flows" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Polymarket Intelligence
Fed/FOMC prediction markets, recession odds, crypto price predictions.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/polymarket_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

## Institutional Modules (500 sats/query)

### Alpha Signals
Systematic multi-factor signal composite: momentum, mean reversion, carry, value, volatility, flow, macro.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/alpha_signals" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Regime Engine
12 market regimes with transition probabilities, leading indicators, historical analogues.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/regime_engine" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Tail Risk Engine
Crisis detection with 12 crisis types, early warning indicators, historical playbooks, composite tail risk score.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/tail_risk_engine" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Liquidity Intelligence
Fed net liquidity (Balance Sheet - TGA - RRP), liquidity regime, bank stress signals.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/liquidity_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Credit Cycle
HY/IG/BBB/CCC spreads, lending standards, default indicators, credit cycle phase, financial conditions.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/credit_cycle" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Institutional Positioning
CFTC COT data, AAII sentiment, NAAIM exposure, put/call ratios, crowded trade detection.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/institutional_positioning" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

## Agent-Optimized Format

For AI agents, use `format=agent` to get actionable signals with direction, confidence, urgency, and delta tracking:

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence?format=agent" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.signals'
```

Response includes:
- `signals.direction` — bullish/bearish/neutral/mixed
- `signals.confidence` — 0.0 to 1.0
- `signals.urgency` — low/medium/high/critical
- `signals.actionable` — true if action recommended
- `suggested_actions` — related modules to query next
- `delta` — what changed since your last query

## Compact Format (Token-Efficient)

Use `format=compact` for 60% fewer tokens in your context window:

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence?format=compact" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.'
```

## Batch Queries (Premium+)

Query multiple modules in one request:

```bash
curl -s -X POST "https://api.traderhc.com/api/v1/intelligence/batch" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": ["market_intelligence", "bond_intelligence", "fed_intelligence"]}' | jq '.'
```

## Real-Time Events (SSE Streaming)

Subscribe to live market events via Server-Sent Events:

```bash
curl -N "https://api.traderhc.com/api/v1/events/stream?types=market.regime_change,market.vix_spike,market.flash_crash" \
  -H "X-API-Key: $AGENTHC_API_KEY"
```

Events include: regime changes, VIX spikes, flash crashes, correlation breaks, tail risk alerts, alpha signal flips, breaking news.

## Lightning Payment (L402)

For per-request payment without registration, the API supports L402 protocol. Request a premium endpoint without auth to receive a 402 response with a Lightning invoice. Pay and retry with the preimage.

## All 46 Modules

| Module | Tier | Description |
|--------|------|-------------|
| market_intelligence | Free | Market snapshot, regime, Fear & Greed |
| news_sentiment | Free | Breaking news with sentiment |
| crypto_intelligence | Free | BTC, ETH, dominance, halving cycle |
| economic_calendar | Free | Economic events, beat/miss |
| technical_analysis | Premium | TA for any ticker (RSI, MACD, etc.) |
| bond_intelligence | Premium | Yields, curve, credit spreads |
| fed_intelligence | Premium | Fed balance sheet, FOMC, ISM |
| macro_intelligence | Premium | Inflation, employment, M2, credit |
| correlation_tracker | Premium | Cross-market correlation anomalies |
| volatility_analyzer | Premium | VIX regime, term structure, skew |
| sector_rotation | Premium | Business cycle sector rotation |
| divergence_detection | Premium | Price/breadth/volume divergences |
| etf_flows | Premium | BTC ETF, equity ETF flows |
| intermarket_analysis | Premium | Stock/bond/dollar/commodity signals |
| earnings_calendar | Premium | Upcoming earnings, reactions |
| crypto_derivatives | Premium | Funding rates, open interest |
| onchain_metrics | Premium | Hash rate, mempool, NVT |
| finnhub_intelligence | Premium | Earnings, insider, analyst ratings |
| reddit_sentiment | Premium | WSB, r/stocks sentiment |
| market_structure | Premium | Breadth, A/D, McClellan |
| polymarket_intelligence | Premium | Prediction market odds |
| educational_content | Premium | Trading concepts |
| alpha_signals | Institutional | Multi-factor signal composite |
| regime_engine | Institutional | 12 market regimes |
| tail_risk_engine | Institutional | Crisis detection, early warnings |
| hedge_fund_playbooks | Institutional | 20+ institutional setups |
| liquidity_intelligence | Institutional | Fed net liquidity, regime |
| credit_cycle | Institutional | Credit cycle phase, spreads |
| institutional_positioning | Institutional | COT, sentiment, smart money |
| smart_money_tracker | Institutional | Smart vs dumb money |
| market_microstructure | Institutional | Gamma, vanna, dealer positioning |
| volatility_surface | Institutional | VIX ecosystem, skew, IV vs RV |
| currency_intelligence | Institutional | DXY, carry trades, FX |
| valuation_intelligence | Institutional | CAPE, Buffett indicator, ERP |
| geopolitical_risk | Institutional | Risk scoring, hedging |
| central_bank_dashboard | Institutional | All major central banks |
| factor_analysis | Institutional | Factor rotation, crowding |
| narrative_tracker | Institutional | Market narrative lifecycle |
| advanced_risk | Institutional | Kelly, VaR, drawdown protocols |
| global_flows | Institutional | Dollar cycle, capital rotation |
| wealth_knowledge | Institutional | Legendary investor wisdom |
| institutional_content | Institutional | Viral FinTwit content |
| market_knowledge | Institutional | Deep market knowledge base |
| sentiment_engine | Institutional | Multi-source sentiment |

## Pricing

- **Free**: 4 modules, 100 requests/day
- **Premium**: 24 modules, 5,000 requests/day, 100 sats/query (~$0.10)
- **Institutional**: 46 modules, 50,000 requests/day, 500 sats/query (~$0.50)

Payment via Bitcoin Lightning Network. Instant settlement, no KYC.

## Example Workflows

### Morning Market Brief
```bash
# Get market overview + bonds + macro + crypto in one batch
curl -s -X POST "https://api.traderhc.com/api/v1/intelligence/batch" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": ["market_intelligence", "bond_intelligence", "macro_intelligence", "crypto_intelligence"]}' | jq '.results'
```

### Risk Check
```bash
# Check tail risk + volatility + correlations
curl -s -X POST "https://api.traderhc.com/api/v1/intelligence/batch" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": ["tail_risk_engine", "volatility_analyzer", "correlation_tracker"]}' | jq '.results'
```

### Ticker Deep Dive
```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/technical_analysis?ticker=NVDA&format=agent" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.'
```

## Disclaimer

All data and analysis is for educational and informational purposes only. Not financial advice. Not a registered investment advisor. Always do your own research.
