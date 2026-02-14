---
name: twitter-scout
description: Use Grok AI to browse and analyze Twitter/X in real-time. Find trending topics, viral posts, crypto alpha, tech news, and opportunities. Use when asked to "check twitter", "find tweets about", "what's trending on X", "twitter alpha", "scan twitter for", or any Twitter/X related research.
---

# Twitter Scout (Grok-Powered)

Real-time Twitter/X intelligence using Grok AI's native X access.

## When to Use

- "What's trending on Twitter?"
- "Find tweets about [topic]"
- "Check Twitter for crypto alpha"
- "What are people saying about [company/token]?"
- "Find viral posts about [subject]"
- "Twitter sentiment on [topic]"
- "Scan X for opportunities"

## How It Works

This skill uses Grok AI which has **native real-time access to Twitter/X**. Unlike other AI models that can't see Twitter, Grok can:

- See real-time tweets and threads
- Analyze trending topics
- Find viral content
- Track sentiment on any topic
- Discover breaking news

## Usage

```bash
# Search for tweets on a topic
python3 scripts/twitter_scout.py search "bitcoin ETF"

# Get trending topics
python3 scripts/twitter_scout.py trending

# Analyze sentiment
python3 scripts/twitter_scout.py sentiment "ethereum"

# Find alpha/opportunities
python3 scripts/twitter_scout.py alpha "crypto"

# Get viral posts
python3 scripts/twitter_scout.py viral "AI agents"
```

## Environment

Requires `GROK_API_KEY` environment variable.

## Output Format

Returns structured JSON with:
- tweets: Array of relevant tweets
- sentiment: Overall sentiment analysis
- trending: Related trending topics
- summary: AI-generated summary of findings
- opportunities: Potential alpha/opportunities found

## Examples

**Find crypto alpha:**
```
twitter_scout.py alpha "solana memecoins"
```

**Check sentiment before trading:**
```
twitter_scout.py sentiment "NVIDIA stock"
```

**Research a project:**
```
twitter_scout.py search "OpenClaw AI agent"
```

## Rate Limits

Grok free tier: ~25 requests/day
Grok paid tier: Higher limits

## Tips

- Be specific with search terms for better results
- Use for market research, trend discovery, sentiment analysis
- Combine with other skills for full research workflow
- Great for finding early signals before they go mainstream
