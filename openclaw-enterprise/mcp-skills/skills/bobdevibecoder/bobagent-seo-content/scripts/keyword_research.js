#!/usr/bin/env node
/**
 * Keyword Research Helper
 * Generates keyword suggestions for a product type.
 * Usage: node keyword_research.js "<product_type>"
 * Example: node keyword_research.js "json csv converter"
 *
 * Output: JSON with keyword categories for blog content planning
 */

const productType = process.argv[2];

if (!productType) {
  console.error("Usage: node keyword_research.js '<product_type>'");
  process.exit(1);
}

// Common keyword patterns for tool-based micro-SaaS
const patterns = {
  howTo: [
    `how to ${productType}`,
    `how to ${productType} online`,
    `how to ${productType} free`,
    `${productType} tutorial`,
    `${productType} step by step`,
  ],
  best: [
    `best ${productType} tool`,
    `best ${productType} online`,
    `best free ${productType}`,
    `${productType} tools 2026`,
    `top ${productType} tools`,
  ],
  comparison: [
    `${productType} vs`,
    `${productType} alternatives`,
    `${productType} comparison`,
    `free vs paid ${productType}`,
  ],
  educational: [
    `what is ${productType}`,
    `${productType} explained`,
    `${productType} for beginners`,
    `why ${productType}`,
    `when to ${productType}`,
  ],
  longTail: [
    `${productType} online free no signup`,
    `${productType} api`,
    `${productType} bulk`,
    `${productType} large files`,
    `${productType} programmatically`,
    `${productType} command line`,
  ],
};

// Blog post ideas based on patterns
const blogIdeas = [
  {
    type: "how-to",
    title: `How to ${productType.charAt(0).toUpperCase() + productType.slice(1)}: Complete Guide (2026)`,
    primaryKeyword: patterns.howTo[0],
    secondaryKeywords: patterns.howTo.slice(1, 3),
    priority: 1,
    estimatedDifficulty: "medium",
  },
  {
    type: "listicle",
    title: `5 Best ${productType.charAt(0).toUpperCase() + productType.slice(1)} Tools in 2026 (Free & Paid)`,
    primaryKeyword: patterns.best[0],
    secondaryKeywords: patterns.best.slice(1, 3),
    priority: 1,
    estimatedDifficulty: "medium",
  },
  {
    type: "comparison",
    title: `Free vs Paid ${productType.charAt(0).toUpperCase() + productType.slice(1)} Tools: Which Is Better?`,
    primaryKeyword: patterns.comparison[3],
    secondaryKeywords: patterns.comparison.slice(0, 2),
    priority: 2,
    estimatedDifficulty: "low",
  },
  {
    type: "educational",
    title: `What Is ${productType.charAt(0).toUpperCase() + productType.slice(1)}? A Beginner's Guide`,
    primaryKeyword: patterns.educational[0],
    secondaryKeywords: patterns.educational.slice(1, 3),
    priority: 3,
    estimatedDifficulty: "low",
  },
  {
    type: "long-tail",
    title: `How to ${productType.charAt(0).toUpperCase() + productType.slice(1)} via API (Developer Guide)`,
    primaryKeyword: patterns.longTail[1],
    secondaryKeywords: patterns.longTail.slice(2, 4),
    priority: 2,
    estimatedDifficulty: "low",
  },
];

const result = {
  productType,
  generatedAt: new Date().toISOString(),
  keywords: patterns,
  blogIdeas,
  totalKeywords: Object.values(patterns).flat().length,
  contentPlan: {
    week1: [blogIdeas[0].title, blogIdeas[1].title],
    week2: [blogIdeas[2].title],
    week3: [blogIdeas[3].title],
    week4: [blogIdeas[4].title],
  },
};

console.log(JSON.stringify(result, null, 2));
