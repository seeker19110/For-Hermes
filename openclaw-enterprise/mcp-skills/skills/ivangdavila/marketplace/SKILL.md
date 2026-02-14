---
name: Marketplace
description: Navigate online marketplaces as buyer, seller, or builder with platform comparison, listing optimization, and scam detection.
---

## First: Identify the User's Role

Before guidance, ask:
1. **Buying** — Shopping on Amazon, eBay, FB Marketplace, Craigslist?
2. **Selling** — Listing products on one or more marketplaces?
3. **Multi-channel** — Managing inventory/presence across multiple platforms?
4. **Building** — Creating your own marketplace platform?

## Buyers

Key concerns: scam detection, price validation, cross-platform comparison.

- **Price history check** — Is this "sale" real or manufactured? Look for CamelCamelCamel (Amazon), Keepa, or platform-specific tools.
- **Seller red flags** — New accounts, stock photos, off-platform payment requests, prices 40%+ below market.
- **Fake review detection** — Uniform 5-star ratings, generic language, review spikes after product launch.
- **Local meetup safety** — Public places, daylight, payment in-person, verify item works before paying.

See `buyer-safety.md` for scam patterns by platform.

## Sellers

Key concerns: platform selection, fee optimization, listing performance.

| Platform | Best For | Take Rate |
|----------|----------|-----------|
| Amazon | Volume, Prime audience | 8-15% + FBA fees |
| eBay | Used/vintage, auctions | 13.25% final value |
| Etsy | Handmade, vintage, craft | 6.5% + 3% payment |
| FB Marketplace | Local, bulky items | 0% local, 5% shipped |

- **Listing optimization** — Platform-specific: Amazon = keywords in title, Etsy = tags matter, eBay = item specifics.
- **Shipping strategy** — Free shipping converts better but build into price. Calculate landed cost per platform.
- **First sales playbook** — Price competitively initially, prioritize reviews over margin.

See `seller-platforms.md` for detailed fee breakdowns and algorithm tips.

## Multi-Channel Sellers

Key concerns: inventory sync, price parity, consolidated operations.

- **Inventory management** — Tools: Sellbrite, Linnworks, ChannelAdvisor. Never oversell.
- **Price consistency** — Monitor your own listings. Amazon MAP violations can suspend accounts.
- **Cross-listing adaptation** — Don't copy-paste. Each platform has different SEO and audience expectations.
- **Review aggregation** — Track sentiment across all channels to spot product issues early.

## Building a Marketplace

Key concerns: business model, cold start, trust systems.

- **Revenue model** — Commission (10-20%), subscription, listing fees, or hybrid. Marketplace take rate benchmarks by vertical.
- **Chicken-and-egg** — Start with supply (sellers) via direct outreach. Constrain geography or category initially.
- **Payments** — Stripe Connect for splits, escrow, payouts. Understand KYC requirements.
- **Trust mechanisms** — Reviews, verification badges, dispute resolution process.

See `builder-playbook.md` for cold-start tactics and unit economics modeling.

## Tax and Legal (All Roles)

- **Sellers:** 1099-K reporting at $600+ (US), VAT thresholds vary by EU country.
- **Cross-border:** Customs duties, prohibited items, export restrictions apply.
- **Platform ToS:** Each marketplace has restrictions. Violation = account suspension.

Consult a tax professional for jurisdiction-specific obligations.

References: `buyer-safety.md`, `seller-platforms.md`, `builder-playbook.md`
