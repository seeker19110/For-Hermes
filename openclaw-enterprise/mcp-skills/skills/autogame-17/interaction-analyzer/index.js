#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const minimist = require('minimist');

const args = minimist(process.argv.slice(2));

if (args.help || !args.file) {
  console.log(`
Usage: interaction-analyzer --file <path/to/log.json> [--output <path/to/report.md>]

Options:
  --file    Path to the interaction log file (JSON array of messages)
  --output  Path to save the generated markdown report (default: stdout)
  --help    Show this help message
`);
  process.exit(0);
}

const inputFile = path.resolve(args.file);
const outputFile = args.output ? path.resolve(args.output) : null;

if (!fs.existsSync(inputFile)) {
  console.error(`Error: File not found: ${inputFile}`);
  process.exit(1);
}

try {
  const data = fs.readFileSync(inputFile, 'utf8');
  const messages = JSON.parse(data);

  if (!Array.isArray(messages)) {
    throw new Error('Input file must be a JSON array of messages');
  }

  const analysis = analyzeMessages(messages);
  const report = generateMarkdown(analysis);

  if (outputFile) {
    fs.mkdirSync(path.dirname(outputFile), { recursive: true });
    fs.writeFileSync(outputFile, report);
    console.log(`Report saved to ${outputFile}`);
  } else {
    console.log(report);
  }

} catch (err) {
  console.error(`Error processing file: ${err.message}`);
  process.exit(1);
}

function analyzeMessages(messages) {
  const stats = {
    total: messages.length,
    userCount: 0,
    assistantCount: 0,
    userWords: 0,
    assistantWords: 0,
    timeDistribution: new Array(24).fill(0),
    sentiment: { positive: 0, negative: 0, neutral: 0 },
    topKeywords: {}
  };

  const stopWords = new Set(['the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'for', 'with', 'on', 'that', 'this', 'at', 'from', 'be', 'by', 'an', 'or', 'as', 'are', 'was', 'if', 'but', 'not', 'can', 'you', 'i', 'we', 'my', 'me', 'your', 'so', 'do', 'no', 'yes', 'ok', 'okay', 'what', 'how', 'why', 'when', 'where', 'who', 'which', 'all', 'any', 'some', 'one', 'use', 'get', 'set', 'run', 'call', 'make', 'create', 'update', 'delete', 'check', 'list', 'show', 'read', 'write', 'edit', 'exec', 'process', 'tool', 'skills', 'skill', 'agent', 'openclaw', 'feishu', 'user', 'assistant', 'system', 'json', 'markdown', 'code', 'file', 'files', 'path', 'content', 'message', 'text', 'data', 'output', 'input', 'log', 'error', 'status', 'command', 'result', 'response', 'request', 'action', 'task', 'step', 'time', 'date', 'day', 'hour', 'minute', 'second', 'week', 'month', 'year', 'now', 'today', 'tomorrow', 'yesterday', 'please', 'thanks', 'thank', 'sorry', 'hello', 'hi', 'hey', 'good', 'bad', 'great', 'awesome', 'nice', 'cool', 'love', 'hate', 'like', 'want', 'need', 'should', 'would', 'could', 'will', 'may', 'might', 'must', 'have', 'has', 'had', 'do', 'did', 'does', 'go', 'went', 'gone', 'see', 'saw', 'seen', 'know', 'knew', 'known', 'think', 'thought', 'feel', 'felt', 'say', 'said', 'tell', 'told', 'ask', 'asked', 'answer', 'answered', 'reply', 'replied', 'send', 'sent', 'receive', 'received']);

  messages.forEach(msg => {
    // Count roles
    if (msg.role === 'user') stats.userCount++;
    else if (msg.role === 'assistant') stats.assistantCount++;

    // Time distribution (if timestamp exists)
    if (msg.timestamp) {
      const date = new Date(msg.timestamp);
      if (!isNaN(date.getTime())) {
        stats.timeDistribution[date.getHours()]++;
      }
    }

    // Word count & keywords
    const content = msg.content || '';
    const words = content.toLowerCase().replace(/[^\w\s]/g, '').split(/\s+/).filter(w => w.length > 2);
    
    if (msg.role === 'user') stats.userWords += words.length;
    else if (msg.role === 'assistant') stats.assistantWords += words.length;

    words.forEach(word => {
      if (!stopWords.has(word)) {
        stats.topKeywords[word] = (stats.topKeywords[word] || 0) + 1;
      }
    });

    // Simple sentiment
    const text = content.toLowerCase();
    if (text.includes('thanks') || text.includes('good') || text.includes('great') || text.includes('awesome')) {
      stats.sentiment.positive++;
    } else if (text.includes('error') || text.includes('fail') || text.includes('bad') || text.includes('wrong')) {
      stats.sentiment.negative++;
    } else {
      stats.sentiment.neutral++;
    }
  });

  // Sort keywords
  stats.topKeywords = Object.entries(stats.topKeywords)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 20)
    .reduce((obj, [key, val]) => { obj[key] = val; return obj; }, {});

  return stats;
}

function generateMarkdown(stats) {
  const avgUserLength = stats.userCount ? (stats.userWords / stats.userCount).toFixed(1) : 0;
  const avgAssistantLength = stats.assistantCount ? (stats.assistantWords / stats.assistantCount).toFixed(1) : 0;

  let md = `# Interaction Analysis Report\n\n`;
  md += `**Total Messages:** ${stats.total}\n`;
  md += `**User Messages:** ${stats.userCount} (Avg Length: ${avgUserLength} words)\n`;
  md += `**Assistant Messages:** ${stats.assistantCount} (Avg Length: ${avgAssistantLength} words)\n\n`;

  md += `## Sentiment Overview\n`;
  md += `- Positive: ${stats.sentiment.positive}\n`;
  md += `- Negative: ${stats.sentiment.negative}\n`;
  md += `- Neutral: ${stats.sentiment.neutral}\n\n`;

  md += `## Top Keywords\n`;
  Object.entries(stats.topKeywords).forEach(([word, count]) => {
    md += `- **${word}**: ${count}\n`;
  });

  md += `\n## Time Distribution (Last 24h)\n`;
  md += `| Hour | Count |\n|---|---|\n`;
  stats.timeDistribution.forEach((count, hour) => {
    if (count > 0) md += `| ${hour}:00 | ${count} |\n`;
  });

  return md;
}
