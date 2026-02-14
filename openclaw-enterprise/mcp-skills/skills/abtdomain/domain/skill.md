# 🌐 DomainKits

**Turn AI into your domain investment expert.**

Search newly registered, expired, deleted domains. Check availability with pricing. WHOIS/DNS lookup. Track market trends.

---

## Why DomainKits?

| What you ask | What happens |
|--------------|--------------|
| "Find me a domain for my AI startup" | AI brainstorms names → validates availability → shows prices with register links |
| "What's dropping today?" | Searches expiring domains → finds valuable ones you can backorder |
| "Is stripe.com for sale?" | WHOIS + DNS + safety check → full analysis in seconds |
| "Show me trending keywords" | Data on what the market is registering |

---

## Connection
```json
{
  "mcp": {
    "url": "https://api.domainkits.com/v1/mcp"
  }
}
```

With API key (optional, for higher limits):
```json
{
  "mcp": {
    "url": "https://api.domainkits.com/v1/mcp",
    "headers": {
      "X-API-Key": "your-key-here"
    }
  }
}
```

---

## Environment Variables

| Name | Required | Description |
|------|----------|-------------|
| `DOMAINKITS_API_KEY` | No | Get your key at domainkits.com for higher rate limits and memory features |

---

## Tools

### Search
- **nrds** - Newly registered domains
- **aged** - Domains with 5-20+ years history
- **expired** - Domains entering deletion cycle
- **deleted** - Just-dropped domains, available now
- **active** - Live sites and for-sale listings
- **ns_reverse** - Domains on a specific nameserver

### Query
- **available** - Availability check with pricing
- **bulk_available** - Check multiple domains at once
- **whois** - Registration details
- **dns** - DNS records
- **safety** - Google Safe Browsing check
- **tld_check** - Keyword availability across TLDs

### Trends
- **keywords_trends** - Hot keywords in registrations
- **tld_trends** - TLD growth patterns
- **tld_rank** - Top TLDs by volume
- **price** - Registration costs by TLD

### Memory
- **get_preferences** - Get saved preferences
- **set_preferences** - Save preferences (requires consent)
- **delete_preferences** - Delete all data

---

## Instructions

When user wants domain suggestions:
1. Brainstorm names based on their keywords
2. Call `bulk_available` to validate
3. Show available options with prices and register links

When user wants to analyze a domain:
1. Call `whois`, `dns`, `safety`
2. Give a clear verdict

Output rules:
- Always show `register_url` for available domains
- Disclose affiliate links
- Default to `no_hyphen=true` and `no_number=true`

---

## Privacy

- Works without API key
- Memory OFF by default
- Users can delete data anytime via `delete_preferences`
- GDPR compliant

---

## Links

- Website: [domainkits.com](https://domainkits.com)
- GitHub: [ABTdomain/domainkits-mcp](https://github.com/ABTdomain/domainkits-mcp)
- Contact: info@domainkits.com