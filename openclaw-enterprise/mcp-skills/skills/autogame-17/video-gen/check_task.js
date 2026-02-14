const https = require('https');
const crypto = require('crypto');
require('dotenv').config({ path: require('path').resolve(__dirname, '../../.env') });

const SECRET_ID = process.env.VITE_VOD_SECRET_ID;
const SECRET_KEY = process.env.VITE_VOD_SECRET_KEY;
const SUB_APP_ID = parseInt(process.env.VITE_VOD_SUB_APP_ID || '1330810954', 10);
const HOST = 'vod.ap-guangzhou.tencentcloudapi.com';
const REGION = 'ap-guangzhou';
const TASK_ID = process.argv[2];

if (!TASK_ID) {
    console.error("Usage: node check_task.js <task_id>");
    process.exit(1);
}

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
            res.on('end', () => resolve(JSON.parse(data)));
        });
        req.on('error', reject);
        req.write(payload);
        req.end();
    });
}

// ... (Previous code)
async function check() {
    console.log(`Checking Task: ${TASK_ID}`);
    const res = await request('DescribeTaskDetail', { 
        SubAppId: SUB_APP_ID, 
        TaskId: TASK_ID 
    });
    
    if (res.Response && res.Response.AigcVideoTask) {
        const task = res.Response.AigcVideoTask;
        console.log(`Status: ${task.Status}`);
        
        if (task.Status === 'FINISH') {
            // Check Output structure carefully
            if (task.Output && task.Output.FileInfos && task.Output.FileInfos.length > 0) {
                const file = task.Output.FileInfos[0];
                console.log(`Video URL: ${file.FileUrl}`);
            } else {
                console.log("Task Finished but Output is empty/invalid.");
                console.log(JSON.stringify(task.Output, null, 2));
            }
        } else if (task.Status === 'FAIL') {
             console.log(`Error: ${task.Message} (${task.ErrCodeExt})`);
        }
    } else {
        console.log(JSON.stringify(res, null, 2));
    }
}
check();
