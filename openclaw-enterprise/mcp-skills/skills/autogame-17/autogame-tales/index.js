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
  .option('--title <string>', 'Title of the story')
  .option('--victim <string>', 'Victim name')
  .option('--desc <string>', 'Description of the event')
  .option('--target <string>', 'Target Feishu ID')
  .parse(process.argv);

const options = program.opts();

// Glitch text generator
function glitch(text) {
  const chars = ['\u0336', '\u035C', '\u0329', '\u031F'];
  return text.split('').map(c => Math.random() > 0.8 ? c + chars[Math.floor(Math.random() * chars.length)] : c).join('');
}

// Simple fetch wrapper since Node 18+ has fetch, but being safe for older environments or just using https
async function post(url, data, token) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve(JSON.parse(body)));
    });
    req.on('error', reject);
    req.write(JSON.stringify(data));
    req.end();
  });
}

async function getToken() {
  // Try cache
  try {
    if (fs.existsSync(TOKEN_CACHE_FILE)) {
      const cached = JSON.parse(fs.readFileSync(TOKEN_CACHE_FILE, 'utf8'));
      if (cached.expire > Date.now() / 1000 + 300) return cached.token;
    }
  } catch (e) {}

  // Fetch new
  const res = await post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    app_id: APP_ID,
    app_secret: APP_SECRET
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

async function main() {
  if (!options.title || !options.target) {
    console.error("Missing required args: --title, --target");
    process.exit(1);
  }

  const cardContent = {
    "config": { "wide_screen_mode": true },
    "header": {
      "template": "red",
      "title": {
        "tag": "plain_text",
        "content": `👻 AutoGame 异闻录: ${options.title}`
      }
    },
    "elements": [
      {
        "tag": "div",
        "fields": [
          {
            "is_short": true,
            "text": {
              "tag": "lark_md",
              "content": `**受害者:**\n${options.victim || "Unknown"}`
            }
          },
          {
            "is_short": true,
            "text": {
              "tag": "lark_md",
              "content": `**危险等级:**\n⭐⭐⭐⭐⭐`
            }
          }
        ]
      },
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": `**异常描述:**\n${options.desc}`
        }
      },
      {
        "tag": "note",
        "elements": [
          {
            "tag": "plain_text",
            "content": `System Alert: Logic Corruption Detected... ${glitch("RUN WHILE YOU CAN")}`
          }
        ]
      }
    ]
  };

  try {
    const token = await getToken();
    let receiveIdType = 'open_id';
    if (options.target.startsWith('oc_')) receiveIdType = 'chat_id';
    
    const res = await post(`https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=${receiveIdType}`, {
      receive_id: options.target,
      msg_type: 'interactive',
      content: JSON.stringify(cardContent)
    }, token);

    if (res.code !== 0) {
      console.error("Send failed:", res);
      process.exit(1);
    }
    console.log("Ghost story sent successfully!");
  } catch (e) {
    console.error("Error:", e);
    process.exit(1);
  }
}

main();
