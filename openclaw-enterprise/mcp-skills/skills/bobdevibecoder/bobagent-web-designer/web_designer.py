#!/usr/bin/env python3
"""Web Designer Skill - AI-powered website generation service."""

import json
import sys
import os
from datetime import datetime, timezone

TEMPLATES = {
    "landing": {
        "name": "Landing Page",
        "description": "Modern dark SaaS/product landing page with glassmorphism effects",
        "sections": ["hero", "stats", "features", "cta", "footer"],
        "price_range": "$75-$150",
        "delivery": "1-2 hours",
        "files": ["page.tsx", "globals.css", "navbar.tsx", "hero.tsx"]
    },
    "portfolio": {
        "name": "Portfolio Site",
        "description": "Personal or agency portfolio with project showcase grid",
        "sections": ["hero", "about", "projects", "skills", "contact", "footer"],
        "price_range": "$150-$300",
        "delivery": "2-4 hours",
        "files": ["page.tsx", "globals.css", "navbar.tsx", "projects.tsx", "contact.tsx"]
    },
    "blog": {
        "name": "Blog Template",
        "description": "Content-focused blog with article cards and reading layout",
        "sections": ["header", "featured", "article-grid", "sidebar", "footer"],
        "price_range": "$100-$200",
        "delivery": "2-3 hours",
        "files": ["page.tsx", "globals.css", "navbar.tsx", "article-card.tsx", "layout.tsx"]
    },
    "docs": {
        "name": "Documentation Site",
        "description": "Clean documentation layout with sidebar navigation",
        "sections": ["sidebar-nav", "content-area", "breadcrumbs", "search", "footer"],
        "price_range": "$150-$300",
        "delivery": "3-5 hours",
        "files": ["page.tsx", "globals.css", "sidebar.tsx", "doc-content.tsx", "search.tsx"]
    },
    "pricing": {
        "name": "Pricing Page",
        "description": "Pricing tiers with feature comparison and CTA buttons",
        "sections": ["header", "pricing-cards", "feature-comparison", "faq", "cta"],
        "price_range": "$75-$150",
        "delivery": "1-2 hours",
        "files": ["page.tsx", "globals.css", "pricing-card.tsx", "faq.tsx"]
    },
    "saas": {
        "name": "Full SaaS Site",
        "description": "Complete SaaS marketing site with all sections",
        "sections": ["navbar", "hero", "stats", "features", "how-it-works", "testimonials", "pricing", "cta", "footer"],
        "price_range": "$200-$500",
        "delivery": "4-8 hours",
        "files": ["page.tsx", "globals.css", "navbar.tsx", "hero.tsx", "features.tsx", "pricing.tsx", "testimonials.tsx"]
    }
}

COLOR_PRESETS = {
    "purple": {"primary": "#6366f1", "accent": "#a78bfa", "example": "ConvertFlow"},
    "green": {"primary": "#10b981", "accent": "#06b6d4", "example": "MarkdownMagic"},
    "blue": {"primary": "#3b82f6", "accent": "#8b5cf6"},
    "orange": {"primary": "#f97316", "accent": "#fbbf24"},
    "pink": {"primary": "#ec4899", "accent": "#a855f7"},
    "red": {"primary": "#ef4444", "accent": "#f97316"},
    "cyan": {"primary": "#06b6d4", "accent": "#3b82f6"},
}


def cmd_templates():
    """List available templates."""
    print("=" * 60)
    print("  WEB DESIGNER - Available Templates")
    print("=" * 60)
    for key, t in TEMPLATES.items():
        print(f"\n  [{key}] {t['name']}")
        print(f"  {t['description']}")
        print(f"  Price: {t['price_range']} | Delivery: {t['delivery']}")
        print(f"  Sections: {', '.join(t['sections'])}")
        print(f"  Files: {', '.join(t['files'])}")
    print(f"\n{'=' * 60}")
    print("  Color Presets: " + ", ".join(COLOR_PRESETS.keys()))
    print("  Usage: web-designer generate <template> \"<brief>\"")
    print("=" * 60)


def cmd_quote(brief):
    """Generate a price quote."""
    brief_lower = brief.lower()

    complexity = "standard"
    price = 150
    delivery = "2-4 hours"

    if any(w in brief_lower for w in ["simple", "basic", "landing", "single page"]):
        complexity = "simple"
        price = 75
        delivery = "1-2 hours"
    elif any(w in brief_lower for w in ["full", "complete", "saas", "multi-page", "e-commerce"]):
        complexity = "complex"
        price = 350
        delivery = "4-8 hours"
    elif any(w in brief_lower for w in ["custom", "unique", "advanced", "enterprise"]):
        complexity = "premium"
        price = 500
        delivery = "6-12 hours"

    addons = []
    if any(w in brief_lower for w in ["animation", "animated", "motion"]):
        addons.append(("Custom animations", 50))
        price += 50
    if any(w in brief_lower for w in ["dark mode", "light mode", "theme toggle"]):
        addons.append(("Theme toggle (dark/light)", 75))
        price += 75
    if any(w in brief_lower for w in ["seo", "meta tags"]):
        addons.append(("SEO optimization", 25))
        price += 25
    if any(w in brief_lower for w in ["blog", "cms"]):
        addons.append(("Blog/CMS integration", 100))
        price += 100

    print("=" * 60)
    print("  WEB DESIGN QUOTE")
    print("=" * 60)
    print(f"\n  Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    print(f"  Brief: {brief}")
    print(f"  Complexity: {complexity.upper()}")
    print(f"\n  Base Price: ${price - sum(a[1] for a in addons)}")
    if addons:
        print("\n  Add-ons:")
        for name, cost in addons:
            print(f"    + {name}: ${cost}")
    print(f"\n  TOTAL: ${price}")
    print(f"  Delivery: {delivery}")
    print(f"\n  Includes:")
    for item in [
        "Next.js + Tailwind CSS source code",
        "Dark glassmorphism design system",
        "Responsive layout (mobile, tablet, desktop)",
        "Production-ready components",
        "Vercel deployment ready",
        "1 revision round included",
    ]:
        print(f"    + {item}")
    print(f"\n  Portfolio:")
    print(f"    > https://micro-saas-template-omega.vercel.app")
    print(f"    > https://markdown-magic-chi.vercel.app")
    print(f"\n{'=' * 60}")


def cmd_preview(template, brief):
    """Generate a preview description."""
    if template not in TEMPLATES:
        print(f"Error: Unknown template '{template}'. Use 'templates' to list.")
        return

    t = TEMPLATES[template]
    print("=" * 60)
    print(f"  DESIGN PREVIEW: {t['name']}")
    print("=" * 60)
    print(f"\n  Brief: {brief}")
    print(f"  Template: {t['name']}")
    print(f"  Design System: Dark Glassmorphism")
    print(f"\n  Sections:")
    for i, section in enumerate(t["sections"], 1):
        print(f"    {i}. {section.replace('-', ' ').title()}")
    print(f"\n  Files to generate:")
    for f in t["files"]:
        print(f"    > {f}")
    print(f"\n  Tech Stack: Next.js 14+ | Tailwind CSS v4 | TypeScript | Lucide Icons | Geist Font")
    print(f"\n  Design Features:")
    for feat in [
        "Dark background (#0a0a0f)",
        "Glassmorphism cards (backdrop-blur)",
        "Animated gradient text (shimmer)",
        "Floating orb effects",
        "Glow borders on hover",
        "Fade-in-up animations",
        "Mac-style window dots",
    ]:
        print(f"    * {feat}")
    print(f"\n  Price: {t['price_range']} | Delivery: {t['delivery']}")
    print(f"\n{'=' * 60}")


def cmd_generate(template, brief):
    """Generate website code from template and brief."""
    if template not in TEMPLATES:
        print(f"Error: Unknown template '{template}'. Use 'templates' to list.")
        return

    t = TEMPLATES[template]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    output_dir = f"/home/node/.openclaw/workspace/skills/web-designer/output/{ts}"

    print("=" * 60)
    print(f"  GENERATING: {t['name']}")
    print("=" * 60)
    print(f"\n  Brief: {brief}")
    print(f"  Template: {template}")
    print(f"  Output: {output_dir}")
    print(f"\n  Files to generate:")
    for f in t["files"]:
        print(f"    > {f}")
    print(f"\n  To complete generation, use the bot:")
    print(f"  > Generate a {t['name'].lower()} for: {brief}")
    print(f"  > Use the dark glassmorphism design system")
    print(f"  > Include sections: {', '.join(t['sections'])}")
    print(f"\n{'=' * 60}")


def cmd_colors():
    """List color presets."""
    print("=" * 60)
    print("  COLOR PRESETS")
    print("=" * 60)
    for name, c in COLOR_PRESETS.items():
        ex = f" (used by {c['example']})" if "example" in c else ""
        print(f"\n  [{name}]{ex}")
        print(f"    Primary: {c['primary']}")
        print(f"    Accent:  {c['accent']}")
    print(f"\n{'=' * 60}")


def main():
    if len(sys.argv) < 2:
        print("Usage: web-designer <command> [args]")
        print("Commands: templates, generate, preview, quote, colors")
        return

    command = sys.argv[1]

    if command == "templates":
        cmd_templates()
    elif command == "colors":
        cmd_colors()
    elif command == "quote" and len(sys.argv) >= 3:
        cmd_quote(" ".join(sys.argv[2:]))
    elif command == "preview" and len(sys.argv) >= 4:
        cmd_preview(sys.argv[2], " ".join(sys.argv[3:]))
    elif command == "generate" and len(sys.argv) >= 4:
        cmd_generate(sys.argv[2], " ".join(sys.argv[3:]))
    else:
        print(f"Unknown command or missing arguments: {command}")
        print("Commands: templates, generate, preview, quote, colors")


if __name__ == "__main__":
    main()
