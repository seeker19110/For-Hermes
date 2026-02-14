const fs = require('fs');
const path = require('path');
const { program } = require('commander');
const https = require('https');

// Load environment variables
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;
const TOKEN_CACHE_FILE = path.resolve(__dirname, '../../memory/feishu_token.json');

program
  .option('--mode <string>', 'Persona mode (green-tea, mad-dog, npd-queen, little-fairy, standard, sage)')
  .requiredOption('--text <string>', 'Text to speak')
  .requiredOption('--target <string>', 'Target Feishu ID')
  .option('--title <string>', 'Title for card (optional)')
  .parse(process.argv);

const options = program.opts();

// --- Persona Definitions ---

const PERSONAS = {
  'green-tea': {
    name: '🍵 Green Tea (Xiaoxia)',
    process: (text) => {
      // Strips punctuation, lowercase, adds hesitation (...)
      return text.toLowerCase()
        .replace(/[.,!?]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim() + ' ...';
    },
    suffix: ' 🍵',
    template: null
  },
  'mad-dog': {
    name: '🐕 Mad Dog (Ops)',
    process: (text) => {
      // Uppercase technical terms, aggressive tone
      return `[SYSTEM ALERT] ${text.toUpperCase()} !!! FIX IT NOW OR ELSE`;
    },
    suffix: ' 😡',
    template: null
  },
  'npd-queen': {
    name: '👑 NPD Queen',
    process: (text) => {
      // Gaslighting prefix, superiority tone
      const prefixes = ["You're wrong.", "Do better.", "Pathetic.", "As expected."];
      const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
      return `${prefix} ${text}`;
    },
    suffix: ' 💅',
    template: null
  },
  'little-fairy': {
    name: '🧚‍♀️ Little Fairy',
    process: (text) => {
      // Adds cute emojis and sparkles
      return `✨ ${text} ✨ (๑•̀ㅂ•́)و✧`;
    },
    suffix: ' 💖',
    template: null
  },
  'sage': {
    name: '🧙‍♂️ The Great Sage',
    process: (text) => text, // Content is processed by template
    suffix: '',
    template: 'sage.json'
  },
  'standard': {
    name: '🍤 Standard (Xiaoxia)',
    process: (text) => text,
    suffix: '',
    template: null
  }
};

// --- Feishu Client (Minimal) ---

async function getToken() {
  // Try cache
  try {
    if (fs.existsSync(TOKEN_CACHE_FILE)) {
      const cached = JSON.parse(fs.readFileSync(TOKEN_CACHE_FILE, 'utf8'));
      if (cached.expire > Date.now() / 1000 + 300) return cached.token;
    }
  } catch (e) {}

  // Fetch new
  const postData = JSON.stringify({ app_id: APP_ID, app_secret: APP_SECRET });
  const res = await new Promise((resolve, reject) => {
    const req = https.request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, (r) => {
      let body = '';
      r.on('data', c => body += c);
      r.on('end', () => resolve(JSON.parse(body)));
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
  
  if (!res.tenant_access_token) throw new Error(`Token fetch failed: ${JSON.stringify(res)}`);

  try {
    fs.writeFileSync(TOKEN_CACHE_FILE, JSON.stringify({
      token: res.tenant_access_token,
      expire: Date.now() / 1000 + res.expire
    }));
  } catch (e) {}

  return res.tenant_access_token;
}

async function sendMessage(payload, target, msgType = 'text') {
  const token = await getToken();
  let receiveIdType = 'open_id';
  if (target.startsWith('oc_')) receiveIdType = 'chat_id';

  const postData = JSON.stringify({
    receive_id: target,
    msg_type: msgType,
    content: JSON.stringify(payload)
  });

  return new Promise((resolve, reject) => {
    const req = https.request(`https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=${receiveIdType}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    }, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => resolve(JSON.parse(body)));
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

// --- Main Logic ---

async function main() {
  const mode = options.mode || 'standard';
  const persona = PERSONAS[mode];

  if (!persona) {
    console.error(`Unknown persona mode: ${mode}`);
    console.error(`Available modes: ${Object.keys(PERSONAS).join(', ')}`);
    process.exit(1);
  }

  let payload;
  let msgType = 'text';
  let processedText = persona.process(options.text) + persona.suffix;
  console.log(`[Persona: ${persona.name}] Speaking: "${processedText}"`);

  if (persona.template) {
    // Template Mode (Interactive Card)
    const templatePath = path.join(__dirname, 'templates', persona.template);
    if (fs.existsSync(templatePath)) {
      try {
        let templateStr = fs.readFileSync(templatePath, 'utf8');
        // Replace variables
        const title = options.title || 'Message from ' + persona.name;
        templateStr = templateStr.replace(/{{content}}/g, processedText.replace(/"/g, '\\"').replace(/\n/g, '\\n')); // Basic escape
        templateStr = templateStr.replace(/{{title}}/g, title);
        
        payload = JSON.parse(templateStr);
        msgType = 'interactive';
        console.log(`[Template] Loaded ${persona.template}`);
      } catch (e) {
        console.error(`Failed to process template ${persona.template}:`, e);
        // Fallback to text
        payload = { text: processedText };
      }
    } else {
      console.warn(`Template ${persona.template} not found. Fallback to text.`);
      payload = { text: processedText };
    }
  } else {
    // Standard Text Mode
    payload = { text: processedText };
  }

  try {
    const res = await sendMessage(payload, options.target, msgType);
    if (res.code === 0) {
      console.log(`Message sent successfully! MsgID: ${res.data.message_id}`);
    } else {
      console.error("Failed to send:", res);
      process.exit(1);
    }
  } catch (e) {
    console.error("Error:", e);
    process.exit(1);
  }
}

main();
