#!/usr/bin/env python3
"""
Twitter Scout - Grok-powered Twitter/X intelligence

Uses Grok AI's native Twitter access to find trends, alpha, and opportunities.

Usage:
    python twitter_scout.py search "bitcoin ETF"
    python twitter_scout.py trending
    python twitter_scout.py sentiment "ethereum"
    python twitter_scout.py alpha "crypto"
    python twitter_scout.py viral "AI"
"""

import os
import sys
import json
import argparse
import requests

GROK_API_URL = "https://api.x.ai/v1/chat/completions"

def get_api_key():
    """Get Grok API key from environment."""
    key = os.getenv("GROK_API_KEY")
    if not key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            key = os.getenv("GROK_API_KEY")
        except ImportError:
            pass
    return key

def query_grok(prompt: str, api_key: str) -> dict:
    """Send a query to Grok API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "grok-3-latest",
        "messages": [
            {
                "role": "system",
                "content": "You are a Twitter/X research assistant with real-time access to Twitter. Provide detailed, actionable insights. Always include specific tweets, usernames, and engagement metrics when relevant. Format output as structured data."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        return {"error": f"API error: {response.status_code}", "details": response.text}

    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

    return {
        "success": True,
        "response": content,
        "model": data.get("model"),
        "usage": data.get("usage")
    }

def search_twitter(query: str, api_key: str) -> dict:
    """Search Twitter for a specific topic."""
    prompt = f"""Search Twitter/X for recent posts about: "{query}"

Return the most relevant and engaging tweets. Include:
1. Top 5-10 most relevant/viral tweets with:
   - Username and handle
   - Tweet content
   - Engagement (likes, retweets, replies if visible)
   - Posted time (relative)
2. Key themes and talking points
3. Notable accounts discussing this
4. Overall sentiment (bullish/bearish/neutral)
5. Any breaking news or alpha

Format as structured JSON."""

    return query_grok(prompt, api_key)

def get_trending(api_key: str) -> dict:
    """Get current trending topics on Twitter."""
    prompt = """What's currently trending on Twitter/X right now?

Provide:
1. Top 10 trending topics/hashtags
2. Why each is trending (brief context)
3. Key tweets driving each trend
4. Any notable viral content
5. Breaking news if any

Focus on: tech, crypto, AI, finance, and general viral content.
Format as structured JSON."""

    return query_grok(prompt, api_key)

def analyze_sentiment(topic: str, api_key: str) -> dict:
    """Analyze Twitter sentiment on a topic."""
    prompt = f"""Analyze the current Twitter/X sentiment around: "{topic}"

Provide:
1. Overall sentiment score (1-10, where 1=very bearish, 10=very bullish)
2. Sentiment breakdown (% positive, negative, neutral)
3. Key positive takes (with usernames)
4. Key negative takes/FUD (with usernames)
5. Notable influencer opinions
6. Sentiment trend (improving/declining/stable)
7. Red flags or concerns being raised
8. Bull cases being made

Format as structured JSON with clear metrics."""

    return query_grok(prompt, api_key)

def find_alpha(topic: str, api_key: str) -> dict:
    """Find alpha and opportunities on Twitter."""
    prompt = f"""Find Twitter/X alpha and opportunities related to: "{topic}"

Look for:
1. Early signals before they go mainstream
2. Insider hints or alpha leaks
3. Underrated projects/tokens being discussed
4. Upcoming catalysts mentioned
5. Smart money movements being discussed
6. Opportunities others might be missing
7. Contrarian takes that could be right
8. Notable predictions from credible accounts

Prioritize:
- Tweets from accounts with good track records
- Information not yet widely known
- Actionable insights

Format as structured JSON with confidence levels."""

    return query_grok(prompt, api_key)

def find_viral(topic: str, api_key: str) -> dict:
    """Find viral posts on a topic."""
    prompt = f"""Find the most viral Twitter/X posts about: "{topic}"

Return:
1. Top 10 most viral/engaging tweets
2. For each tweet:
   - Full content
   - Username and follower count
   - Engagement metrics
   - Why it went viral
   - Key replies/quote tweets
3. Common themes in viral content
4. What makes these posts successful

Format as structured JSON."""

    return query_grok(prompt, api_key)

def main():
    parser = argparse.ArgumentParser(description="Twitter Scout - Grok-powered X intelligence")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search Twitter for a topic")
    search_parser.add_argument("query", help="Search query")

    # Trending command
    subparsers.add_parser("trending", help="Get trending topics")

    # Sentiment command
    sentiment_parser = subparsers.add_parser("sentiment", help="Analyze sentiment on a topic")
    sentiment_parser.add_argument("topic", help="Topic to analyze")

    # Alpha command
    alpha_parser = subparsers.add_parser("alpha", help="Find alpha and opportunities")
    alpha_parser.add_argument("topic", help="Topic to find alpha on")

    # Viral command
    viral_parser = subparsers.add_parser("viral", help="Find viral posts")
    viral_parser.add_argument("topic", help="Topic to find viral posts on")

    args = parser.parse_args()

    api_key = get_api_key()
    if not api_key:
        print(json.dumps({"error": "GROK_API_KEY environment variable not set"}))
        sys.exit(1)

    if args.command == "search":
        result = search_twitter(args.query, api_key)
    elif args.command == "trending":
        result = get_trending(api_key)
    elif args.command == "sentiment":
        result = analyze_sentiment(args.topic, api_key)
    elif args.command == "alpha":
        result = find_alpha(args.topic, api_key)
    elif args.command == "viral":
        result = find_viral(args.topic, api_key)
    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
