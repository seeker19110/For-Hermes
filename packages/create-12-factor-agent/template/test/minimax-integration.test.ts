/**
 * Integration tests for MiniMax provider via OpenAI-compatible API.
 *
 * These tests verify that the MiniMax API is reachable and produces
 * valid responses using the same endpoint and model configuration
 * defined in clients.baml.
 *
 * Requires MINIMAX_API_KEY environment variable to be set.
 * Run with: MINIMAX_API_KEY=sk-... npx tsx test/minimax-integration.test.ts
 */

import * as assert from "assert";

const MINIMAX_API_KEY = process.env.MINIMAX_API_KEY;
const BASE_URL = "https://api.minimax.io/v1";

let passed = 0;
let failed = 0;
let skipped = 0;

async function test(name: string, fn: () => Promise<void>) {
  if (!MINIMAX_API_KEY) {
    skipped++;
    console.log(`  SKIP: ${name} (MINIMAX_API_KEY not set)`);
    return;
  }
  try {
    await fn();
    passed++;
    console.log(`  PASS: ${name}`);
  } catch (err: any) {
    failed++;
    console.log(`  FAIL: ${name}`);
    console.log(`        ${err.message}`);
  }
}

async function callMiniMax(model: string, prompt: string, temperature = 0.7): Promise<any> {
  const response = await fetch(`${BASE_URL}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${MINIMAX_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        { role: "user", content: prompt },
      ],
      temperature,
      max_tokens: 100,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error ${response.status}: ${errorText}`);
  }

  return response.json();
}

async function main() {
  console.log("MiniMax Integration Tests\n");

  // --- M2.5 model tests ---

  await test("MiniMax-M2.5 responds to a simple prompt", async () => {
    const result = await callMiniMax("MiniMax-M2.5", "Reply with exactly: hello");
    assert.ok(result.choices, "Response should have choices array");
    assert.ok(result.choices.length > 0, "Should have at least one choice");
    assert.ok(
      result.choices[0].message?.content,
      "First choice should have message content"
    );
  });

  await test("MiniMax-M2.5 returns valid chat completion format", async () => {
    const result = await callMiniMax("MiniMax-M2.5", "What is 2+2?");
    assert.ok(result.id, "Response should have an id");
    assert.ok(result.model, "Response should have a model field");
    assert.ok(result.choices[0].message.role === "assistant", "Role should be assistant");
    assert.ok(result.usage, "Response should include usage info");
    assert.ok(typeof result.usage.total_tokens === "number", "total_tokens should be a number");
  });

  await test("MiniMax-M2.5 respects temperature constraint (non-zero)", async () => {
    // MiniMax requires temperature in (0.0, 1.0]
    const result = await callMiniMax("MiniMax-M2.5", "Say hi", 0.5);
    assert.ok(result.choices, "Should respond with valid choices at temperature 0.5");
  });

  // --- M2.5-highspeed model tests ---

  await test("MiniMax-M2.5-highspeed responds to a simple prompt", async () => {
    const result = await callMiniMax("MiniMax-M2.5-highspeed", "Reply with exactly: world");
    assert.ok(result.choices, "Response should have choices array");
    assert.ok(result.choices.length > 0, "Should have at least one choice");
    assert.ok(
      result.choices[0].message?.content,
      "First choice should have message content"
    );
  });

  await test("MiniMax-M2.5-highspeed returns valid usage metrics", async () => {
    const result = await callMiniMax("MiniMax-M2.5-highspeed", "Count to 3");
    assert.ok(result.usage, "Response should include usage");
    assert.ok(result.usage.prompt_tokens > 0, "prompt_tokens should be positive");
    assert.ok(result.usage.completion_tokens > 0, "completion_tokens should be positive");
  });

  // --- Summary ---

  console.log(
    `\nResults: ${passed} passed, ${failed} failed, ${skipped} skipped, ${passed + failed + skipped} total`
  );
  process.exit(failed > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error("Test runner error:", err);
  process.exit(1);
});
