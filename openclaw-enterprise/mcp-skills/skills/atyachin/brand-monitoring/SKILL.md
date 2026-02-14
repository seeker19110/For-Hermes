---
name: social-sentiment
description: "Sentiment analysis for brands and products across Twitter, Reddit, and Instagram. Monitor public opinion, track brand reputation, detect PR crises, surface complaints and praise at scale — analyze 70K+ posts with bulk CSV export and Python/pandas. Social listening and brand monitoring powered by 1.5B+ indexed posts."
homepage: https://xpoz.ai
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "bins": ["mcporter"],
            "skills": ["xpoz-setup"],
            "network": ["mcp.xpoz.ai"],
            "credentials": "Xpoz account (free tier) — auth via xpoz-setup skill (OAuth 2.1)",
          },
      },
  }
tags:
  - sentiment-analysis
  - brand-monitoring
  - social-media
  - twitter
  - reddit
  - instagram
  - analytics
  - brand-sentiment
  - reputation
  - social-listening
  - opinion-mining
  - brand-tracking
  - competitor-analysis
  - public-opinion
  - crisis-detection
  - NLP
  - reputation
  - mcp
  - xpoz
  - opinion
  - market-research
---

# Social Sentiment

**Find out what people really think — from what they're actually saying on social media.**

Analyze sentiment for any brand, product, topic, or person across Twitter, Reddit, and Instagram. Surfaces positive and negative themes, flags viral complaints, compares competitors, and tracks opinion over time — powered by 1.5B+ indexed posts via Xpoz MCP.

**Scale:** Analyzes thousands to tens of thousands of posts per run using bulk CSV exports and automated code analysis. Not a sample — the full dataset.

---

## ⚡ Prerequisites

1. **Xpoz MCP** must be configured and authenticated. Follow the [xpoz-setup](https://clawhub.ai/skills/xpoz-setup) skill.

Verify Xpoz is ready:

```bash
mcporter call xpoz.checkAccessKeyStatus
```

If not `hasAccessKey: true`, follow xpoz-setup first, then return here.

---

## How It Works

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  STEP 1: COLLECT │ →  │ STEP 2: BULK     │ →  │ STEP 3: ANALYZE  │
│                  │    │ DOWNLOAD         │    │ AT SCALE         │
│ Search Twitter   │    │                  │    │                  │
│ Search Reddit    │    │ Get CSV export   │    │ Python/pandas on │
│ Search Instagram │    │ operationId from │    │ full dataset     │
│ (keyword queries │    │ each search      │    │ Keyword classify │
│  across all 3)   │    │ Download full    │    │ Engagement weight│
│                  │    │ CSVs (up to 64K  │    │ Theme extraction │
│                  │    │ rows each!)      │    │ Viral detection  │
└──────────────────┘    └──────────────────┘    └──────────────────┘

┌──────────────────┐
│  STEP 4: REPORT  │
│                  │
│ Overall score    │
│ Theme breakdown  │
│ Top voices       │
│ Viral flags      │
│ Recommendations  │
└──────────────────┘
```

---

## Usage

### Basic: Single Brand/Product

> "Analyze sentiment for Notion"
> "What do people think about Cursor IDE?"
> "How is the public perception of Tesla right now?"

### Comparison Mode

> "Compare sentiment for Notion vs Obsidian"
> "How does Figma sentiment compare to Canva?"

### Topic/Event Tracking

> "What's the sentiment around the new iPhone launch?"
> "How are people reacting to the latest OpenAI announcement?"

---

## Step 1: Search All Platforms

For the target brand/product/topic, run parallel searches across all three platforms.

### Generate Search Queries

Create 2-3 queries per platform to capture different angles:

1. **Direct mentions** — the brand/product name (broadest query)
2. **Pain points** — complaints, issues, frustrations (targeted negative)
3. **Praise** — love, recommend, best, amazing (targeted positive)

**Example for "Notion":**
- `"Notion"` (direct mentions — this is the main high-volume query)
- `"Notion" AND (slow OR buggy OR frustrating OR hate OR terrible OR worst OR broken)` (negative)
- `"Notion" AND (love OR amazing OR best OR recommend OR perfect OR great)` (positive)

### Twitter

```bash
mcporter call xpoz.getTwitterPostsByKeywords \
  query='"BRAND_NAME"' \
  startDate="YYYY-MM-DD" \
  limit=100 \
  fields='["id","text","authorUsername","likeCount","retweetCount","replyCount","impressionCount","createdAtDate"]'
```

**Important:** Always poll for results:

```bash
mcporter call xpoz.checkOperationStatus operationId="OPERATION_ID"
```

Poll every 5 seconds until `status: completed`.

### Reddit

```bash
mcporter call xpoz.getRedditPostsByKeywords \
  query='"BRAND_NAME"' \
  startDate="YYYY-MM-DD" \
  limit=100
```

### Instagram

```bash
mcporter call xpoz.getInstagramPostsByKeywords \
  query='"BRAND_NAME"' \
  startDate="YYYY-MM-DD" \
  limit=100 \
  fields='["id","caption","username","likeCount","commentCount","createdAtDate"]'
```

### Default Time Period

- Use **last 30 days** unless the user specifies otherwise
- For events/launches, narrow to the relevant window

---

## Step 2: Bulk CSV Download (CRITICAL — DO NOT SKIP)

**This is what makes this skill powerful.** Every Xpoz search returns a `dataDumpExportOperationId` in its response. This gives you a CSV download of the COMPLETE result set — up to 64,000 rows per query.

**DO NOT just read the first 100 results from the API response and call it done.** That's sampling, not analysis. Download the full CSV.

### How to get the CSV

1. After each search completes, note the `dataDumpExportOperationId` from the response
2. Poll it until the CSV is ready:

```bash
mcporter call xpoz.checkOperationStatus operationId="op_datadump_XXXXX"
```

3. When complete, you'll get a `downloadUrl` — download it:

```bash
curl -o /tmp/twitter-sentiment.csv "DOWNLOAD_URL"
```

4. Repeat for each platform's search results

### What you get

Each CSV contains the full dataset with all requested fields:
- **Twitter CSV:** id, text, authorUsername, likeCount, retweetCount, replyCount, impressionCount, createdAtDate
- **Reddit CSV:** id, title, body, authorUsername, subredditName, score, numComments, createdAtDate
- **Instagram CSV:** id, caption, username, likeCount, commentCount, createdAtDate

### Volume expectations

| Brand Size | Twitter | Reddit | Instagram | Total |
|------------|---------|--------|-----------|-------|
| Niche product | 100-500 | 10-50 | 10-50 | ~200-600 |
| Mid-tier tool | 1K-10K | 50-500 | 50-200 | ~1K-10K |
| Major brand | 10K-64K | 500-5K | 200-2K | ~10K-70K |

For very high-volume brands, you can limit the date range to keep the dataset manageable while still analyzing thousands of posts.

---

## Step 3: Analyze at Scale with Code

**Use Python/pandas to analyze the full CSV datasets.** This is where bulk analysis happens — not by reading posts one by one, but by running automated classification and aggregation over the entire dataset.

### Analysis Script

Write and execute a Python script that:

```python
import pandas as pd
import re
from collections import Counter

# Load all CSVs
twitter_df = pd.read_csv('/tmp/twitter-sentiment.csv')
reddit_df = pd.read_csv('/tmp/reddit-sentiment.csv')
instagram_df = pd.read_csv('/tmp/instagram-sentiment.csv')

# === SENTIMENT CLASSIFICATION ===
# Keyword-based classification (fast, works at scale)

POSITIVE_KEYWORDS = [
    'love', 'amazing', 'best', 'great', 'awesome', 'excellent', 'perfect',
    'recommend', 'incredible', 'fantastic', 'game changer', 'game-changer',
    'impressed', 'beautiful', 'brilliant', 'outstanding', 'favorite',
    'happy', 'excited', 'wonderful', 'solid', 'reliable', 'smooth',
    'intuitive', 'powerful', 'clean', 'fast', 'helpful', 'goat', 'fire',
    'lfg', 'must-have', 'must have', 'worth it', 'changed my life'
]

NEGATIVE_KEYWORDS = [
    'hate', 'terrible', 'worst', 'awful', 'horrible', 'broken', 'buggy',
    'slow', 'expensive', 'overpriced', 'frustrating', 'disappointed',
    'unusable', 'garbage', 'trash', 'scam', 'malware', 'insecure',
    'unsafe', 'security', 'vulnerability', 'leak', 'privacy', 'risky',
    'annoying', 'painful', 'nightmare', 'waste', 'regret', 'sucks',
    'god-awful', 'god awful', 'rip-off', 'don\'t use', 'do not use',
    'giving up', 'uninstalled', 'switched away', 'cancel'
]

def classify_sentiment(text):
    """Classify a post as positive, negative, neutral, or mixed."""
    if not isinstance(text, str):
        return 'neutral', 0
    text_lower = text.lower()
    pos_hits = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    neg_hits = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    
    if pos_hits > 0 and neg_hits > 0:
        return 'mixed', pos_hits - neg_hits
    elif pos_hits > 0:
        return 'positive', pos_hits
    elif neg_hits > 0:
        return 'negative', -neg_hits
    else:
        return 'neutral', 0

# Apply to Twitter
twitter_df['sentiment'], twitter_df['intensity'] = zip(
    *twitter_df['text'].apply(classify_sentiment)
)

# Apply to Reddit (use title + body if available)
reddit_text = reddit_df['title'].fillna('') + ' ' + reddit_df.get('body', pd.Series([''] * len(reddit_df))).fillna('')
reddit_df['sentiment'], reddit_df['intensity'] = zip(
    *reddit_text.apply(classify_sentiment)
)

# Apply to Instagram
instagram_df['sentiment'], instagram_df['intensity'] = zip(
    *instagram_df['caption'].apply(classify_sentiment)
)

# === ENGAGEMENT WEIGHTING ===
import numpy as np

# Twitter engagement score
twitter_df['engagement'] = (
    twitter_df.get('likeCount', 0).fillna(0) +
    twitter_df.get('retweetCount', 0).fillna(0) * 2 +
    twitter_df.get('replyCount', 0).fillna(0) * 1.5
)
twitter_df['weighted_score'] = twitter_df['intensity'] * np.log2(1 + twitter_df['engagement'])

# === AGGREGATE METRICS ===
for label, df in [('Twitter', twitter_df), ('Reddit', reddit_df), ('Instagram', instagram_df)]:
    total = len(df)
    pos = (df['sentiment'] == 'positive').sum()
    neg = (df['sentiment'] == 'negative').sum()
    neu = (df['sentiment'] == 'neutral').sum()
    mix = (df['sentiment'] == 'mixed').sum()
    print(f"\n=== {label} ({total} posts) ===")
    print(f"  Positive: {pos} ({pos/total*100:.1f}%)")
    print(f"  Negative: {neg} ({neg/total*100:.1f}%)")
    print(f"  Neutral:  {neu} ({neu/total*100:.1f}%)")
    print(f"  Mixed:    {mix} ({mix/total*100:.1f}%)")

# === THEME EXTRACTION ===
# Define theme keyword groups
THEMES = {
    'Performance / Speed': ['slow', 'fast', 'speed', 'performance', 'lag', 'loading'],
    'Pricing / Cost': ['expensive', 'cheap', 'price', 'pricing', 'cost', 'free', 'overpriced', 'afford', 'worth'],
    'Security': ['security', 'secure', 'unsafe', 'malware', 'vulnerability', 'privacy', 'leak', 'plaintext'],
    'Ease of Use / UX': ['intuitive', 'easy', 'simple', 'hard', 'difficult', 'confusing', 'ux', 'ui', 'clean'],
    'Setup / Installation': ['install', 'setup', 'set up', 'configure', 'getting started', 'onboarding'],
    'Features': ['feature', 'missing', 'need', 'wish', 'want', 'add', 'support'],
    'Customer Support': ['support', 'help', 'response', 'team', 'community'],
    'Reliability / Bugs': ['bug', 'crash', 'broken', 'error', 'issue', 'fix', 'stable', 'reliable'],
}

def extract_themes(text):
    if not isinstance(text, str):
        return []
    text_lower = text.lower()
    return [theme for theme, keywords in THEMES.items() if any(kw in text_lower for kw in keywords)]

# Apply to all datasets
all_posts = pd.concat([
    twitter_df[['text', 'sentiment', 'engagement']].rename(columns={'text': 'content'}).assign(platform='twitter'),
    reddit_df[['title', 'sentiment']].rename(columns={'title': 'content'}).assign(platform='reddit', engagement=0),
    instagram_df[['caption', 'sentiment']].rename(columns={'caption': 'content'}).assign(platform='instagram', engagement=0),
])
all_posts['themes'] = all_posts['content'].apply(extract_themes)

# Theme frequency by sentiment
from collections import defaultdict
theme_stats = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0, 'total': 0})
for _, row in all_posts.iterrows():
    for theme in row['themes']:
        theme_stats[theme][row['sentiment']] += 1
        theme_stats[theme]['total'] += 1

print("\n=== THEMES ===")
for theme, stats in sorted(theme_stats.items(), key=lambda x: x[1]['total'], reverse=True):
    print(f"  {theme}: {stats['total']} mentions (pos={stats['positive']}, neg={stats['negative']}, neu={stats['neutral']})")

# === VIRAL FLAGS ===
# Posts with outsized engagement
if 'engagement' in twitter_df.columns:
    viral = twitter_df.nlargest(10, 'engagement')[['text', 'authorUsername', 'likeCount', 'retweetCount', 'impressionCount', 'sentiment']]
    print("\n=== TOP 10 VIRAL POSTS (Twitter) ===")
    for _, row in viral.iterrows():
        print(f"  [{row['sentiment'].upper()}] @{row['authorUsername']} — {row.get('likeCount',0)} likes, {row.get('impressionCount',0)} imp")
        print(f"    {str(row['text'])[:120]}...")

# === OVERALL SCORE ===
# Weighted by engagement: positive posts add, negative subtract, normalize to 0-100
pos_weight = twitter_df[twitter_df['sentiment'] == 'positive']['weighted_score'].sum()
neg_weight = twitter_df[twitter_df['sentiment'] == 'negative']['weighted_score'].abs().sum()
total_weight = pos_weight + neg_weight
if total_weight > 0:
    raw_score = (pos_weight - neg_weight) / total_weight  # -1 to 1
    normalized = int((raw_score + 1) * 50)  # 0 to 100
    print(f"\n=== OVERALL SCORE: {normalized}/100 ===")
```

### Key analysis principles:

1. **Analyze ALL posts, not a sample** — That's why we download the CSV
2. **Keyword-based classification scales** — Reading 10K posts individually doesn't; pattern matching does
3. **Engagement weighting matters** — A complaint with 500 likes ≠ a complaint with 0 likes
4. **Theme extraction via keyword groups** — Identifies what people are actually talking about
5. **Viral detection via engagement outliers** — Flags posts with outsized reach

### Adapt the keyword lists

The `POSITIVE_KEYWORDS`, `NEGATIVE_KEYWORDS`, and `THEMES` dictionaries above are starting points. **Customize them for the specific brand/product:**

- For a **gaming product**: add "fun", "addictive", "boring", "grind", "pay to win"
- For a **SaaS tool**: add "integration", "API", "downtime", "onboarding"
- For a **consumer brand**: add "quality", "shipping", "return", "customer service"

### Output from the script

The script produces raw numbers. Use these to write the final report — the LLM interprets the data, identifies patterns, and generates actionable insights. The script does the heavy lifting (classifying 10K+ posts); the LLM does the thinking (what does this mean?).

---

## Step 4: Generate Report

After running the analysis script, compile findings into a structured report.

### Report Structure

#### 1. Sentiment Score (headline number)

```
Overall Sentiment: 72/100 (Mostly Positive)

Posts analyzed: 14,832 (not a sample — full dataset)

Breakdown:
  😊 Positive: 58% (8,603 posts)
  😠 Negative: 24% (3,560 posts)
  😐 Neutral:  18% (2,669 posts)

Platform breakdown:
  Twitter:   68/100 (12,400 posts analyzed)
  Reddit:    61/100 (1,932 posts analyzed)
  Instagram: 82/100 (500 posts analyzed)
```

**Score calculation:**
- Engagement-weighted: `(pos_weight - neg_weight) / total_weight`, normalized to 0-100
- 0-30 = Very Negative, 31-45 = Negative, 46-55 = Neutral, 56-70 = Positive, 71-100 = Very Positive

#### 2. Key Themes

List top themes by frequency, with sentiment breakdown and representative quotes:

```
📈 POSITIVE THEMES

1. "Ease of Use" — 1,847 mentions (72% positive)
   Top posts by engagement:
   "Notion's database views just clicked for me. Game changer." — @user (234 likes)
   "Switched from Confluence to Notion and never looked back" — r/productivity (189 upvotes)

📉 NEGATIVE THEMES

1. "Performance / Speed" — 2,038 mentions (81% negative)
   Top posts by engagement:
   "Notion is unusable with large databases. 10+ second load times." — @dev (567 likes)
```

#### 3. Viral Moments

Flag top 10 posts by engagement score across all platforms. For each:
- Sentiment classification
- Full text quote
- Engagement metrics
- Platform and URL

#### 4. Top Voices

Most influential accounts talking about the brand (by total engagement across their posts):
- Username, platform, follower count if available
- Their overall stance (positive/negative/mixed)
- Their highest-engagement post

#### 5. Competitor Comparison (if requested)

Side-by-side metrics with identical methodology applied to each brand.

#### 6. Actionable Insights

3-5 recommendations based on the data:
- What negative themes need addressing?
- What positive themes to amplify?
- Which viral moments need response?
- Platform-specific strategies

---

## Comparison Mode

When comparing two or more brands:

1. Run the full pipeline for each brand separately
2. Use the same time period, query structure, and keyword lists
3. Download CSVs and run the same analysis script for each
4. Present side-by-side metrics
5. Note volume differences (more mentions ≠ better sentiment)

---

## Scheduling (Optional)

For ongoing monitoring, the user can set up a cron job:

```
"Run social sentiment analysis for [brand] weekly and email me the report"
```

The agent can use OpenClaw cron to schedule this as a recurring isolated job.

---

## Data Storage

Store results for trend tracking:

```bash
mkdir -p data/social-sentiment
# Save CSVs and analysis results per run
# data/social-sentiment/{brand}-{date}-twitter.csv
# data/social-sentiment/{brand}-{date}-reddit.csv
# data/social-sentiment/{brand}-{date}-instagram.csv
# data/social-sentiment/{brand}-{date}-analysis.json
```

If previous runs exist, include a **trend line** in the report:

```
📈 TREND (last 4 weeks)
  Week 1: 68/100 (analyzed 12,400 posts)
  Week 2: 65/100 (analyzed 11,800 posts) ↓ pricing backlash
  Week 3: 70/100 (analyzed 13,200 posts) ↑ new feature launch
  Week 4: 72/100 (analyzed 14,832 posts) ↑ stabilizing
```

---

## Tips for Best Results

- **Download the full CSV** — Never settle for the first 100 API results. The CSV export is the whole point.
- **Be specific with brand names** — "Notion" is better than "notion app" (avoid false positives)
- **Check for ambiguity** — If the brand name is a common word (e.g., "Slack", "Rust"), add context terms
- **Customize keyword lists** — The default positive/negative keywords are a starting point. Add domain-specific terms.
- **Reddit is gold for honest opinions** — Longer posts, real opinions, subreddit context
- **Instagram skews positive** — Platform culture favors positive content; adjust expectations
- **Twitter captures real-time reactions** — Best for event-driven sentiment and highest volume
- **30 days is the sweet spot** — Enough data for trends, recent enough to be actionable
- **For huge brands (50K+ posts)** — Narrow the date range rather than sampling

---

## Responsible Use

- Only analyze **publicly available** social media content
- Don't use sentiment data to harass or target individuals
- Present findings honestly — don't cherry-pick to misrepresent opinion
- Disclose methodology when sharing results externally
- Respect that public posts ≠ consent to surveillance at scale

---

## Resources

- **Xpoz:** [xpoz.ai](https://xpoz.ai) — social intelligence MCP powering the searches
- **Setup:** [xpoz-setup on ClawHub](https://clawhub.ai/skills/xpoz-setup) — one-time auth
- **Search reference:** [xpoz-social-search on ClawHub](https://clawhub.ai/skills/xpoz-social-search) — full query patterns

---

**Built for ClawHub • Powered by Xpoz**
