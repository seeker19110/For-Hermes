#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { plan, simulate } = require('./domain');
const { visualize } = require('./visualizer');

const args = process.argv.slice(2);
const actionArg = args.indexOf('--action');
const domainArg = args.indexOf('--domain');
const problemArg = args.indexOf('--problem');
const outputArg = args.indexOf('--output');

const action = actionArg !== -1 ? args[actionArg + 1] : null;
const domainPath = domainArg !== -1 ? args[domainArg + 1] : null;
const problemPath = problemArg !== -1 ? args[problemArg + 1] : null;
const outputPath = outputArg !== -1 ? args[outputArg + 1] : null;

if (!action || !domainPath || !problemPath) {
  console.error('Usage: node index.js --action <visualize|simulate> --domain <domain.json> --problem <problem.json> [--output <file>]');
  process.exit(1);
}

const domain = JSON.parse(fs.readFileSync(domainPath, 'utf8'));
const problem = JSON.parse(fs.readFileSync(problemPath, 'utf8'));

if (action === 'visualize') {
  const result = visualize(domain, problem);
  if (outputPath) {
    fs.writeFileSync(outputPath, result);
    console.log(`Plan visualization written to ${outputPath}`);
  } else {
    console.log(result);
  }
} else if (action === 'simulate') {
  const result = simulate(domain, problem);
  console.log(JSON.stringify(result, null, 2));
} else {
  console.error(`Unknown action: ${action}`);
  process.exit(1);
}
