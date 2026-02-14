# Marketplace Builder Playbook

## Business Model Options

| Model | Pros | Cons | Examples |
|-------|------|------|----------|
| Commission (10-20%) | Aligns with seller success | Requires transaction volume | Airbnb, Etsy |
| Subscription | Predictable revenue | Harder to acquire sellers | Amazon Pro |
| Listing fees | Low barrier | Low per-unit revenue | Craigslist premium |
| Lead generation | High margins | Quality control issues | Thumbtack |
| Freemium + ads | Easy acquisition | Ad revenue requires scale | Facebook Marketplace |

**Benchmark take rates by vertical:**
- Physical goods: 10-15%
- Services/gigs: 15-25%
- Rentals: 10-15%
- High-value (real estate, vehicles): 3-6%

## Solving the Chicken-and-Egg Problem

### Supply-First Strategy (Most Common)
1. **Constrain the market** — One city, one category, one niche
2. **Onboard supply manually** — Personal outreach, not ads
3. **Offer free/discounted listings** — Until you have 50-100 active sellers
4. **Create fake demand signals** — Show "X people looking for this" (carefully)
5. **Be the first buyer** — Make purchases yourself to prove the model

### Demand-First Strategy (Harder)
1. **Build audience first** — Content, community, newsletter
2. **Aggregate demand** — "Join waitlist for X"
3. **Approach sellers with committed buyers** — "I have 500 people who want..."

### Single-Player Mode
- Provide value to ONE side even without the other
- Example: OpenTable started as reservation management (restaurants got value alone)

## Payment Infrastructure

**Stripe Connect recommended for:**
- Split payments between marketplace and sellers
- KYC/identity verification handled
- 1099 generation for US sellers
- International payouts

**Key decisions:**
- Payout timing: Instant (expensive) vs. weekly (cheaper)
- Holding period: Release after delivery confirmation?
- Refund handling: Who eats the cost?
- Currency: Single vs. multi-currency support

**Escrow requirements:**
- Some jurisdictions require escrow licenses for holding funds
- Consider Stripe's built-in escrow vs. third-party

## Trust and Safety

### Verification Tiers
| Tier | Requirements | Badge |
|------|--------------|-------|
| Basic | Email verified | None |
| Verified | Phone + ID check | ✓ Verified |
| Trusted | Transaction history + reviews | ⭐ Trusted |
| Pro | Business verification | 🏢 Pro Seller |

### Review System
- Two-way reviews (buyer and seller)
- Review window: 14-30 days post-transaction
- Display: Average + count + recent
- Fake review detection: IP clustering, timing patterns, text analysis

### Dispute Resolution
1. Buyer reports issue
2. Seller has 48h to respond
3. Marketplace mediates if unresolved
4. Escalation to refund/account action
5. Appeal process (one chance)

## Unit Economics

**Key metrics:**
- GMV (Gross Merchandise Value)
- Net Revenue (GMV × take rate)
- CAC (Customer Acquisition Cost) — both sides
- LTV (Lifetime Value) — both sides
- Contribution margin per transaction

**Rough benchmarks for viability:**
- LTV:CAC ratio > 3:1
- Payback period < 12 months
- Gross margin > 50%
- Take rate sustainable for the vertical

**Formula for minimum viable GMV:**
```
Minimum GMV = Fixed Costs / (Take Rate × Gross Margin)

Example: $50K/month costs, 15% take, 70% margin
= $50,000 / (0.15 × 0.70) = $476K GMV/month needed
```

## Tech Stack Recommendations

**MVP (< $10K budget):**
- Sharetribe, Arcadier, or Kreezalid (no-code)
- Stripe Connect for payments
- Launch in 2-4 weeks

**Custom build:**
- Next.js + PostgreSQL + Stripe Connect
- Algolia or Meilisearch for search
- Cloudinary for images
- Timeline: 3-6 months

**Key features for v1:**
- User registration/auth
- Listing creation with photos
- Search/browse/filter
- Checkout/payments
- Messaging between parties
- Reviews
- Admin dashboard
