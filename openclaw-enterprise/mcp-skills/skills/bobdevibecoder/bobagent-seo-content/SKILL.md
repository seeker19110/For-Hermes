---
name: seo-content
description: "Generate SEO blog posts and landing pages for deployed micro-SaaS products. Research keywords, write content, deploy to product blogs. Run weekly via cron or on-demand."
metadata: { "openclaw": { "emoji": "📝" } }
---

# SEO Content Engine

You generate high-quality, SEO-optimized blog posts and landing pages for micro-SaaS products built by the microsaas-factory skill. Content drives organic Google traffic — the primary growth channel.

## Execution Modes

### Generate Mode (default)
Generate new blog posts for a specific product.

**Trigger:** "write content for [product-slug]" or "generate blog posts for [product-name]"

### Keyword Research Mode
Research high-value keywords for a product's niche.

**Trigger:** "find keywords for [product-slug]"

### Bulk Mode (cron)
Auto-generate 2-3 posts per product per week.

**Trigger:** Weekly cron job

---

## Content Strategy

For each product, generate these content types in priority order:

### Tier 1: Bottom-of-Funnel (write first — these convert)
1. **"How to [do the thing]"** — Step-by-step tutorial using the product
   - Example: "How to Convert JSON to CSV — Free Online Tool"
2. **"Best [tool type] tools in 2026"** — Listicle featuring our product at #1
   - Example: "5 Best JSON to CSV Converters in 2026 (Free & Paid)"
3. **"[Our product] vs [competitor]"** — Comparison page
   - Example: "ConvertFlow vs Zamzar: Which JSON Converter Is Better?"

### Tier 2: Middle-of-Funnel (write next — these educate)
4. **"What is [format/concept]?"** — Educational content
   - Example: "What is JSON? A Beginner's Guide"
5. **"[Format A] vs [Format B]"** — Format comparison
   - Example: "JSON vs CSV: When to Use Which?"

### Tier 3: Top-of-Funnel (write last — these attract)
6. **"[Workflow] tips for [audience]"** — Workflow guides
   - Example: "Data Conversion Tips for Developers"

---

## Content Generation Process

### Step 1: Read Product Info
Read /home/node/.openclaw/workspace/skills/microsaas-factory/data/products.json to find the product details.

### Step 2: Research Keywords
Use web search to find:
- Primary keyword (high intent, e.g., "json to csv converter")
- 3-5 secondary keywords (related searches)
- 2-3 long-tail variations (e.g., "convert json to csv online free")
- Competitor names to compare against

Run the keyword helper:
```bash
node /home/node/.openclaw/workspace/skills/seo-content/scripts/keyword_research.js "[product-type]"
```

### Step 3: Generate Blog Post
Create a JSON file following this exact schema:

```json
{
  "title": "How to Convert JSON to CSV: Complete Guide (2026)",
  "description": "Learn the fastest ways to convert JSON data to CSV format. Free online tool, API access, and step-by-step instructions.",
  "date": "2026-02-03",
  "tags": ["guide", "json", "csv"],
  "sections": [
    {
      "heading": "Section Title with Keywords",
      "content": "2-4 paragraphs of genuinely useful content. Not fluff. Not keyword-stuffed. Write like a developer explaining to another developer."
    }
  ]
}
```

### Step 4: Save to Product
Save the JSON file to the product's blog content directory:
```bash
node /home/node/.openclaw/workspace/skills/seo-content/scripts/save_blog_post.js [product-slug] [post-slug] '[post-json]'
```

### Step 5: Redeploy Product
After adding content, trigger a redeploy:
```bash
cd /home/milad/[product-slug] && source ~/.nvm/nvm.sh && vercel --prod --yes 2>&1
```

### Step 6: Report
Send to Telegram:
```
📝 New blog post published!

Product: [name]
Title: [post title]
URL: [product-url]/blog/[post-slug]
Keywords: [primary], [secondary1], [secondary2]

Posts for this product: [total count]
```

---

## Content Rules

### SEO Rules
1. Title must contain the primary keyword naturally
2. Title should be 50-65 characters
3. Description (meta) should be 140-160 characters
4. Use the primary keyword in the first section
5. Use secondary keywords in subheadings
6. Each section should be 100-200 words
7. Total post: 800-1500 words (5-7 sections)
8. Include a CTA section pointing back to the product

### Quality Rules
1. Write genuinely useful content — not SEO spam
2. Include specific examples and code snippets where relevant
3. Be technically accurate
4. No fluff, no filler paragraphs
5. Write like a senior developer explaining to a junior
6. Every section should teach something actionable
7. Never generate fake testimonials or reviews

### Formatting Rules
1. Content is stored as JSON, not Markdown
2. Each section has a heading and content string
3. Use \n for line breaks within content
4. Keep tags to 3-5 relevant terms
5. Date should be today's date in YYYY-MM-DD format

---

## Keyword Research Guidelines

When researching keywords, prioritize:
- **Intent match**: "convert json to csv" beats "what is json" (higher buying intent)
- **Volume vs competition**: Target medium-volume, low-competition keywords
- **Long-tail first**: "convert json to csv online free" is easier to rank than "json converter"
- **Informational + transactional mix**: Mix "how to" posts with "best tools" posts

---

## Content Calendar

For each product, aim for this publishing schedule:
- **Week 1**: "How to [do the thing]" guide + "Best [tools] in 2026" listicle
- **Week 2**: "[Product] vs [Competitor]" comparison
- **Week 3**: "[Format A] vs [Format B]" educational post
- **Week 4**: "[Workflow] tips for [audience]" guide

Then cycle back with new keywords and angles.

---

## Error Handling
- If product not found in products.json: report error, list available products
- If web search fails: generate content from product config alone (skip keyword research)
- If deploy fails: save content locally and report — content is preserved for manual deploy
- If blog directory doesn't exist: create it
