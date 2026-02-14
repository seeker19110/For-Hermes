const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE_ROOT = path.resolve(__dirname, '../../');
const LOGS_DIR = path.join(WORKSPACE_ROOT, 'logs');
const MEMORY_LOGS_DIR = path.join(WORKSPACE_ROOT, 'memory/logs');
const TROUBLESHOOTING_FILE = path.join(WORKSPACE_ROOT, 'TROUBLESHOOTING.md');
const CARD_TOOL = path.join(WORKSPACE_ROOT, 'skills/feishu-card/send.js');

function normalizeError(err) {
    if (!err || typeof err !== 'string') return '';
    // Remove timestamps (ISO 8601)
    let norm = err.replace(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z/g, '');
    // Remove typical log prefixes
    norm = norm.replace(/^.*\[ERROR\]\s*/, '').replace(/^.*Exception:\s*/, '');
    // Remove file paths
    norm = norm.replace(/(\/[\w\-\.]+)+/g, '<path>');
    // Remove PIDs and numbers
    norm = norm.replace(/PID=\d+/g, '').replace(/\b\d+\b/g, 'N');
    // Remove variable segments (hashes)
    norm = norm.replace(/[a-f0-9]{8,}/g, '<hash>');
    return norm.trim().substring(0, 80); // First 80 chars as signature
}

function getExistingSignatures() {
    if (!fs.existsSync(TROUBLESHOOTING_FILE)) return new Set();
    const content = fs.readFileSync(TROUBLESHOOTING_FILE, 'utf8');
    const signatures = new Set();
    
    // Extract code blocks
    const codeBlockRegex = /```[\s\S]*?```/g;
    let match;
    while ((match = codeBlockRegex.exec(content)) !== null) {
        signatures.add(normalizeError(match[0]));
    }
    
    // Extract "Symptom: ..." lines
    const symptomRegex = /\*\*Symptom:\*\*\s*`?([^`\n]+)`?/g;
    while ((match = symptomRegex.exec(content)) !== null) {
        signatures.add(normalizeError(match[1]));
    }
    
    return signatures;
}

function scanLogs() {
    const errors = [];
    const seen = new Set();

    // Helper to add unique errors
    const addError = (source, text) => {
        const sig = normalizeError(text);
        if (!sig || sig.length < 10) return;
        // Filter out known noise
        if (sig.includes('user_missing') || sig.includes('memory_missing') || sig.includes('command exited with code 1')) return;
        
        if (!seen.has(sig)) {
            seen.add(sig);
            errors.push({ source, text, sig });
        }
    };
    
    // 1. Scan wrapper_lifecycle.log (last 200 lines)
    const wrapperLog = path.join(LOGS_DIR, 'wrapper_lifecycle.log');
    if (fs.existsSync(wrapperLog)) {
        try {
            const content = fs.readFileSync(wrapperLog, 'utf8');
            const lines = content.split('\n').slice(-200);
            lines.forEach(line => {
                if (line.includes('ERROR') || line.includes('Exception') || line.includes('Failed')) {
                    addError('wrapper_lifecycle.log', line.trim());
                }
            });
        } catch (e) { console.error('Error reading wrapper log:', e.message); }
    }
    
    // 2. Scan today's memory log
    const today = new Date().toISOString().split('T')[0];
    const dailyLog = path.join(MEMORY_LOGS_DIR, `${today}.md`);
    if (fs.existsSync(dailyLog)) {
        try {
            const content = fs.readFileSync(dailyLog, 'utf8');
            const lines = content.split('\n');
            lines.forEach(line => {
                // Markdown log format usually has headers or bullet points
                if (line.includes('[ERROR]') || line.includes('Error:') || line.includes('Exception:')) {
                    addError(`memory/logs/${today}.md`, line.trim());
                }
            });
        } catch (e) { console.error('Error reading daily log:', e.message); }
    }
    
    return errors;
}

async function main() {
    console.log('[Auto-Troubleshooter] Scanning for new errors...');
    
    const knownSignatures = getExistingSignatures();
    const foundErrors = scanLogs();
    const newIssues = [];

    for (const err of foundErrors) {
        if (!knownSignatures.has(err.sig)) {
            newIssues.push(err);
        }
    }

    if (newIssues.length === 0) {
        console.log('[Auto-Troubleshooter] No new undocumented issues found.');
        return;
    }

    console.log(`[Auto-Troubleshooter] Found ${newIssues.length} new issues.`);

    // Append to TROUBLESHOOTING.md
    let appendContent = '';
    const dateStr = new Date().toISOString().split('T')[0];
    
    // Determine next number
    let nextNum = 1;
    if (fs.existsSync(TROUBLESHOOTING_FILE)) {
        const content = fs.readFileSync(TROUBLESHOOTING_FILE, 'utf8');
        const matches = content.match(/## (\d+)\./g);
        if (matches) {
            const nums = matches.map(m => parseInt(m.match(/\d+/)[0], 10));
            nextNum = Math.max(...nums) + 1;
        }
    }

    const reportLines = [];

    for (const issue of newIssues) {
        const title = `${nextNum}. Auto-Detected Issue (${dateStr})`;
        appendContent += `\n## ${title}\n` +
            `**Symptom:** \`${issue.text}\`\n` +
            `**Source:** ${issue.source}\n` +
            `**Context:** Detected by Auto-Troubleshooter.\n` +
            `**Status:** [ ] Identified (${dateStr})\n` +
            `**Proposed Fix:** (Pending investigation)\n` +
            `---\n`;
        
        reportLines.push(`${nextNum}. ${issue.text.substring(0, 60)}...`);
        nextNum++;
    }

    fs.appendFileSync(TROUBLESHOOTING_FILE, appendContent);
    console.log(`[Auto-Troubleshooter] Appended ${newIssues.length} entries to TROUBLESHOOTING.md`);

    // Notify
    if (fs.existsSync(CARD_TOOL)) {
        const target = process.env.LOG_TARGET || 'ou_cdc63fe05e88c580aedead04d851fc04'; // Default to master
        const cardTitle = "🔍 Auto-Troubleshooter Alert";
        const cardBody = `**Found ${newIssues.length} new undocumented errors:**\n\n` +
            reportLines.join('\n') + 
            `\n\n[View TROUBLESHOOTING.md](https://github.com/openclaw/openclaw/blob/main/TROUBLESHOOTING.md)`; // adjust URL if needed
        
        try {
            // Write temp file for content
            const tmpFile = path.join('/tmp', `trouble_${Date.now()}.txt`);
            fs.writeFileSync(tmpFile, cardBody);
            
            console.log(`[Auto-Troubleshooter] Sending notification to ${target}...`);
            execSync(`node "${CARD_TOOL}" --target "${target}" --title "${cardTitle}" --content-file "${tmpFile}"`, { stdio: 'inherit' });
            
            fs.unlinkSync(tmpFile);
        } catch (e) {
            console.error('[Auto-Troubleshooter] Notification failed:', e.message);
        }
    } else {
        console.warn('[Auto-Troubleshooter] feishu-card tool not found, skipping notification.');
    }
}

main();
