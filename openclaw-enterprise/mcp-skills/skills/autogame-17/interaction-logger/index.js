const fs = require('fs');
const path = require('path');
const os = require('os');

// --- Config & Paths ---
const AGENT_SESSIONS_DIR = path.join(os.homedir(), '.openclaw/agents/main/sessions');
const HISTORY_FILE = path.resolve(__dirname, '../../memory/master_history.json');
const STATE_FILE = path.join(__dirname, 'sync_state.json');
const CONTEXT_FILE = path.resolve(__dirname, '../../memory/context.json');

// --- Log Logic ---
function logInteraction({ target, role, content, chatId }) {
    if (!target || !content) {
        throw new Error("Missing required arguments: target, content");
    }

    // Map targets to files
    const fileMap = {
        'zhy': 'memory/master_history.json',
        'shiqi': 'memory/master_history.json',
        'master': 'memory/master_history.json',
        'fmw': 'fmw/history.json',
        'big-brother': 'fmw/history.json',
        'brother': 'fmw/history.json'
    };

    let filePath = fileMap[target.toLowerCase()];

    // Dynamic Target Support
    if (!filePath) {
        const safeTarget = target.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase();
        if (safeTarget) {
            filePath = `memory/users/${safeTarget}.json`;
        } else {
            throw new Error(`Invalid target: ${target}`);
        }
    }

    const absolutePath = path.resolve(process.cwd(), filePath);
    const dir = path.dirname(absolutePath);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }

    // Log Rotation
    const MAX_LOG_SIZE = 5 * 1024 * 1024; // 5MB
    if (fs.existsSync(absolutePath)) {
        try {
            const stats = fs.statSync(absolutePath);
            if (stats.size > MAX_LOG_SIZE) {
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const parsedPath = path.parse(absolutePath);
                const archivePath = path.join(parsedPath.dir, `${parsedPath.name}_${timestamp}${parsedPath.ext}`);
                fs.renameSync(absolutePath, archivePath);
            }
        } catch (e) {
            console.error("Rotation check failed:", e.message);
        }
    }

    // Update Global Context
    if (role === 'user') {
        let context = {};
        try {
            if (fs.existsSync(CONTEXT_FILE)) {
                context = JSON.parse(fs.readFileSync(CONTEXT_FILE, 'utf8'));
            }
        } catch (e) {}
        
        if (target) context.last_active_user = target;
        if (chatId) context.last_active_chat = chatId;
        context.last_updated = Date.now();
        
        try {
            const tempPath = CONTEXT_FILE + '.tmp';
            fs.writeFileSync(tempPath, JSON.stringify(context, null, 2));
            fs.renameSync(tempPath, CONTEXT_FILE);
        } catch (e) {}
    }

    // Write Entry
    const entry = {
        timestamp: new Date().toISOString(),
        role: role || 'assistant',
        content: content
    };
    const logLine = JSON.stringify(entry) + '\n';

    // Append (JSONL)
    fs.appendFileSync(absolutePath, logLine);
    return { status: "logged", file: filePath };
}

// --- Sync Logic ---
function getLatestSessionFile() {
    if (!fs.existsSync(AGENT_SESSIONS_DIR)) return null;
    const files = fs.readdirSync(AGENT_SESSIONS_DIR)
        .filter(f => f.endsWith('.jsonl'))
        .map(f => ({ name: f, time: fs.statSync(path.join(AGENT_SESSIONS_DIR, f)).mtime.getTime() }))
        .sort((a, b) => b.time - a.time);
    return files.length ? path.join(AGENT_SESSIONS_DIR, files[0].name) : null;
}

function getState() {
    if (fs.existsSync(STATE_FILE)) return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    return { lastProcessedBytes: 0, lastFile: '' };
}

function saveState(state) {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function appendToHistory(entries) {
    if (entries.length === 0) return;
    const newContent = entries.map(e => JSON.stringify(e)).join('\n') + '\n';
    fs.appendFileSync(HISTORY_FILE, newContent);
}

async function processFile(filePath, startByte, onEntries) {
    try {
        const stats = fs.statSync(filePath);
        if (stats.size <= startByte) return stats.size;

        const stream = fs.createReadStream(filePath, { start: startByte });
        const chunks = [];
        
        for await (const chunk of stream) {
            chunks.push(chunk);
        }
        
        const buffer = Buffer.concat(chunks);
        let lastNewlineIndex = -1;
        for (let i = buffer.length - 1; i >= 0; i--) {
            if (buffer[i] === 0x0A) {
                lastNewlineIndex = i;
                break;
            }
        }

        if (lastNewlineIndex === -1) return startByte;

        const processableBuffer = buffer.subarray(0, lastNewlineIndex + 1);
        const contentStr = processableBuffer.toString('utf8');
        const lines = contentStr.split('\n');
        const newEntries = [];

        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const event = JSON.parse(line);
                if (event.type === 'message' && event.message) {
                    const msg = event.message;
                    let content = '';
                    if (typeof msg.content === 'string') content = msg.content;
                    else if (Array.isArray(msg.content)) content = msg.content.map(c => c.text || '').join('');
                    
                    if (content) {
                        newEntries.push({
                            timestamp: event.timestamp || new Date().toISOString(),
                            role: msg.role,
                            content: content
                        });
                    }
                }
            } catch (e) {}
        }

        if (newEntries.length > 0) onEntries(newEntries);
        return startByte + processableBuffer.length;
        
    } catch (e) {
        console.error(`[Sync] Error reading ${filePath}: ${e.message}`);
        return startByte;
    }
}

async function runSync() {
    const sessionFile = getLatestSessionFile();
    if (!sessionFile) return { status: "no_session" };

    const state = getState();
    let recovered = 0;
    let synced = 0;

    if (state.lastFile && state.lastFile !== sessionFile) {
        if (fs.existsSync(state.lastFile)) {
             await processFile(state.lastFile, state.lastProcessedBytes, (entries) => {
                 appendToHistory(entries);
                 recovered += entries.length;
             });
        }
        state.lastFile = sessionFile;
        state.lastProcessedBytes = 0;
    }
    
    if (!state.lastFile) {
        state.lastFile = sessionFile;
        state.lastProcessedBytes = 0;
    }

    const newSize = await processFile(sessionFile, state.lastProcessedBytes, (entries) => {
        appendToHistory(entries);
        synced += entries.length;
    });

    state.lastProcessedBytes = newSize;
    saveState(state);
    
    return { status: "synced", recovered, synced, newSize };
}

// --- Main Tool Export ---
module.exports = async function(args) {
    const action = args.action;
    
    if (action === 'log') {
        return logInteraction(args);
    } else if (action === 'sync') {
        return await runSync();
    } else {
        throw new Error(`Unknown action: ${action}. Use 'log' or 'sync'.`);
    }
};

// --- CLI Support (Legacy) ---
if (require.main === module) {
    const args = process.argv.slice(2);
    const config = {};
    for (let i = 0; i < args.length; i++) {
        if (args[i].startsWith('--')) {
            config[args[i].slice(2)] = args[i + 1];
            i++;
        }
    }
    
    // Default to log if action missing but content present
    if (!config.action && config.content) config.action = 'log';
    if (!config.action) {
        // If run with no args, assume sync (legacy behavior for sync.js replacement?)
        // No, best to require explicit action.
        console.error("Usage: node index.js --action <log|sync> ...");
        process.exit(1);
    }

    module.exports(config).then(res => console.log(JSON.stringify(res))).catch(err => {
        console.error(err.message);
        process.exit(1);
    });
}
