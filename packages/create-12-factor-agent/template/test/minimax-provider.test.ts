/**
 * Unit tests for MiniMax provider configuration in BAML clients.
 *
 * Validates that the clients.baml file correctly defines MiniMax
 * client entries with proper model names, API base URL, and
 * inclusion in round-robin/fallback strategies.
 *
 * Run with: npx tsx test/minimax-provider.test.ts
 */

import * as fs from "fs";
import * as path from "path";
import * as assert from "assert";

const BAML_PATH = path.join(__dirname, "..", "baml_src", "clients.baml");

function readBamlConfig(): string {
  return fs.readFileSync(BAML_PATH, "utf-8");
}

let passed = 0;
let failed = 0;

function test(name: string, fn: () => void) {
  try {
    fn();
    passed++;
    console.log(`  PASS: ${name}`);
  } catch (err: any) {
    failed++;
    console.log(`  FAIL: ${name}`);
    console.log(`        ${err.message}`);
  }
}

console.log("MiniMax Provider Unit Tests\n");

// --- MiniMax M2.7 client (latest, recommended) ---

test("MiniMaxM27 client block is defined", () => {
  const content = readBamlConfig();
  assert.ok(
    content.includes('client<llm> MiniMaxM27'),
    "clients.baml should define MiniMaxM27 client"
  );
});

test("MiniMaxM27 uses openai provider", () => {
  const content = readBamlConfig();
  const m27Block = content.split("client<llm> MiniMaxM27")[1].split("client<llm>")[0];
  assert.ok(
    m27Block.includes("provider openai"),
    "MiniMaxM27 should use openai provider"
  );
});

test("MiniMaxM27 uses correct model name", () => {
  const content = readBamlConfig();
  const m27Block = content.split("client<llm> MiniMaxM27")[1].split("client<llm>")[0];
  assert.ok(
    m27Block.includes('"MiniMax-M2.7"'),
    'MiniMaxM27 should use model "MiniMax-M2.7"'
  );
});

test("MiniMaxM27 uses MINIMAX_API_KEY env var", () => {
  const content = readBamlConfig();
  const m27Block = content.split("client<llm> MiniMaxM27")[1].split("client<llm>")[0];
  assert.ok(
    m27Block.includes("env.MINIMAX_API_KEY"),
    "MiniMaxM27 should reference env.MINIMAX_API_KEY"
  );
});

test("MiniMaxM27 uses correct base_url", () => {
  const content = readBamlConfig();
  const m27Block = content.split("client<llm> MiniMaxM27")[1].split("client<llm>")[0];
  assert.ok(
    m27Block.includes('"https://api.minimax.io/v1"'),
    "MiniMaxM27 should set base_url to https://api.minimax.io/v1"
  );
});

// --- MiniMax M2.7-highspeed client ---

test("MiniMaxM27Highspeed client block is defined", () => {
  const content = readBamlConfig();
  assert.ok(
    content.includes("client<llm> MiniMaxM27Highspeed"),
    "clients.baml should define MiniMaxM27Highspeed client"
  );
});

test("MiniMaxM27Highspeed uses correct model name", () => {
  const content = readBamlConfig();
  const hsBlock = content.split("client<llm> MiniMaxM27Highspeed")[1].split("client<llm>")[0];
  assert.ok(
    hsBlock.includes('"MiniMax-M2.7-highspeed"'),
    'MiniMaxM27Highspeed should use model "MiniMax-M2.7-highspeed"'
  );
});

test("MiniMaxM27Highspeed has retry policy", () => {
  const content = readBamlConfig();
  const hsBlock = content.split("client<llm> MiniMaxM27Highspeed")[1].split("client<llm>")[0];
  assert.ok(
    hsBlock.includes("retry_policy Exponential"),
    "MiniMaxM27Highspeed should have Exponential retry policy"
  );
});

test("MiniMaxM27Highspeed uses correct base_url", () => {
  const content = readBamlConfig();
  const hsBlock = content.split("client<llm> MiniMaxM27Highspeed")[1].split("client<llm>")[0];
  assert.ok(
    hsBlock.includes('"https://api.minimax.io/v1"'),
    "MiniMaxM27Highspeed should set base_url to https://api.minimax.io/v1"
  );
});

// --- MiniMax M2.5 client (previous generation) ---

test("MiniMaxM25 client block is defined", () => {
  const content = readBamlConfig();
  assert.ok(
    content.includes('client<llm> MiniMaxM25'),
    "clients.baml should define MiniMaxM25 client"
  );
});

test("MiniMaxM25 uses openai provider", () => {
  const content = readBamlConfig();
  const m25Block = content.split("client<llm> MiniMaxM25")[1].split("client<llm>")[0];
  assert.ok(
    m25Block.includes("provider openai"),
    "MiniMaxM25 should use openai provider"
  );
});

test("MiniMaxM25 uses correct model name", () => {
  const content = readBamlConfig();
  const m25Block = content.split("client<llm> MiniMaxM25")[1].split("client<llm>")[0];
  assert.ok(
    m25Block.includes('"MiniMax-M2.5"'),
    'MiniMaxM25 should use model "MiniMax-M2.5"'
  );
});

test("MiniMaxM25 uses MINIMAX_API_KEY env var", () => {
  const content = readBamlConfig();
  const m25Block = content.split("client<llm> MiniMaxM25")[1].split("client<llm>")[0];
  assert.ok(
    m25Block.includes("env.MINIMAX_API_KEY"),
    "MiniMaxM25 should reference env.MINIMAX_API_KEY"
  );
});

test("MiniMaxM25 uses correct base_url", () => {
  const content = readBamlConfig();
  const m25Block = content.split("client<llm> MiniMaxM25")[1].split("client<llm>")[0];
  assert.ok(
    m25Block.includes('"https://api.minimax.io/v1"'),
    "MiniMaxM25 should set base_url to https://api.minimax.io/v1"
  );
});

// --- MiniMax M2.5-highspeed client ---

test("MiniMaxM25Highspeed client block is defined", () => {
  const content = readBamlConfig();
  assert.ok(
    content.includes("client<llm> MiniMaxM25Highspeed"),
    "clients.baml should define MiniMaxM25Highspeed client"
  );
});

test("MiniMaxM25Highspeed uses correct model name", () => {
  const content = readBamlConfig();
  const hsBlock = content.split("client<llm> MiniMaxM25Highspeed")[1].split("client<llm>")[0];
  assert.ok(
    hsBlock.includes('"MiniMax-M2.5-highspeed"'),
    'MiniMaxM25Highspeed should use model "MiniMax-M2.5-highspeed"'
  );
});

test("MiniMaxM25Highspeed has retry policy", () => {
  const content = readBamlConfig();
  const hsBlock = content.split("client<llm> MiniMaxM25Highspeed")[1].split("client<llm>")[0];
  assert.ok(
    hsBlock.includes("retry_policy Exponential"),
    "MiniMaxM25Highspeed should have Exponential retry policy"
  );
});

test("MiniMaxM25Highspeed uses correct base_url", () => {
  const content = readBamlConfig();
  const hsBlock = content.split("client<llm> MiniMaxM25Highspeed")[1].split("client<llm>")[0];
  assert.ok(
    hsBlock.includes('"https://api.minimax.io/v1"'),
    "MiniMaxM25Highspeed should set base_url to https://api.minimax.io/v1"
  );
});

// --- Strategy inclusion (M2.7 is default in strategies) ---

test("MiniMaxM27Highspeed is included in round-robin strategy", () => {
  const content = readBamlConfig();
  const rrBlock = content.split("client<llm> CustomFast")[1].split("client<llm>")[0];
  assert.ok(
    rrBlock.includes("MiniMaxM27Highspeed"),
    "CustomFast round-robin should include MiniMaxM27Highspeed"
  );
});

test("MiniMaxM27 is included in fallback strategy", () => {
  const content = readBamlConfig();
  const fbBlock = content.split("client<llm> OpenaiFallback")[1].split("retry_policy")[0];
  assert.ok(
    fbBlock.includes("MiniMaxM27"),
    "OpenaiFallback should include MiniMaxM27"
  );
});

// --- Existing providers preserved ---

test("OpenAI clients are preserved", () => {
  const content = readBamlConfig();
  assert.ok(content.includes("client<llm> CustomGPT4o"), "CustomGPT4o should still exist");
  assert.ok(content.includes("client<llm> CustomGPT4oMini"), "CustomGPT4oMini should still exist");
});

test("Anthropic clients are preserved", () => {
  const content = readBamlConfig();
  assert.ok(content.includes("client<llm> CustomSonnet"), "CustomSonnet should still exist");
  assert.ok(content.includes("client<llm> CustomHaiku"), "CustomHaiku should still exist");
});

test("Retry policies are preserved", () => {
  const content = readBamlConfig();
  assert.ok(content.includes("retry_policy Constant"), "Constant retry policy should exist");
  assert.ok(content.includes("retry_policy Exponential"), "Exponential retry policy should exist");
});

// --- Summary ---

console.log(`\nResults: ${passed} passed, ${failed} failed, ${passed + failed} total`);
process.exit(failed > 0 ? 1 : 0);
