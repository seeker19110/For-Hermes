const https = require('https');
const crypto = require('crypto');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { program } = require('commander');

// --- Configuration ---
require('dotenv').config();
const SECRET_ID = process.env.VITE_VOD_SECRET_ID;
const SECRET_KEY = process.env.VITE_VOD_SECRET_KEY;
const SUB_APP_ID = parseInt(process.env.VITE_VOD_SUB_APP_ID || '1500044236', 10);
const HOST = 'vod.ap-guangzhou.tencentcloudapi.com';
const REGION = 'ap-guangzhou';

// --- Validation Models ---
const VALID_MODELS = {
    'Hailuo': ['02', '2.3', '2.3-fast'],
    'Kling': ['1.6', '2.0', '2.1', '2.5', 'o1', '2.6'],
    'Vidu': ['q2', 'q2-turbo', 'q2-pro'],
    'Jimeng': ['3.0pro'],
    'Seedance': ['1.0-pro', '1.0-lite-i2v', '1.0-pro-fast', '1.5-pro', '2.0'],
    'GV': ['3.1', '3.1-fast'],
    'OS': ['2.0']
};

if (!SECRET_ID || !SECRET_KEY) {
    console.error("Error: Missing VITE_VOD_SECRET_ID or VITE_VOD_SECRET_KEY");

    process.exit(1);
}

// --- CLI Definitions ---
program
    .argument('<prompt>', 'Text prompt for video generation')
    .option('--model <name>', 'Model name (Kling, Hailuo, Vidu, etc.)', 'Kling')
    .option('--content <prompt>', 'Content (alias for argument <prompt>)')
    .option('--model-version <version>', 'Model version (e.g. 2.1, 2.5)', '2.5')
    .option('--image <url>', 'Reference image URL for I2V')
    .option('--last-frame <url>', 'Last frame image URL (Kling 2.1, Vidu, GV)')
    .option('--resolution <res>', 'Resolution (720P, 1080P, 2K, 4K)', '1080P')
    .option('--ratio <ratio>', 'Aspect Ratio (16:9, 9:16, 1:1)', '16:9')
    .option('--enhance', 'Enable prompt enhancement', false)
    .option('--chat-id <id>', 'Feishu chat ID for progress cards')
    .parse(process.argv);

const options = program.opts();
const promptArg = program.args[0] || options.content;

// --- Validation Check (Early Exit) ---
if (VALID_MODELS[options.model] && !VALID_MODELS[options.model].includes(options.modelVersion)) {
    const valid = VALID_MODELS[options.model].join(', ');
    const errorMsg = `Error: ModelVersion ${options.modelVersion} is invalid for ModelName ${options.model}\nValid versions: ${valid}`;
    console.error(errorMsg);
    
    if (options.chatId) {
        const cardScript = path.resolve(__dirname, '../feishu-card/send.js');
        const tempDir = path.resolve(__dirname, '../../temp');
        if (!fs.existsSync(tempDir)) try { fs.mkdirSync(tempDir, { recursive: true }); } catch (e) {}
        const tempFile = path.resolve(tempDir, `vod_err_${Date.now()}.md`);
        fs.writeFileSync(tempFile, `**Error**: ${errorMsg}`);
        exec(`node "${cardScript}" --target "${options.chatId}" --text-file "${tempFile}" --title "🎬 视频生成无效参数"`);
    }
    // Give exec a moment to spawn
    setTimeout(() => process.exit(1), 500);
}

// --- TC3 Signature ---
function sign(key, msg) {
    return crypto.createHmac('sha256', key).update(msg, 'utf8').digest();
}

function getSignature(payload, timestamp, date) {
    const httpRequestMethod = "POST";
    const canonicalUri = "/";
    const canonicalQueryString = "";
    const canonicalHeaders = "content-type:application/json\nhost:" + HOST + "\n";
    const signedHeaders = "content-type;host";
    const hashedRequestPayload = crypto.createHash('sha256').update(payload).digest('hex');
    const canonicalRequest = httpRequestMethod + "\n" +
        canonicalUri + "\n" +
        canonicalQueryString + "\n" +
        canonicalHeaders + "\n" +
        signedHeaders + "\n" +
        hashedRequestPayload;

    const algorithm = "TC3-HMAC-SHA256";
    const credentialScope = date + "/" + "vod" + "/" + "tc3_request";
    const hashedCanonicalRequest = crypto.createHash('sha256').update(canonicalRequest).digest('hex');
    const stringToSign = algorithm + "\n" +
        timestamp + "\n" +
        credentialScope + "\n" +
        hashedCanonicalRequest;

    const secretDate = sign("TC3" + SECRET_KEY, date);
    const secretService = sign(secretDate, "vod");
    const secretSigning = sign(secretService, "tc3_request");
    const signature = crypto.createHmac('sha256', secretSigning).update(stringToSign).digest('hex');

    return {
        authorization: algorithm + " " +
            "Credential=" + SECRET_ID + "/" + credentialScope + ", " +
            "SignedHeaders=" + signedHeaders + ", " +
            "Signature=" + signature,
        timestamp: timestamp
    };
}

// --- API Request ---
function request(action, params) {
    return new Promise((resolve, reject) => {
        const payload = JSON.stringify(params);
        const timestamp = Math.floor(Date.now() / 1000);
        const date = new Date(timestamp * 1000).toISOString().slice(0, 10);

        const sig = getSignature(payload, timestamp, date);

        const reqOpts = {
            hostname: HOST,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Host': HOST,
                'X-TC-Action': action,
                'X-TC-Version': '2018-07-17',
                'X-TC-Timestamp': sig.timestamp,
                'X-TC-Region': REGION,
                'Authorization': sig.authorization
            }
        };

        const req = https.request(reqOpts, (res) => {
            let data = '';
            res.on('data', c => data += c);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (json.Response && json.Response.Error) {
                        // Normalize API errors
                        const err = new Error(json.Response.Error.Message);
                        err.code = json.Response.Error.Code;
                        reject(err);
                    } else {
                        resolve(json.Response);
                    }
                } catch (e) {
                    reject(new Error(`Invalid JSON response: ${data.substring(0, 100)}...`));
                }
            });
        });
        req.on('error', reject);
        req.write(payload);
        req.end();
    });
}

// --- Feishu Helper ---
function sendCard(title, content, type = 'info') {
    if (!options.chatId) return;
    const cardScript = path.resolve(__dirname, '../feishu-card/send.js');
    
    // Harden: Ensure temp directory exists
    const tempDir = path.resolve(__dirname, '../../temp');
    if (!fs.existsSync(tempDir)) {
        try {
            fs.mkdirSync(tempDir, { recursive: true });
        } catch (e) {
            console.error(`[Card] Failed to create temp dir: ${e.message}`);
            return;
        }
    }

    const tempFile = path.resolve(tempDir, `vod_card_${Date.now()}.md`);
    
    // Simple markdown body
    fs.writeFileSync(tempFile, content);
    
    // Using exec to fire-and-forget (mostly)
    exec(`node "${cardScript}" --target "${options.chatId}" --text-file "${tempFile}" --title "${title}"`, (error) => {
        if (error) console.error(`[Card] Failed to send: ${error.message}`);
        try { fs.unlinkSync(tempFile); } catch(e) {}
    });
}

// --- Main Logic ---
async function main() {
    console.log(`[VideoGen] Starting task for model: ${options.model} ${options.modelVersion}`);
    
    sendCard("🎬 视频生成任务已提交", 
        `**Prompt**: ${promptArg}\n` +
        `**Model**: ${options.model} ${options.modelVersion}\n` + 
        `**Ref Image**: ${options.image ? 'Yes' : 'No'}\n` +
        `**Status**: 🚀 Initializing...`
    );

    try {
        // 1. Build Parameters
        const createParams = {
            SubAppId: SUB_APP_ID,
            ModelName: options.model,
            ModelVersion: options.modelVersion,
            Prompt: promptArg,
            EnhancePrompt: options.enhance ? "Enabled" : "Disabled",
            OutputConfig: {
                StorageMode: "Temporary", // Or Permanent if bucket configured
                Resolution: options.resolution,
                AspectRatio: options.ratio
            }
        };

        // Add Image Reference (I2V)
        if (options.image) {
            createParams.FileInfos = [{ Type: "Url", Url: options.image }];
        }

        // Add Last Frame
        if (options.lastFrame) {
            createParams.LastFrameUrl = options.lastFrame;
        }

        // Kling Special Scene Type
        if (options.model === 'Kling' && options.image) {
            // Check if we want motion_control? Defaulting not to unless specific arg added later.
            // createParams.SceneType = "motion_control"; 
        }

        console.log("[VideoGen] Create Params:", JSON.stringify(createParams, null, 2));

        // 2. Create Task
        const createRes = await request('CreateAigcVideoTask', createParams);
        const taskId = createRes.TaskId;
        console.log(`[VideoGen] Task Created. ID: ${taskId}`);

        sendCard("🎬 视频生成进行中", `**Task ID**: ${taskId}\n**Status**: ⏳ Generating (This may take 3-10 minutes)...`);

        // 3. Poll Loop
        let attempts = 0;
        const POLL_INTERVAL = 5000; // 5s
        const MAX_ATTEMPTS = 240;   // 20 minutes max

        while (attempts < MAX_ATTEMPTS) {
            await new Promise(r => setTimeout(r, POLL_INTERVAL));
            
            const pollRes = await request('DescribeTaskDetail', { 
                SubAppId: SUB_APP_ID, 
                TaskId: taskId 
            });
            
            const task = pollRes.AigcVideoTask;
            if (!task) continue;

            const status = task.Status;
            const progress = task.Progress || 0;

            if (status === 'FINISH') {
                if (task.ErrCode && task.ErrCode !== 0) {
                    throw new Error(`Task Finished with Error ${task.ErrCodeExt}: ${task.Message}`);
                }

                // Success!
                const file = task.Output?.FileInfos?.[0];
                if (file) {
                    const videoUrl = file.FileUrl;
                    const coverUrl = file.MetaData?.CoverUrl || 'N/A';
                    const duration = file.MetaData?.Duration || 0;

                    console.log(`[VideoGen] SUCCESS!`);
                    console.log(`MEDIA_URL:${videoUrl}`);
                    console.log(`COVER_URL:${coverUrl}`);
                    
                    sendCard("🎬 视频生成成功", 
                        `**Status**: ✅ Completed\n` +
                        `**Duration**: ${duration}s\n` +
                        `**Video**: [点击下载/播放](${videoUrl})\n` +
                        `**Cover**: [Cover Image](${coverUrl})`
                    );
                    return;
                } else {
                    throw new Error("Task finished but no output file found.");
                }
            } else if (status === 'FAIL') {
                throw new Error(`Task Failed: ${task.Message} (${task.ErrCodeExt})`);
            }

            // Log progress occasionally
            if (attempts % 6 === 0) { // Every ~30s
                console.log(`[VideoGen] Status: ${status} (${progress}%)`);
            }
            
            attempts++;
        }

        throw new Error("Polling timed out after 20 minutes.");

    } catch (err) {
        console.error(`[VideoGen] Error: ${err.message}`);
        sendCard("🎬 视频生成失败", `**Error**: ${err.message}\n**Code**: ${err.code || 'Unknown'}`);
        process.exit(1);
    }
}

main();
