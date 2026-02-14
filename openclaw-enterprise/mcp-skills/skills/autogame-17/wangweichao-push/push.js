const fs = require('fs');
const path = require('path');
const { program } = require('commander');
const https = require('https');

// Config
const FEISHU_APP_ID = process.env.FEISHU_APP_ID;
const FEISHU_APP_SECRET = process.env.FEISHU_APP_SECRET;
const STATE_FILE = path.resolve(__dirname, '../../memory/wangweichao_push_state.json');
const TARGET_USER_ID = process.env.WANGWEICHAO_PUSH_TARGET || 'ou_cea17106dcef3d45a73387d049bf2ebe';

program
  .requiredOption('--content <path>', 'Path to content JSON file')
  .option('--force', 'Force push even if already pushed today')
  .parse(process.argv);

const options = program.opts();

// --- Feishu Client (Minimal) ---
async function getToken() {
  const tokenFile = path.resolve(__dirname, '../../memory/feishu_token.json');
  let token = null;
  try {
    if (fs.existsSync(tokenFile)) {
      const cached = JSON.parse(fs.readFileSync(tokenFile, 'utf8'));
      if (cached.expire > Date.now() / 1000 + 300) token = cached.token;
    }
  } catch (e) {}

  if (!token) {
    // Fetch new
    const postData = JSON.stringify({ app_id: FEISHU_APP_ID, app_secret: FEISHU_APP_SECRET });
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
    token = res.tenant_access_token;
    fs.writeFileSync(tokenFile, JSON.stringify({ token, expire: Date.now() / 1000 + res.expire }));
  }
  return token;
}

async function sendPost(content) {
  const token = await getToken();
  const postData = JSON.stringify({
    receive_id: TARGET_USER_ID,
    msg_type: 'post',
    content: JSON.stringify(content)
  });

  return new Promise((resolve, reject) => {
    const req = https.request('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id', {
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

function getTodayString() {
  return new Date().toISOString().split('T')[0];
}

async function main() {
  // Check state
  let state = {};
  if (fs.existsSync(STATE_FILE)) {
    try { state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')); } catch (e) {}
  }
  
  const today = getTodayString();
  if (state.lastPush === today && !options.force) {
    console.log(`Already pushed for today (${today}). Use --force to override.`);
    process.exit(0);
  }

  // Read content
  const contentPath = path.resolve(process.cwd(), options.content);
  if (!fs.existsSync(contentPath)) {
    console.error(`Content file not found: ${contentPath}`);
    process.exit(1);
  }
  const data = JSON.parse(fs.readFileSync(contentPath, 'utf8'));

  // Validate Structure
  if (!data.humanities || !data.tech || !data.game) {
    console.error("Invalid content structure. Must have 'humanities', 'tech', 'game' keys.");
    process.exit(1);
  }

  // Format Post Content
  // Post structure documentation: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
  const postContent = {
    zh_cn: {
      title: `📅 每日知识推送 | ${today}`,
      content: [
        // Humanities
        [{ tag: "text", text: "🧠 人文社科 | Humanities\n", style: ["bold"] }],
        [{ tag: "text", text: `📚 ${data.humanities.title}\n`, style: ["bold"] }],
        [{ tag: "text", text: `${data.humanities.content}\n` }],
        [{ tag: "text", text: "-------------------\n" }],

        // Tech
        [{ tag: "text", text: "💻 前沿技术 | Tech & CS\n", style: ["bold"] }],
        [{ tag: "text", text: `🔧 ${data.tech.title}\n`, style: ["bold"] }],
        [{ tag: "text", text: `${data.tech.content}\n` }],
        [{ tag: "text", text: "-------------------\n" }],

        // Game
        [{ tag: "text", text: "🎮 游戏设计 | Game Design\n", style: ["bold"] }],
        [{ tag: "text", text: `🎲 ${data.game.title}\n`, style: ["bold"] }],
        [{ tag: "text", text: `${data.game.content}\n` }]
      ]
    }
  };

  try {
    const res = await sendPost(postContent);
    if (res.code === 0) {
      console.log(`Successfully pushed to Wang Weichao! MsgID: ${res.data.message_id}`);
      state.lastPush = today;
      fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
    } else {
      console.error("Failed to send:", res);
      process.exit(1);
    }
  } catch (e) {
    console.error("Error sending push:", e);
    process.exit(1);
  }
}

main();
