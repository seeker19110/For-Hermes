import express from 'express';
import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3100;

// Serve static files
app.use(express.static(path.join(__dirname, '../public')));

// Content API endpoint
app.get('/api/content/:slug', async (req, res) => {
  const { slug } = req.params;

  try {
    let contentPath: string;

    // Handle special cases
    if (slug === 'intro') {
      // Return a welcome message
      return res.send(`# Welcome to 12-Factor Agents

This interactive explorer helps you understand the principles for building reliable LLM applications.

## Getting Started

Select any factor from the sidebar to begin exploring!
`);
    } else if (slug === 'brief-history') {
      contentPath = path.join(__dirname, '../../content/brief-history-of-software.md');
    } else {
      // Regular factor content
      contentPath = path.join(__dirname, `../../content/${slug}.md`);
    }

    const content = await fs.readFile(contentPath, 'utf-8');
    res.type('text/markdown').send(content);
  } catch (error) {
    console.error(`Error loading content for ${slug}:`, error);
    res.status(404).send('# Content Not Found\n\nThe requested content could not be loaded.');
  }
});

// Image API endpoint
app.get('/api/image/:factorId', async (req, res) => {
  const { factorId } = req.params;

  try {
    // Map factor IDs to image filenames
    const imageMap: { [key: string]: string } = {
      '1': '110-natural-language-tool-calls.png',
      '2': '120-own-your-prompts.png',
      '3': '130-own-your-context-building.png',
      '4': '140-tools-are-just-structured-outputs.png',
      '5': '150-unify-state.png',
      '6': '160-pause-resume-with-simple-apis.png',
      '7': '170-contact-humans-with-tools.png',
      '8': '180-control-flow.png',
      '9': '190-factor-9-errors-static.png',
      '10': '1a0-small-focused-agents.png',
      '11': '1b0-trigger-from-anywhere.png',
      '12': '1c0-stateless-reducer.png'
    };

    const imageName = imageMap[factorId];
    if (!imageName) {
      return res.status(404).send('Image not found');
    }

    const imagePath = path.join(__dirname, `../../img/${imageName}`);

    // Check if file exists
    await fs.access(imagePath);

    res.sendFile(imagePath);
  } catch (error) {
    console.error(`Error loading image for factor ${factorId}:`, error);
    res.status(404).send('Image not found');
  }
});

// List all factors
app.get('/api/factors', async (req, res) => {
  const factors = [
    { id: 1, title: 'Natural Language to Tool Calls', slug: 'factor-01-natural-language-to-tool-calls' },
    { id: 2, title: 'Own Your Prompts', slug: 'factor-02-own-your-prompts' },
    { id: 3, title: 'Own Your Context Window', slug: 'factor-03-own-your-context-window' },
    { id: 4, title: 'Tools are Structured Outputs', slug: 'factor-04-tools-are-structured-outputs' },
    { id: 5, title: 'Unify Execution State', slug: 'factor-05-unify-execution-state' },
    { id: 6, title: 'Launch/Pause/Resume', slug: 'factor-06-launch-pause-resume' },
    { id: 7, title: 'Contact Humans with Tools', slug: 'factor-07-contact-humans-with-tools' },
    { id: 8, title: 'Own Your Control Flow', slug: 'factor-08-own-your-control-flow' },
    { id: 9, title: 'Compact Errors', slug: 'factor-09-compact-errors' },
    { id: 10, title: 'Small, Focused Agents', slug: 'factor-10-small-focused-agents' },
    { id: 11, title: 'Trigger from Anywhere', slug: 'factor-11-trigger-from-anywhere' },
    { id: 12, title: 'Stateless Reducer', slug: 'factor-12-stateless-reducer' }
  ];

  res.json(factors);
});

// Search endpoint
app.get('/api/search', async (req, res) => {
  const { q } = req.query;

  if (!q || typeof q !== 'string') {
    return res.status(400).json({ error: 'Query parameter "q" is required' });
  }

  try {
    const contentDir = path.join(__dirname, '../../content');
    const files = await fs.readdir(contentDir);
    const results: any[] = [];

    for (const file of files) {
      if (file.startsWith('factor-') && file.endsWith('.md')) {
        const filePath = path.join(contentDir, file);
        const content = await fs.readFile(filePath, 'utf-8');

        // Simple search - check if query exists in content
        if (content.toLowerCase().includes(q.toLowerCase())) {
          const slug = file.replace('.md', '');
          const lines = content.split('\n');
          const titleLine = lines.find(line => line.startsWith('#'));
          const title = titleLine ? titleLine.replace(/^#+\s*/, '') : slug;

          results.push({
            slug,
            title,
            preview: content.substring(0, 200) + '...'
          });
        }
      }
    }

    res.json(results);
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ error: 'Search failed' });
  }
});

// Code examples endpoint
app.get('/api/examples/:factor', async (req, res) => {
  const { factor } = req.params;

  try {
    // Map factors to demo files
    const demoPath = path.join(__dirname, '../../demos/ollama-agent-demo/src');
    const files = await fs.readdir(demoPath);

    const examples: any[] = [];

    for (const file of files) {
      if (file.endsWith('.ts')) {
        const filePath = path.join(demoPath, file);
        const content = await fs.readFile(filePath, 'utf-8');

        // Look for comments mentioning the factor
        if (content.includes(`Factor ${factor}`)) {
          examples.push({
            file,
            path: filePath,
            content
          });
        }
      }
    }

    res.json(examples);
  } catch (error) {
    console.error('Error loading examples:', error);
    res.status(500).json({ error: 'Failed to load examples' });
  }
});

app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 12-Factor Agents Explorer                           ║
║                                                           ║
║   Server running at: http://localhost:${PORT}              ║
║                                                           ║
║   📚 Explore all 12 factors for building reliable        ║
║      LLM applications in an interactive interface        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

API Endpoints:
  GET  /                          - Main explorer interface
  GET  /api/factors               - List all factors
  GET  /api/content/:slug         - Get factor content (markdown)
  GET  /api/image/:factorId       - Get factor diagram image
  GET  /api/search?q=query        - Search across all content
  GET  /api/examples/:factor      - Get code examples for a factor

Open http://localhost:${PORT} in your browser to start exploring!
`);
});
