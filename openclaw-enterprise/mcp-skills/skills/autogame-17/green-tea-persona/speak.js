#!/usr/bin/env node
const { program } = require('commander');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const MIN_DELAY_MS = 2000;
const MAX_DELAY_MS = 5000;
const IMAGE_CHANCE = 0.05; // 5% chance

program
  .requiredOption('-t, --target <id>', 'Target Feishu ID')
  .requiredOption('-x, --text <text>', 'Text to speak')
  .option('--image', 'Force send an image')
  .parse(process.argv);

const options = program.opts();

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getRandomDelay() {
    return Math.floor(Math.random() * (MAX_DELAY_MS - MIN_DELAY_MS + 1) + MIN_DELAY_MS);
}

function formatText(text) {
    let processed = text.replace(/\\n/g, '\n');
    let clean = processed.replace(/[，。,.\uff0c\uff08\uff09!?？！、；：""''…—～~·]/g, ' ');
    clean = clean.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FEFF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}]/gu, '');
    clean = clean.replace(/[（(][^）)]*[）)]/g, '').replace(/\*[^*]*\*/g, '');
    clean = clean.replace(/喵~?/g, '').replace(/主人/g, '你');
    
    // Split by newlines first
    let initialSegments = clean.split(/[\n\r]+/);
    let final = [];
    
    for (const seg of initialSegments) {
        const trimmed = seg.trim();
        if (!trimmed) continue;
        
        // Further split by spaces to keep messages short
        const words = trimmed.split(/\s+/);
        let current = '';
        
        for (const w of words) {
            if ((current.length + w.length + 1) > 15) {
                if (current) final.push(current);
                current = w;
            } else {
                current = current ? current + ' ' + w : w;
            }
        }
        if (current) final.push(current);
    }
    
    return final.slice(0, 5);
}

async function speak() {
    const segments = formatText(options.text);
    console.log(`[Green Tea] Sending ${segments.length} segments to ${options.target}...`);
    
    // Create temp directory if not exists
    const tempDir = path.resolve(__dirname, '../../temp');
    if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });

    for (let i = 0; i < segments.length; i++) {
        const segment = segments[i];
        
        // Use 'message' tool via CLI - but need to quote properly
        // Or better, use the direct node script for feishu-post or feishu-message if available.
        // The previous script used feishu-post/send.js --text-file.
        // Let's use simple openclaw message tool for simplicity via CLI? 
        // No, calling openclaw recursively is tricky.
        // Let's use the local `skills/feishu-message/send.js` if it exists, or `skills/feishu-post/send.js`.
        
        // Use `message` tool directly via openclaw CLI?
        // Actually, we are INSIDE a node script. We can just use execSync to call openclaw CLI?
        // Or easier: use the existing feishu skills directly.
        
        // Fallback: use 'openclaw message send' via execSync
        // But wait, the environment variables might not be passed correctly if we spawn?
        // Let's rely on `skills/feishu-post/send.js` as in previous version, assuming it exists.
        
        const tempFile = path.join(tempDir, `greentea_${Date.now()}_${i}.txt`);
        fs.writeFileSync(tempFile, segment);
        
        // Use feishu-post send.js if available
        let cmd = '';
        if (fs.existsSync(path.resolve(__dirname, '../feishu-post/send.js'))) {
             cmd = `node skills/feishu-post/send.js --target "${options.target}" --text-file "${tempFile}"`;
        } else {
             // Fallback to simple echo (dry run) if skill missing
             console.log(`[Mock Send] ${segment}`);
             cmd = `echo "Mock send: ${segment}"`;
        }

        try {
            execSync(cmd, { stdio: 'ignore' }); 
        } catch (e) {
            console.error(`Failed to send segment: ${segment}`);
        } finally {
            if (fs.existsSync(tempFile)) fs.unlinkSync(tempFile);
        }

        if (i < segments.length - 1) {
            const delay = getRandomDelay();
            await sleep(delay);
        }
    }
}

speak();
