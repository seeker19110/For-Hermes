#!/usr/bin/env node

const axios = require('axios');
const { JSDOM } = require('jsdom');
const { Readability } = require('@mozilla/readability');
const TurndownService = require('turndown');
const fs = require('fs');
const path = require('path');
const url = require('url');

// Configuration
const MEMORY_DIR = path.resolve(__dirname, '../../memory/clippings');
if (!fs.existsSync(MEMORY_DIR)) {
  fs.mkdirSync(MEMORY_DIR, { recursive: true });
}

// Parse args
const args = process.argv.slice(2);
const targetUrl = args.find(arg => arg.startsWith('http'));
if (!targetUrl) {
  console.error('Usage: node skills/web-clipper/index.js <url>');
  process.exit(1);
}

async function clip(targetUrl) {
  try {
    console.log(`Fetching ${targetUrl}...`);
    const response = await axios.get(targetUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });

    const dom = new JSDOM(response.data, { url: targetUrl });
    const reader = new Readability(dom.window.document);
    const article = reader.parse();

    if (!article) {
      throw new Error('Readability failed to parse content.');
    }

    const turndownService = new TurndownService({
      headingStyle: 'atx',
      codeBlockStyle: 'fenced'
    });

    const markdown = turndownService.turndown(article.content);
    const date = new Date().toISOString().split('T')[0];
    const slug = article.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '')
      .substring(0, 50);

    const filename = `${date}-${slug}.md`;
    const filepath = path.join(MEMORY_DIR, filename);

    const frontmatter = `---
title: "${article.title.replace(/"/g, '\\"')}"
url: "${targetUrl}"
date: "${date}"
author: "${article.byline || 'Unknown'}"
---

# ${article.title}

${markdown}
`;

    fs.writeFileSync(filepath, frontmatter);
    console.log(`Saved to ${filepath}`);
    console.log(JSON.stringify({
      status: 'success',
      file: filepath,
      title: article.title
    }));

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

clip(targetUrl);