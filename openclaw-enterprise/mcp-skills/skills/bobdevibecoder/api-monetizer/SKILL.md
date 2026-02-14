# api-monetizer

Packages micro-SaaS tool logic as paid APIs and lists them on RapidAPI and similar marketplaces.

## Overview

Takes the core conversion/generation logic from each micro-SaaS product and wraps it in a standalone API endpoint. Creates documentation, usage examples, and marketplace listings to generate API-based revenue alongside the web UI revenue.

## Usage

- "api create PRODUCT-SLUG" - Generate API wrapper for a product
- "api docs PRODUCT-SLUG" - Generate API documentation
- "api listing PRODUCT-SLUG" - Generate RapidAPI listing content
- "api stats" - Show API usage and revenue stats

## Pipeline

### Step 1: Extract Core Logic
For each micro-SaaS product, identify the core function:
- QR Code Generator: generateQR(text, options) -> image
- Invoice Generator: createInvoice(data) -> PDF
- Markdown Magic: convertMarkdown(input, format) -> output
- JSON Formatter: formatJSON(input, indent) -> formatted
- Base64 Encoder: encode/decode(input) -> output

### Step 2: Create API Route
Add an API route to the existing Next.js project:
/src/app/api/v1/[endpoint]/route.ts

API route structure:
- Validate API key from header (X-API-Key)
- Rate limit: 100 requests/day free, unlimited on paid
- Parse input from request body
- Call core logic function
- Return JSON response with result

### Step 3: API Key Management
Store API keys in Supabase (if available) or in a simple JSON file:
/home/milad/PRODUCT-SLUG/api-keys.json

Tiers:
- Free: 100 requests/day, basic features
- Pro ($9/mo via Stripe): 10,000 requests/day, all features
- Enterprise ($49/mo): 100,000 requests/day, priority support, SLA

### Step 4: Generate Documentation
Create OpenAPI/Swagger spec for each API:
- Endpoint URL
- Authentication method
- Request/response schema with examples
- Error codes
- Rate limit info
- Code examples in: curl, JavaScript, Python

### Step 5: RapidAPI Listing
Generate listing content:
- Title: "[Tool Name] API - [one-line benefit]"
- Description: 200 words covering use cases
- Category selection
- Pricing tiers mapped to RapidAPI plans
- Example requests/responses

Save to: /home/milad/.openclaw/workspace/skills/api-monetizer/listings/PRODUCT-SLUG/

## Revenue Model

| Tier | Price | Requests/Day | Revenue Target |
|------|-------|-------------|----------------|
| Free | $0 | 100 | Lead gen |
| Pro | $9/mo | 10,000 | Main revenue |
| Enterprise | $49/mo | 100,000 | High-value |

## Important Notes

- API monetization is an additional revenue stream, not a replacement for web UI
- Human uploads the actual RapidAPI listing (bot prepares everything)
- Track API usage separately from web UI usage
- API keys must be kept secure, never logged in plain text
