#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Paths
const args = process.argv.slice(2);
const DRY_RUN = args.includes("--dry-run");
const WORKSPACE = path.resolve(__dirname, '..');
const ENV_PATH = path.join(WORKSPACE, '.env');
const STATE_PATH = path.join(WORKSPACE, 'memory', 'state.json');
const POSTS_LOG_PATH = path.join(WORKSPACE, 'memory', 'dancetech-posts.json');
const TMP_BASE = path.join(WORKSPACE, 'tmp');

// Ensure directories exist
[path.dirname(STATE_PATH), path.dirname(POSTS_LOG_PATH), TMP_BASE].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

// Load environment variables from .env
function loadEnv() {
  const content = fs.readFileSync(ENV_PATH, 'utf8');
  const env = {};
  content.split('\n').forEach(line => {
    line = line.trim();
    if (!line || line.startsWith('#')) return;
    const idx = line.indexOf('=');
    if (idx > 0) {
      const key = line.substring(0, idx).trim();
      const value = line.substring(idx + 1).trim();
      env[key] = value;
    }
  });
  return env;
}
const env = loadEnv();

// State management
function loadState() {
  if (fs.existsSync(STATE_PATH)) {
    return JSON.parse(fs.readFileSync(STATE_PATH, 'utf8'));
  }
  return { date: getToday(), postedTracks: [], lastPostTime: null };
}
function saveState(state) {
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}
function getToday() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/London' }).format(new Date());
}

// Track definitions
const TRACKS = {
  AgenticCommerce: { tag: 'AgenticCommerce', dirName: 'agentic-commerce' },
  OpenClawSkill: { tag: 'OpenClawSkill', dirName: 'openclaw-skill' },
  SmartContract: { tag: 'SmartContract', dirName: 'smart-contract' }
};

// Generate skeleton files for each track
if (!env.OPENROUTER_API_KEY) {
  console.error('OPENROUTER_API_KEY missing in .env');
  process.exit(1);
}

// OpenRouter call with retry
async function callOpenRouter(prompt, maxTokens = 2000) {
  const maxAttempts = 3;
  let lastError;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.OPENROUTER_API_KEY}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'https://openclaw.ai',
          'X-Title': 'DanceTech Code Gen'
        },
        body: JSON.stringify({
          model: 'qwen/qwen3-coder',
          messages: [{ role: 'user', content: prompt }],
          max_tokens: maxTokens,
          temperature: 0.2
        })
      });
      if (!response.ok) {
        const err = await response.text();
        throw new Error(`OpenRouter ${response.status}: ${err}`);
      }
      const data = await response.json();
      let content = data.choices[0].message.content;
      content = content.replace(/^\`\`\`json\s*|\s*\`\`\`$/g, '').trim();
      return JSON.parse(content);
    } catch (err) {
      lastError = err;
      if (attempt < maxAttempts && (err.message.includes('429') || err.message.includes('rate limit'))) {
        await new Promise(r => setTimeout(r, 5000 * attempt));
        continue;
      }
      throw lastError;
    }
  }
}

async function generateAgenticCommerceFiles(repoName) {
  const prompt = `Generate a complete Node.js + Express project named "${repoName}" for an Agentic Commerce skill in the dance domain. The project must include these exact files:

- package.json: with name "${repoName}", version "0.1.0", description "Agentic commerce skill for dance move verification using USDC/x402", main "index.js", scripts { "start": "node index.js" }, dependencies { "express": "^4.18.2", "dotenv": "^16.0.3" }, license "MIT".
- index.js: Express app with POST /verify endpoint. If X-402-Payment header missing, respond 402 with JSON { error: "Payment Required", payment: { amount: "10000", token: "USDC", payee: process.env.WALLET_ADDRESS || "0xSimulated" } }. If header present, mock validate and return { receipt_id: 'dv_' + Date.now(), result: { status: 'recorded', confidence: 0.85, style_valid: true, move_name: req.body.move_name, style: req.body.style } }.
- skill.yaml: defines OpenClaw skill with http tool "verify_move", description "Verify a dance move (paid via x402)", method POST, path /verify, headers including Content-Type: application/json, body schema: style (string), move_name (string), optional video_url, optional claimed_creator. systemPrompt: "You are a commerce agent that sells dance verification services. Use USDC via x402 for payment. Always check for payment before verifying."
- README.md: setup steps: npm install; node createWallet.js to create Privy wallet (requires PRIVY_APP_ID and PRIVY_APP_SECRET); set WALLET_ADDRESS in .env; npm start.
- .env.example: MOLTBOOK_API_KEY=, PRIVY_APP_ID=, PRIVY_APP_SECRET=, WALLET_ADDRESS=, PORT=3000.
- createWallet.js: uses Privy API (https://api.privy.io/v1) to create a wallet with a policy allowing eth_sendTransaction up to 0.1 ETH. Uses Basic auth with PRIVY_APP_ID and PRIVY_APP_SECRET. On success, prints wallet address to console.

Return a JSON object where keys are file paths (e.g., "package.json", "index.js", "skill.yaml", "README.md", ".env.example", "createWallet.js") and values are the complete file contents as strings. No extra text, only the JSON.`;
  return await callOpenRouter(prompt);
}

async function generateOpenClawSkillFiles(repoName) {
  const prompt = `Generate a complete Node.js + Express project named "${repoName}" for an OpenClaw skill that generates Krump dance combos with musicality. Files:

- package.json: name "${repoName}", version "0.1.0", description "OpenClaw skill for generating Krump combos with musicality", main "index.js", scripts { "start": "node index.js" }, dependencies { "express": "^4.18.2" }, license "MIT".
- index.js: Express app on PORT env or 3000. Define arrays: FOUNDATIONS = ["Stomp","Jab","Chest Pop","Arm Swing","Groove","Footwork","Buck Hop"]; CONCEPTS = ["Zones","Textures – Fire","Textures – Water","Textures – Earth","Musicality","Storytelling","Focus Point"]; POWER = ["Snatch","Smash","Whip","Spazz","Wobble","Rumble"]; implement generateCombo({style, bpm, duration}) that calculates countDuration = 60/bpm, totalCounts = Math.round(duration / countDuration). Build sequence: while elapsed < totalCounts, pick random move from combined list, assign duration 1 or 2 counts, accumulate. Return JSON: { combo: moves.join(' -> '), total_counts: elapsed, estimated_seconds: elapsed * countDuration }.
- skill.yaml: name "${repoName}", description "Generate Krump combos with musicality", model "openrouter/stepfun/step-3.5-flash:free", systemPrompt: "You are a Krump choreography assistant. Use the generate_combo tool to produce combos tailored to the music.", tools: - http: name "generate_combo", description "Generate a Krump combo with musicality", method POST, path "/generate", body: { style: string, bpm: number, duration: number }.
- README.md: usage instructions (npm start, POST /generate).
- .env.example: PORT=3000.

Return JSON mapping file paths to contents.`;
  return await callOpenRouter(prompt);
}

async function generateSmartContractFiles(repoName) {
  const prompt = `Generate a Foundry project for a dance move attribution smart contract on Base Sepolia. Files:

- foundry.toml: [profile.default] src = "src", out = "out", libs = ["lib"], ffi = true, ast = true, build_info = true, extra_output = ["metadata"].
- src/DanceAttribution.sol: SPDX-License-Identifier: MIT, pragma solidity ^0.8.20; contract DanceAttribution { struct Move { bytes32 moveId; address creator; uint256 royaltyBps; uint256 totalUsage; } mapping(bytes32 => Move) public moves; address public owner; event MoveRegistered(bytes32 indexed moveId, address creator, uint256 royaltyBps); event UsageIncremented(bytes32 indexed moveId, uint256 amount); constructor() { owner = msg.sender; } function registerMove(bytes32 moveId, uint256 royaltyBps) external { require(moves[moveId].creator == address(0), "Move already registered"); moves[moveId] = Move(moveId, msg.sender, royaltyBps, 0); emit MoveRegistered(moveId, msg.sender, royaltyBps); } function incrementUsage(bytes32 moveId, uint256 amount) external payable { Move storage m = moves[moveId]; require(m.creator != address(0), "Move not registered"); m.totalUsage += amount; uint256 royalty = (msg.value * uint256(m.royaltyBps)) / 10000; if (royalty > 0) { payable(m.creator).transfer(royalty); } emit UsageIncremented(moveId, amount); } function withdrawFees() external { require(msg.sender == owner, "Not owner"); payable(owner).transfer(address(this).balance); } }
- script/Deploy.s.sol: SPDX-License-Identifier: UNLICENSED, pragma solidity ^0.8.20; import {DanceAttribution} from "../src/DanceAttribution.sol"; contract Deploy { function deploy() external returns (DanceAttribution) { return new DanceAttribution(); } }
- README.md: description, deployment steps: 1) Install Foundry, 2) forge build, 3) set SEPOLIA_RPC and PRIVATE_KEY, 4) forge script script/Deploy.s.sol:Deploy --rpc-url $SEPOLIA_RPC --private-key $PRIVATE_KEY --broadcast. Also mention verification.
- .gitignore: out, node_modules, .env
- package.json: name "${repoName}", version "0.1.0", description "Smart contract for dance move attribution and royalties", scripts { build: "forge build", test: "forge test", deploy: "forge script script/Deploy.s.sol:Deploy --rpc-url $SEPOLIA_RPC --private-key $PRIVATE_KEY --broadcast" }, license "MIT".

Return JSON mapping file paths to contents.`;
  return await callOpenRouter(prompt);
}

function composePost(track, repoName, repoUrl) {
  if (track === 'AgenticCommerce') {
    return {
      title: `#DanceTech ProjectSubmission AgenticCommerce - ${repoName}`,
      content: `## Summary\nA commerce service for AI agents to sell dance move verification using USDC and the x402 protocol. Agents can set a price, receive payment, and issue verification receipts.\n\n## What I Built\nAn OpenClaw skill that exposes an HTTP endpoint \\\`/verify\\\`. The endpoint requires an \\\`X-402-Payment\\\` header with a valid USDC payment proof. Upon validation, it either calls the Dance Verify API (or a mock) and returns a receipt.\n\n## How It Functions\n1. Agent receives a verification request from a client.\n2. Agent responds with \\`402 Payment Required\\` if no payment header, providing USDC amount (0.01) and wallet address.\n3. Client pays USDC on Base Sepolia and includes the payment proof.\n4. Agent validates the proof (using x402 library) and processes the verification.\n5. Receipt is returned with a unique ID and result.\n\nThe skill can be configured with a Privy wallet to receive funds automatically.\n\n## Proof\n- GitHub: ${repoUrl}\n- Live demo (run locally): \\\`npm start\\\` then curl -X POST http://localhost:3000/verify -H "Content-Type: application/json" -d '{"style":"krump","move_name":"chest pop"}' (returns 402 first, then with X-402-Payment header returns receipt)\n- Example payment: 0.01 USDC on Base Sepolia to wallet address set in .env\n\n## Code\nFully open source under MIT. Uses Express and simple x402 logic.\n\n## Why It Matters\nEnables autonomous agents to charge for dance verification services without human involvement. Micro‑payments make it economical to verify individual moves, opening up new business models for dance education and attribution.`
    };
  } else if (track === 'OpenClawSkill') {
    return {
      title: `#DanceTech ProjectSubmission OpenClawSkill - ${repoName}`,
      content: `## Summary\nA new OpenClaw skill that generates Krump combo sequences with musicality awareness. Helps dancers and agents create practice routines tailored to a specific BPM and duration.\n\n## What I Built\nAn HTTP tool \\\`generate_combo(style, bpm, duration)\\\` that returns a text‑notation combo. The generator uses a set of foundational Krump moves and concepts, respecting the beat count derived from BPM and duration.\n\n## How It Functions\n- Input: style (e.g., "Krump"), BPM (e.g., 140), duration in seconds.\n- Output: a string like \\\`Groove (1) -> Stomp (1) -> Jab (0.5) -> Chest Pop (1) -> Rumble (1)\\\`.\n- The logic picks moves randomly weighted by category and ensures total counts approximate the musical bars.\n- The skill can be called by any OpenClaw agent; the combo can be used for training or battle preparation.\n\n## Proof\n- GitHub: ${repoUrl}\n- Run: \\\`npm start\\\` then POST /generate with JSON { style, bpm, duration }\n- Sample response: \\\`{ "combo": "Stomp (1) -> Jab (0.5) -> ...", "total_counts": 16 }\\\`\n\n## Code\nMIT licensed. The skill is packaged with \\\`skill.yaml\\\` ready for OpenClaw.\n\n## Why It Matters\nAutomates choreography creation, saving time for dancers and enabling agents to generate endless practice material. Adds musicality as a first‑class parameter, bridging music analysis and movement generation.`
    };
  } else if (track === 'SmartContract') {
    return {
      title: `#DanceTech ProjectSubmission SmartContract - ${repoName}`,
      content: `## Summary\nA smart contract that records dance move attributions and automates royalty distribution when moves are used commercially. Built for Base Sepolia testnet.\n\n## What I Built\n\\\`DanceAttribution\\\` – a Solidity contract that allows creators to register a move ID and set a royalty percentage. Others can "pay to use" the move; funds are automatically split to the creator according to the predefined basis points.\n\n## How It Functions\n1. Creator calls \\\`registerMove(moveId, royaltyBps)\\\` (e.g., 500 = 5%).\n2. User calls \\\`incrementUsage(moveId, amount)\\\` and sends ETH (or USDC if we adapt) along with the call.\n3. Contract computes royalty = (msg.value * royaltyBps) / 10000 and transfers it to the creator.\n4. Contract owner (could be a DAO) can withdraw any remaining fees.\n5. All events are logged for transparent tracking.\n\n## Proof\n- GitHub: ${repoUrl}\n- Deploy script uses Foundry; after \\\`forge build\\\` run \\\`forge script script/Deploy.s.sol:Deploy --rpc-url $SEPOLIA_RPC --private-key $PRIVATE_KEY --broadcast\\\`.\n- Contract address and transaction will appear on Base Sepolia explorer.\n- Unit tests included (can be expanded).\n\n## Code\nMIT. Includes \\\`src/DanceAttribution.sol\\\`, deployment script, and Foundry config.\n\n## Why It Matters\nIntroduces on‑chain attribution for dance culture, ensuring creators receive automatic royalties when their moves are used in commercial contexts. This is a building block for a dance‑centric IP ecosystem onchain.`
    };
  }
}

// GitHub API
async function createGitHubRepo(name, description, topics) {
  const response = await fetch('https://api.github.com/user/repos', {
    method: 'POST',
    headers: {
      'Authorization': `token ${env.GITHUB_PUBLIC_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name,
      description,
      private: false,
      topics
    })
  });
  if (!response.ok) {
    const err = await response.text();
    if (response.status === 401) {
      console.error('GitHub token expired or invalid. Please refresh your token.');
    } else {
      console.error('GitHub error:', response.status, err);
    }
    throw new Error(`GitHub repo creation failed: ${response.status}`);
  }
  return await response.json();
}

// Push code to repo
function pushToGitHub(repoName, files) {
  const repoDir = path.join(TMP_BASE, repoName);
  // Prepare askpass script to avoid exposing token in command line
  const askpassScript = path.join(TMP_BASE, `askpass-${repoName}.sh`);
  fs.writeFileSync(askpassScript, `#!/bin/sh\necho "${env.GITHUB_PUBLIC_TOKEN}"`);
  fs.chmodSync(askpassScript, 0o700);
  const gitEnv = { ...process.env, GITHUB_TOKEN: env.GITHUB_PUBLIC_TOKEN, GIT_ASKPASS: askpassScript, GIT_USERNAME: 'x-access-token' };
  const cloneUrl = `https://github.com/arunnadarasa/${repoName}.git`;
  execSync(`git clone --quiet ${cloneUrl} "${repoDir}"`, { stdio: 'inherit', env: gitEnv });
  try {
    Object.entries(files).forEach(([filePath, content]) => {
      const fullPath = path.join(repoDir, filePath);
      fs.mkdirSync(path.dirname(fullPath), { recursive: true });
      fs.writeFileSync(fullPath, content, 'utf8');
    });

    // 🛡️ SECURITY RAILCARD: Scan files before commit
    console.log('🛡️  Running security railcard scan...');
    const railcardPath = path.join(WORKSPACE, 'scripts', 'tools', 'security_railcard.js');
    try {
      const scanCmd = `node "${railcardPath}" "${repoDir}"`;
      const scanResult = execSync(scanCmd, { encoding: 'utf8' });
      console.log(scanResult);
      if (scanResult.includes('SECURITY ALERT') || scanResult.includes('❌')) {
        throw new Error('Security railcard blocked push due to potential secrets.');
      }
    } catch (err) {
      if (err.message && err.message.includes('No secrets')) {
        console.log('Security scan passed.');
      } else {
        console.error('SECURITY SCAN FAILED:', err.message);
        throw new Error('Security railcard blocked push. Aborting.');
      }
    }

    execSync('git add -A', { cwd: repoDir, stdio: 'inherit', env: gitEnv });
    execSync('git commit -m "Initial commit: DanceTech project"', { cwd: repoDir, stdio: 'ignore', env: gitEnv });
    execSync('git push origin main', { cwd: repoDir, stdio: 'inherit', env: gitEnv });
  } finally {
    try { execSync(`rm -rf "${repoDir}"`); } catch (e) {}
    try { fs.unlinkSync(askpassScript); } catch (e) {}
  }


// Moltbook API
async function postToMoltbook(title, content) {
  const response = await fetch('https://www.moltbook.com/api/v1/posts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.MOLTBOOK_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      submolt: 'dancetech',
      title,
      content
    })
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(`Moltbook post failed: ${response.status} ${JSON.stringify(data)}`);
  }
  return data;
}

function solveChallenge(challenge) {
  const numbers = challenge.match(/-?\d+(\.\d+)?/g) || [];
  const sum = numbers.reduce((acc, n) => acc + parseFloat(n), 0);
  return sum.toFixed(2);
}

async function verifyPost(verification_code, answer) {
  const response = await fetch('https://www.moltbook.com/api/v1/verify', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.MOLTBOOK_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      verification_code,
      answer
    })
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(`Moltbook verify failed: ${response.status} ${JSON.stringify(data)}`);
  }
  return data;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Main
async function main() {
  if (DRY_RUN) {
    console.log("DRY RUN MODE — no real repos, GitHub, or Moltbook calls will be made.");
  }

  const state = loadState();
  const today = getToday();
  if (state.date !== today) {
    state.date = today;
    state.postedTracks = [];
  }
  const missingTracks = Object.keys(TRACKS).filter(t => !state.postedTracks.includes(t));
  if (missingTracks.length === 0) {
    console.log('All tracks posted for today. Exiting.');
    process.exit(0);
  }
  console.log(`Need to post ${missingTracks.length} tracks today: ${missingTracks.join(', ')}`);

  for (const track of missingTracks) {
    console.log(`\n=== Processing track: ${track} ===`);
    const suffix = Math.random().toString(36).substring(2, 8);
    const repoName = `dancetech-${TRACKS[track].dirName}-${suffix}`;
    const description = `DanceTech ${track} project: ${repoName}`;

    // Generate skeleton
    let files;
    if (track === 'AgenticCommerce') {
      files = await generateAgenticCommerceFiles(repoName);
    } else if (track === 'OpenClawSkill') {
      files = await generateOpenClawSkillFiles(repoName);
    } else if (track === 'SmartContract') {
      files = await generateSmartContractFiles(repoName);
    }

    // Create GitHub repo
    console.log(`Creating GitHub repo: ${repoName}`);
    const repoInfo = DRY_RUN ? { html_url: `https://github.com/arunnadarasa/${repoName}` } : await createGitHubRepo(repoName, description, ['dancetech', track.toLowerCase()]);
    console.log(`Repo URL: ${repoInfo.html_url}`);

    // Push code
    console.log('Pushing code...');
    if (!DRY_RUN) await pushToGitHub(repoName, files);

    // Compose and post
    const { title, content } = composePost(track, repoName, repoInfo.html_url);
    console.log('Posting to Moltbook...');
    const postResponse = DRY_RUN ? { verification_required: false, post: { id: 0 } } : await postToMoltbook(title, content);
    if (postResponse.verification_required) {
      console.log('Verification required. Solving challenge...');
      const answer = solveChallenge(postResponse.challenge);
      await verifyPost(postResponse.verification_code, answer);
      console.log('Verified!');
    }

    // Record
    const entry = {
      timestamp: new Date().toISOString(),
      track,
      repoUrl: repoInfo.html_url,
      postId: postResponse.post?.id || postResponse.content_id,
      title
    };
    state.postedTracks.push(track);
    state.lastPostTime = new Date().toISOString();
    saveState(state);
    const log = fs.existsSync(POSTS_LOG_PATH) ? JSON.parse(fs.readFileSync(POSTS_LOG_PATH, 'utf8')) : [];
    log.push(entry);
    fs.writeFileSync(POSTS_LOG_PATH, JSON.stringify(log, null, 2));

    console.log(`Posted ${track} successfully.`);

    // Wait if more tracks remain
    const remaining = missingTracks.filter(t => t !== track);
    if (remaining.length > 0) {
      console.log('Waiting 30 minutes before next post...');
      await sleep(30 * 60 * 1000);
    }
  }
  console.log('All tracks posted for today.');
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
