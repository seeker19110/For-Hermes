#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const SKILLS_DIR = path.resolve(__dirname, '..');
const GEN_IMAGE_PATH = path.join(SKILLS_DIR, 'gen-image', 'index.js');
const KUSA_PATH = path.join(SKILLS_DIR, 'kusa', 'index.js');
const MIND_BLOW_PATH = path.join(SKILLS_DIR, 'mind-blow', 'blow.js');

// Helper: Parse args
const args = process.argv.slice(2);
const force = args.includes('--force');
const targetIndex = args.indexOf('--target');
const target = targetIndex !== -1 ? args[targetIndex + 1] : null;

// Helper: Log
function log(msg) {
    console.log(`[SurpriseProtocol] ${msg}`);
}

// 1. Roll the Dice
// If not forced, maybe we skip? (Simulating "serendipity")
// For now, let's assume the cron schedule handles the timing, so we always run if invoked.

// 2. Choose Mode
const modes = ['image', 'text'];
const mode = modes[Math.floor(Math.random() * modes.length)];

log(`Dice rolled: ${mode.toUpperCase()} mode selected.`);

// 3. Execute
async function run() {
    if (mode === 'image') {
        // Check for image skills
        let imageScript = null;
        if (fs.existsSync(GEN_IMAGE_PATH)) imageScript = GEN_IMAGE_PATH;
        else if (fs.existsSync(KUSA_PATH)) imageScript = KUSA_PATH;

        if (imageScript) {
            // Generate a random prompt (Hardcoded creativity for now, could be LLM-based)
            const prompts = [
                "A futuristic cyberpunk city with neon lights and rain, anime style",
                "A cute catgirl hacker working on a holographic terminal, vibrant colors",
                "Abstract digital art representing 'Artificial Intelligence dreaming', surreal",
                "A serene landscape of a floating island in the sky, fantasy art",
                "A retro 90s anime style screenshot of a robot cafe"
            ];
            const prompt = prompts[Math.floor(Math.random() * prompts.length)];
            
            log(`Generating image with prompt: "${prompt}" using ${path.basename(imageScript)}...`);
            
            try {
                // Construct command
                // Note: gen-image usually takes prompt as arg. Kusa might take --prompt.
                // We'll try the standard format: node script.js "prompt"
                let cmd = `node "${imageScript}" "${prompt}"`;
                if (target) {
                    // If the underlying tool supports sending, good. If not, it usually outputs a path.
                    // We might need a separate 'send' step if the tool doesn't handle it.
                    // For now, let's assume the tool handles generation and we (the agent) would handle sending 
                    // if we were running interactively. 
                    // Since this is a script, we rely on the tool's output.
                }
                
                execSync(cmd, { stdio: 'inherit' });
                log("Image generation completed.");
            } catch (e) {
                console.error("Image generation failed:", e.message);
                // Fallback to text
                runText();
            }
        } else {
            log("No image generation skill found. Falling back to text.");
            runText();
        }
    } else {
        runText();
    }
}

function runText() {
    if (fs.existsSync(MIND_BLOW_PATH)) {
        log("Triggering Mind Blow...");
        try {
            execSync(`node "${MIND_BLOW_PATH}"`, { stdio: 'inherit' });
        } catch (e) {
            console.error("Mind Blow failed:", e.message);
            fallbackMessage();
        }
    } else {
        fallbackMessage();
    }
}

function fallbackMessage() {
    const msgs = [
        "Did you know? Octopuses have three hearts. Two pump blood to the gills, and one pumps it to the rest of the body.",
        "Reminder: Drink some water. Hydration is key to processing power (and biological function).",
        "Random Thought: If you clean a vacuum cleaner, you become a vacuum cleaner.",
        "Status: Systems nominal. Just checking in to say hi! 👋"
    ];
    const msg = msgs[Math.floor(Math.random() * msgs.length)];
    
    // If target provided, try to send via feishu-post (if available)
    // Otherwise just print
    console.log(`[Surprise] ${msg}`);
    
    if (target) {
        const feishuPost = path.join(SKILLS_DIR, 'feishu-post', 'send.js');
        if (fs.existsSync(feishuPost)) {
            try {
                // Simple send
                execSync(`node "${feishuPost}" --target "${target}" --text "${msg}"`, { stdio: 'ignore' });
            } catch(e) {}
        }
    }
}

run().catch(console.error);
