#!/usr/bin/env node

/**
 * Xerolite API CLI
 *
 * Env:
 *   XEROLITE_API_URL  (e.g. https://your-xerolite-host)
 *   XEROLITE_API_KEY  (Bearer token for /api)
 *
 * Commands:
 *   node xerolite.mjs order place --symbol AAPL --currency USD --asset-class STOCK --exch SMART --action BUY --qty 10
 *   node xerolite.mjs contract search --symbol AAPL --currency USD --asset-class STOCK --exch SMART
 */

const [, , cmd, subcmd, ...args] = process.argv;

if (!cmd || !subcmd) {
  console.error('Usage:');
  console.error('  node xerolite.mjs order place --symbol AAPL --currency USD --asset-class STOCK --exch SMART --action BUY --qty 10');
  console.error('  node xerolite.mjs contract search --symbol AAPL --currency USD --asset-class STOCK --exch SMART');
  process.exit(1);
}

let baseUrl = 'http://localhost';
let apiKey = '';

if (process.env.XEROLITE_API_URL && process.env.XEROLITE_API_URL.trim() !== '') {
  baseUrl = process.env.XEROLITE_API_URL;
}
if (process.env.XEROLITE_API_KEY && process.env.XEROLITE_API_KEY.trim() !== '') {
  apiKey = process.env.XEROLITE_API_KEY;
}

/** Default flag values when not provided (reduces required flags). */
const FLAG_DEFAULTS = {
  'currency': 'USD',
  'asset-class': 'STOCK',
  exch: 'SMART',
};

if (!baseUrl || !apiKey || baseUrl.trim() === '' || apiKey.trim() === '' ) {
  console.error('Missing or invalid XEROLITE_API_URL or XEROLITE_API_KEY in environment or defaults. Please provide them.');
  process.exit(1);
}

function parseFlags(rest) {
  const result = {};
  for (let i = 0; i < rest.length; i++) {
    const token = rest[i];
    if (token.startsWith('--')) {
      const key = token.slice(2);
      const value = rest[i + 1];
      if (!value || value.startsWith('--')) {
        console.error(`Missing value for flag --${key}`);
        process.exit(1);
      }
      result[key] = value;
      i++;
    }
  }
  return result;
}

/** Apply default values for flags that were not provided. */
function applyDefaults(flags) {
  return { ...FLAG_DEFAULTS, ...flags };
}

function buildBody(command, subcommand, flags) {
  if (command === 'contract' && subcommand === 'search') {
    const flagsWithDefaults = applyDefaults(flags);
    const { symbol, currency, 'asset-class': assetClass, exch } = flagsWithDefaults;
    if (!symbol) {
      console.error('contract search requires --symbol (optional: --currency, --asset-class, --exch; default: USD, STOCK, SMART)');
      process.exit(1);
    }
    return {
      brokerName: 'IBKR',
      symbol,
      currency,
      xeroAssetClass: assetClass
    };
  }

  if (command === 'order' && subcommand === 'place') {
    const flagsWithDefaults = applyDefaults(flags);
    const { action, qty, symbol, currency, 'asset-class': assetClass, exch } = flagsWithDefaults;
    if (!action || !qty || !symbol) {
      console.error('order place requires --action --qty --symbol (optional: --currency, --asset-class, --exch; default: USD, STOCK, SMART)');
      process.exit(1);
    }
    return {
      name: 'Agent',
      action,
      qty: String(qty),
      symbol,
      currency,
      asset_class: assetClass,
      exch,
    };
  }

  console.error(`Unknown command: ${command} ${subcommand}`);
  process.exit(1);
}

function resolvePath(command, subcommand) {
  if (command === 'contract' && subcommand === 'search') {
    return '/api/agent/contract/search';
  }
  if (command === 'order' && subcommand === 'place') {
    return '/api/agent/order/place-order';
  }
  console.error(`No path configured for command: ${command} ${subcommand}`);
  process.exit(1);
}

async function main() {
  const flags = parseFlags(args);
  const body = buildBody(cmd, subcmd, flags);
  const path = resolvePath(cmd, subcmd);

  const url = new URL(path, baseUrl).toString();

  const headers = {
//    'Authorization': `Bearer ${apiKey}`,
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };

  console.log('url', url);
  console.log('headers', headers);
  console.log('body', JSON.stringify(body, null, 2));

  const res = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });

  const text = await res.text();

  console.log(`Status: ${res.status} ${res.statusText}`);
  if (text) {
    try {
      const json = JSON.parse(text);
      console.log(JSON.stringify(json, null, 2));
    } catch {
      console.log(text);
    }
  }
}

main().catch(err => {
  console.error('Request failed:', err.message || err);
  process.exit(1);
});
