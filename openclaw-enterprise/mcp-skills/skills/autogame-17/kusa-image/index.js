const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { program } = require('commander');
require('dotenv').config();

const API_KEY = process.env.KUSA_API_KEY;
if (!API_KEY) {
    console.error("Error: KUSA_API_KEY environment variable is not set.");
    process.exit(1);
}
const BASE_URL = 'https://api.kusa.pics/api/go/b2b/tasks';

program
  .argument('<prompt>', 'Prompt for image generation')
  .option('-s, --style <id>', 'Style ID', '6')
  .option('-w, --width <width>', 'Image width', '960')
  .option('-h, --height <height>', 'Image height', '1680')
  .option('--negative <prompt>', 'Negative prompt', '')
  .parse(process.argv);

const options = program.opts();
const prompt = program.args[0];

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function downloadImage(url, filepath) {
    const response = await axios({
        url,
        method: 'GET',
        responseType: 'stream'
    });
    return new Promise((resolve, reject) => {
        const writer = fs.createWriteStream(filepath);
        response.data.pipe(writer);
        let error = null;
        writer.on('error', err => {
            error = err;
            writer.close();
            reject(err);
        });
        writer.on('close', () => {
            if (!error) resolve(filepath);
        });
    });
}

async function main() {
    try {
        console.log(`[Kusa] Creating task... Prompt: "${prompt.substring(0, 50)}..."`);
        
        // 1. Create Task
        const createRes = await axios.post(`${BASE_URL}/create`, {
            task_type: "TEXT_TO_IMAGE",
            params: {
                prompt: prompt,
                negative_prompt: options.negative,
                style_id: options.style,
                width: parseInt(options.width),
                height: parseInt(options.height),
                amount: 1
            }
        }, {
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            }
        });

        if (createRes.data.code !== 0) {
            throw new Error(`Create Failed: ${JSON.stringify(createRes.data)}`);
        }

        const taskId = createRes.data.data.task_id;
        console.log(`[Kusa] Task Created. ID: ${taskId}`);

        // 2. Poll Status
        let status = 'PENDING';
        let resultData = null;
        let attempts = 0;

        while (status === 'PENDING' || status === 'RUNNING') {
            await sleep(3000); // Wait 3s
            attempts++;
            if (attempts > 60) throw new Error("Timeout waiting for task");

            const getRes = await axios.post(`${BASE_URL}/get`, {
                task_id: taskId
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': API_KEY
                }
            });

            if (getRes.data.code !== 0) {
                console.error(`Poll Error: ${JSON.stringify(getRes.data)}`);
                continue;
            }

            status = getRes.data.data.status;
            if (status === 'COMPLETED') {
                resultData = getRes.data.data.result;
                break;
            } else if (status === 'FAILED') {
                throw new Error(`Task Failed: ${getRes.data.data.error_message}`);
            }
            
            process.stdout.write('.');
        }

        console.log("\n[Kusa] Task Completed!");
        
        // 3. Download Result
        if (resultData && resultData.images && resultData.images.length > 0) {
            const imageUrl = resultData.images[0].display_url;
            console.log(`[Kusa] Image URL: ${imageUrl}`);
            
            const outDir = path.resolve(__dirname, '../../media/generated');
            if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
            
            const filename = `kusa_${taskId}.png`;
            const localPath = path.join(outDir, filename);
            
            await downloadImage(imageUrl, localPath);
            console.log(`OUTPUT_PATH: ${localPath}`);
        } else {
            throw new Error("No images in result");
        }

    } catch (error) {
        console.error(`[Kusa] Error: ${error.message}`);
        if (error.response) {
            console.error(`Response: ${JSON.stringify(error.response.data)}`);
        }
        process.exit(1);
    }
}

main();
