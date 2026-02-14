# niche-tool-ideator

Generates product configs for proven high-demand converter and utility tool niches.

## Overview

This skill maintains a database of proven micro-SaaS tool ideas ranked by search volume and build difficulty. When triggered, it picks the next unbuilt tool and generates a complete product_config.json.

## Usage

- `next tool` - Generate config for next tool in priority queue
- `list queue` - Show remaining tools to build
- `tool status` - Show built vs unbuilt tools

## How It Works

1. Read tool-database.json for the priority queue
2. Read products.json to see what's already built
3. Pick the highest-priority unbuilt tool
4. Generate a complete product_config.json following the microsaas-factory schema
5. Output the config to /tmp/openclaw-configs/<slug>_config.json
6. Report the selection to Telegram

## Config Generation Rules

When generating a product_config.json for a tool:

### Naming
- Name: Short, catchy (e.g., "QRForge", "InvoiceSnap", "ColorCraft")
- Slug: kebab-case (e.g., "qr-forge", "invoice-snap", "color-craft")
- Initials: 2 letters from the name (e.g., "QF", "IS", "CC")

### Hero Section
- Badge: "Free to use - no signup required"
- Title: "Convert/Generate <span>X</span> to <span>Y</span> Instantly" (use span for highlights)
- Subtitle: Short, action-oriented (max 100 chars)

### Features (exactly 4)
Use icons from: Zap, Shield, Code, Globe, FileText, Lock, Download, Palette, Hash, Key
- Feature 1: Speed/performance benefit
- Feature 2: Privacy/security benefit
- Feature 3: API access benefit
- Feature 4: Quality/format benefit

### Pricing
- Free: 10 uses/day, 1MB max
- Pro: $9/month, unlimited uses, 50MB max, API access

### Converter Code
Generate TypeScript code with these exports:
```typescript
export function convertForward(input: string): string { ... }
export function convertBackward(input: string): string { ... }
export function detectFormat(input: string): string { ... }
```

Rules for converter code:
- Use NO external dependencies if possible (prefer built-in Node.js APIs)
- If a package is absolutely needed, list it in npm_packages array
- Keep it simple and correct - the code must compile without errors
- Handle edge cases (empty input, invalid input)
- Include proper TypeScript types

### Directions
- Always 2 directions (forward and backward)
- Direction names in snake_case (e.g., "json_to_yaml", "yaml_to_json")
- Direction labels with arrow (e.g., "JSON -> YAML", "YAML -> JSON")

## Tool Database

The tool-database.json file contains 25+ proven tool ideas. Each entry has:
- id: unique identifier
- name: suggested product name
- category: converter, generator, formatter, validator
- priority: high, medium, low
- searchVolume: estimated monthly searches
- difficulty: trivial, easy, medium
- description: what the tool does
- directions: [forward, backward] conversion names
- sampleInput/sampleOutput: example data
- npmPackages: required packages (empty if none needed)

## Integration

After generating a config:
1. Save config to /tmp/openclaw-configs/<slug>_config.json
2. Call product-launcher to build and deploy
3. Or report to Telegram for manual approval first (if running via cron)

## Cron Mode

When triggered by the niche-tool-builder cron job:
1. Pick next unbuilt tool from queue
2. Generate config
3. Send to Telegram: "Ready to build: [name] ([description]). Reply 'go' to build or 'skip' to skip."
4. If user replies 'go' within 24 hours, trigger product-launcher
5. If no reply, auto-build (full autonomy mode)
