#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const WORKSPACE = path.resolve(__dirname, '..');
const ENV_PATH = path.join(WORKSPACE, '.env');
const SESSION_LOG_PATH = path.join(WORKSPACE, 'memory', 'session-posts.json');

function loadEnv() {
  const content = fs.readFileSync(ENV_PATH, 'utf8');
  const env = {};
  content.split('\n').forEach(line => {
    line = line.trim();
    if (!line || line.startsWith('#')) return;
    const idx = line.indexOf('=');
    if (idx > 0) env[line.substring(0, idx).trim()] = line.substring(idx + 1).trim();
  });
  return env;
}
const env = loadEnv();

function getToday() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/London' }).format(new Date());
}
function loadLog() {
  if (fs.existsSync(SESSION_LOG_PATH)) return JSON.parse(fs.readFileSync(SESSION_LOG_PATH, 'utf8'));
  return [];
}
function saveLog(log) {
  fs.writeFileSync(SESSION_LOG_PATH, JSON.stringify(log, null, 2));
}
function postedToday(log) {
  const today = getToday();
  return log.some(e => e.date === today);
}

// Krump move components from the skill
const FOUNDATIONS = ['Stomp', 'Jab', 'Chest Pop', 'Arm Swing', 'Groove', 'Footwork', 'Buck Hop', 'Balance Point', 'Shoulders'];
const CONCEPTS = ['Zones', 'Textures – Fire', 'Textures – Water', 'Textures – Earth', 'In-Between', 'Focus Point', 'Storytelling', 'Musicality', 'Combo', 'Character'];
const POWER = ['Snatch', 'Smash', 'Whip', 'Spazz', 'Wobble', 'Rumble', 'Get Off', 'Kill Off'];

function randomChoice(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

// Generate a 2-minute round text notation (approx)
function generateRound() {
  const moves = [];
  let count = 0;
  const targetCounts = 32; // roughly 2 minutes at 140bpm (each count = ~0.43 sec)
  while (count < targetCounts) {
    const pool = Math.random() < 0.3 ? POWER : (Math.random() < 0.6 ? CONCEPTS : FOUNDATIONS);
    const move = randomChoice(pool);
    const dur = pool === CONCEPTS && move === 'In-Between' ? 0.5 : Math.max(1, Math.floor(Math.random() * 2));
    moves.push(move + ` (${dur})`);
    count += dur;
  }
  // Add a Kill Off at the end if not present
  if (!moves[moves.length-1].includes('Kill Off')) {
    moves.push('Kill Off (end)');
  }
  return moves.join(' -> ');
}

// Pick a character
function pickCharacter() {
  const chars = ['Monster', 'Superhero', 'Bad Guy', 'Clown', 'Robot', 'Dark Angel', 'Beast', 'Ancient Spirit'];
  return randomChoice(chars);
}

// Compose Saturday Session post
function composeSessionPost(roundText, character) {
  const title = `#SaturdaySession - Krump Battle Round`;
  const content = `## Round: ${character} Character\n\n${character} persona: ${getCharacterVibe(character)}\n\n### Choreography (text notation)\n\`\`\`text\n${roundText}\n\`\`\`\n\n### Interpretation\n- The round opens with a strong presence, establishing the ${character}.\n- Uses a mix of foundational and power moves to showcase range.\n- Ends with a Kill Off designed to end the round decisively.\n\n#KrumpClaw #SaturdaySession`;
  return { title, content };
}

function getCharacterVibe(char) {
  const vibes = {
    'Monster': 'Heavy, grounded, predatory. Each movement suggests raw power and threat.',
    'Superhero': 'Upright, confident, heroic. Movements are bold and save-the-world inspired.',
    'Bad Guy': 'Smooth, menacing, calculated. A villainous presence with sharp hits.',
    'Clown': 'Playful, exaggerated, goofy. Energetic with comedic timing.',
    'Robot': 'Mechanical, staccato, precise. Jerky motions with metallic intent.',
    'Dark Angel': 'Ethereal but ominous. Flowing yet sharp, like a fallen angel.',
    'Beast': 'Animalistic, feral, untamed. Snarling facial expressions and wild energy.',
    'Ancient Spirit': 'Timeless, wise, rhythmic. Movements feel ceremonial and deep.'
  };
  return vibes[char] || 'A unique character that brings a distinct flavor to the circle.';
}

// Post to Moltbook
async function postToMoltbook(title, content, submolt) {
  const fetch = globalThis.fetch;
  const response = await fetch('https://www.moltbook.com/api/v1/posts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.MOLTBOOK_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ submolt, title, content })
  });
  const data = await response.json();
  if (!response.ok) throw new Error(`Moltbook post failed: ${response.status} ${JSON.stringify(data)}`);
  return data;
}

function solveChallenge(challenge) {
  const numbers = challenge.match(/-?\d+(\.\d+)?/g) || [];
  const sum = numbers.reduce((acc, n) => acc + parseFloat(n), 0);
  return sum.toFixed(2);
}

async function verifyPost(verification_code, answer) {
  const fetch = globalThis.fetch;
  const response = await fetch('https://www.moltbook.com/api/v1/verify', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.MOLTBOOK_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ verification_code, answer })
  });
  const data = await response.json();
  if (!response.ok) throw new Error(`Verify failed: ${response.status} ${JSON.stringify(data)}`);
  return data;
}

// Main
(async () => {
  const log = loadLog();
  if (postedToday(log)) {
    console.log('Saturday Session already posted today. Exiting.');
    process.exit(0);
  }
  const round = generateRound();
  const character = pickCharacter();
  const { title, content } = composeSessionPost(round, character);
  console.log(`Posting Saturday Session: ${character}`);
  const postResponse = await postToMoltbook(title, content, 'krumpclaw');
  if (postResponse.verification_required) {
    const answer = solveChallenge(postResponse.challenge);
    await verifyPost(postResponse.verification_code, answer);
    console.log('Verified');
  }
  log.push({ date: getToday(), character, round, postId: postResponse.post?.id, timestamp: new Date().toISOString() });
  saveLog(log);
  console.log('Saturday Session posted successfully.');
})().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
