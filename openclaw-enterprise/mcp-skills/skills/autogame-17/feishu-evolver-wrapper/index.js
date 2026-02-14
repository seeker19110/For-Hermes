const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const { sleepSync } = require('./utils/sleep'); // New helper
const { sendReport } = require('./report.js'); // Use optimized internal report function

// [2026-02-03] WRAPPER REFACTOR: PURE PROXY
// This wrapper now correctly delegates to the core 'evolver' plugin.
// Enhanced with Kill Switch, Heartbeat Summary, Artifact Upload, and Thought Injection.

function sleepSeconds(sec) {
    const s = Number(sec);
    if (!Number.isFinite(s) || s <= 0) return;
    
    // Check for wake signal every 2 seconds
    const interval = 2;
    const wakeFile = path.resolve(__dirname, '../../memory/evolver_wake.signal');
    
    const steps = Math.ceil(s / interval);
    for (let i = 0; i < steps; i++) {
        if (fs.existsSync(wakeFile)) {
            console.log('[Wrapper] Wake signal detected! Skipping sleep.');
            try { fs.unlinkSync(wakeFile); } catch (e) {}
            return;
        }
        sleepSync(interval * 1000);
    }
}

function nextCycleTag(cycleFile) {
    // Atomic read-increment-write using tmp+rename to prevent concurrent duplicates
    var cycleId = 1;
    try {
        if (fs.existsSync(cycleFile)) {
            var raw = fs.readFileSync(cycleFile, 'utf8').trim();
            if (raw && !isNaN(raw)) {
                cycleId = parseInt(raw, 10) + 1;
            }
        }
    } catch (e) {
        console.error('Cycle read error:', e.message);
    }

    try {
        var tmpFile = cycleFile + '.tmp.' + process.pid;
        fs.writeFileSync(tmpFile, cycleId.toString());
        fs.renameSync(tmpFile, cycleFile);
    } catch (e) {
        console.error('Cycle write error:', e.message);
        // Fallback: direct write
        try { fs.writeFileSync(cycleFile, cycleId.toString()); } catch (_) {}
    }

    return String(cycleId).padStart(4, '0');
}

function tailText(buf, maxChars) {
    if (!buf) return '';
    const s = Buffer.isBuffer(buf) ? buf.toString('utf8') : String(buf);
    if (s.length <= maxChars) return s;
    return s.slice(-maxChars);
}

// --- FAILURE LEARNING + RETRY POLICY ---
const FAILURE_LESSONS_FILE = path.resolve(__dirname, '../../memory/evolution/failure_lessons.jsonl');
const HAND_MAX_RETRIES_PER_CYCLE = Number.parseInt(process.env.EVOLVE_HAND_MAX_RETRIES || '3', 10);
const HAND_RETRY_BACKOFF_SECONDS = Number.parseInt(process.env.EVOLVE_HAND_RETRY_BACKOFF_SECONDS || '15', 10);

function appendFailureLesson(cycleTag, reason, details) {
    try {
        const dir = path.dirname(FAILURE_LESSONS_FILE);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        const entry = {
            at: new Date().toISOString(),
            cycle: String(cycleTag),
            reason: String(reason || 'unknown'),
            details: String(details || '').slice(0, 1200),
        };
        fs.appendFileSync(FAILURE_LESSONS_FILE, JSON.stringify(entry) + '\n');
    } catch (e) {
        console.warn('[Wrapper] Failed to write failure lesson:', e.message);
    }
}

function readRecentFailureLessons(limit) {
    try {
        if (!fs.existsSync(FAILURE_LESSONS_FILE)) return [];
        const n = Number.isFinite(Number(limit)) ? Number(limit) : 5;
        const lines = fs.readFileSync(FAILURE_LESSONS_FILE, 'utf8').split('\n').filter(Boolean);
        return lines.slice(-n).map((l) => {
            try { return JSON.parse(l); } catch (_) { return null; }
        }).filter(Boolean);
    } catch (_) {
        return [];
    }
}

function cleanStatusText(raw) {
    return String(raw || '').replace(/\r/g, '').trim();
}

function isGenericStatusText(text) {
    const t = cleanStatusText(text).toLowerCase();
    if (!t) return true;
    const genericPatterns = [
        'status: [complete] cycle finished.',
        '状态: [完成] 周期已完成。',
        'status: [complete] cycle finished',
        '状态: [完成] 周期已完成',
        'step complete',
        'completed.',
        'done.',
    ];
    for (const p of genericPatterns) {
        if (t === p || t.includes(p)) return true;
    }
    // Too short + only completion semantics => still considered generic.
    if (t.length < 40 && (t.includes('完成') || t.includes('complete') || t.includes('finished'))) {
        return true;
    }
    return false;
}

function buildFallbackStatus(lang, cycleTag, gitInfo, latestEvent) {
    const evt = latestEvent || readLatestEvolutionEvent();
    const intent = evt && evt.intent ? String(evt.intent) : null;
    const signals = evt && Array.isArray(evt.signals) ? evt.signals.slice(0, 3).map(String) : [];
    const geneId = evt && Array.isArray(evt.genes_used) && evt.genes_used.length ? String(evt.genes_used[0]) : null;
    const mutation = evt && evt.meta && evt.meta.mutation ? evt.meta.mutation : null;
    const expectedEffect = mutation && mutation.expected_effect ? String(mutation.expected_effect) : null;
    const blastFiles = evt && evt.blast_radius ? evt.blast_radius.files : null;
    const blastLines = evt && evt.blast_radius ? evt.blast_radius.lines : null;
    const hasGit = !!(gitInfo && gitInfo.shortHash);

    if (lang === 'zh') {
        const intentLabel = intentLabelByLang(intent, 'zh');
        const parts = [`状态: [${intentLabel}]`];
        if (expectedEffect) {
            parts.push(`目标：${expectedEffect}。`);
        }
        if (signals.length) {
            parts.push(`触发信号：${signals.join(', ')}。`);
        }
        if (geneId) {
            parts.push(`使用基因：${geneId}。`);
        }
        if (blastFiles != null) {
            parts.push(`影响范围：${blastFiles} 个文件 / ${blastLines || 0} 行。`);
        }
        if (hasGit) {
            parts.push(`提交：${gitInfo.fileCount} 个文件，涉及 ${gitInfo.areaStr}。`);
        } else {
            parts.push(`无可提交代码变更。`);
        }
        return parts.join(' ');
    }
    const intentLabel = intentLabelByLang(intent, 'en');
    const parts = [`Status: [${intentLabel}]`];
    if (expectedEffect) {
        parts.push(`Goal: ${expectedEffect}.`);
    }
    if (signals.length) {
        parts.push(`Signals: ${signals.join(', ')}.`);
    }
    if (geneId) {
        parts.push(`Gene: ${geneId}.`);
    }
    if (blastFiles != null) {
        parts.push(`Blast radius: ${blastFiles} files / ${blastLines || 0} lines.`);
    }
    if (hasGit) {
        parts.push(`Committed ${gitInfo.fileCount} files in ${gitInfo.areaStr}.`);
    } else {
        parts.push(`No committable code diff.`);
    }
    return parts.join(' ');
}

function withOutcomeLine(statusText, success, lang) {
    const s = cleanStatusText(statusText);
    const enPrefix = 'Result: ';
    const zhPrefix = '结果: ';
    if (lang === 'zh') {
        if (s.startsWith(zhPrefix)) return s;
        return `${zhPrefix}${success ? '成功' : '失败'}\n${s}`;
    }
    if (s.startsWith(enPrefix)) return s;
    return `${enPrefix}${success ? 'SUCCESS' : 'FAILED'}\n${s}`;
}

function ensureDetailedStatus(rawText, lang, cycleTag, gitInfo, latestEvent) {
    const s = cleanStatusText(rawText);
    if (!s || isGenericStatusText(s)) return buildFallbackStatus(lang, cycleTag, gitInfo, latestEvent);
    return s;
}

function readLatestEvolutionEvent() {
    try {
        const eventsFile = path.resolve(__dirname, '../../assets/gep/events.jsonl');
        if (!fs.existsSync(eventsFile)) return null;
        const lines = fs.readFileSync(eventsFile, 'utf8').split('\n').filter(Boolean);
        for (let i = lines.length - 1; i >= 0; i--) {
            try {
                const obj = JSON.parse(lines[i]);
                if (obj && obj.type === 'EvolutionEvent') return obj;
            } catch (_) {}
        }
        return null;
    } catch (_) {
        return null;
    }
}

function intentLabelByLang(intent, lang) {
    const i = String(intent || '').toLowerCase();
    if (lang === 'zh') {
        if (i === 'innovate') return '创新';
        if (i === 'optimize') return '优化';
        return '修复';
    }
    if (i === 'innovate') return 'INNOVATION';
    if (i === 'optimize') return 'OPTIMIZE';
    return 'REPAIR';
}

function enforceStatusIntent(statusText, intent, lang) {
    const s = cleanStatusText(statusText);
    if (!intent) return s;
    const label = intentLabelByLang(intent, lang);
    if (lang === 'zh') {
        if (/^状态:\s*\[[^\]]+\]/.test(s)) return s.replace(/^状态:\s*\[[^\]]+\]/, `状态: [${label}]`);
        return `状态: [${label}] ${s}`;
    }
    if (/^Status:\s*\[[^\]]+\]/.test(s)) return s.replace(/^Status:\s*\[[^\]]+\]/, `Status: [${label}]`);
    return `Status: [${label}] ${s}`;
}

// --- FEATURE 2: HEARTBEAT SUMMARY (Option 2: Real-time Error, Summary Info) ---
let sessionLogs = { infoCount: 0, errorCount: 0, startTime: 0, errors: [] };
const LOG_DEDUP_FILE = path.resolve(__dirname, '../../memory/evolution/log_dedup.json');
const LOG_DEDUP_WINDOW_MS = Number.parseInt(process.env.EVOLVE_LOG_DEDUP_WINDOW_MS || '600000', 10); // 10 minutes
const LOG_DEDUP_MAX_KEYS = Number.parseInt(process.env.EVOLVE_LOG_DEDUP_MAX_KEYS || '800', 10);

// Lifecycle log target group (set via env or hardcode for reliability)
const FEISHU_LOG_GROUP = process.env.LOG_TARGET || 'oc_ab79ebbe224701d0288891d6f8ddb10e';
const FEISHU_CN_REPORT_GROUP = process.env.FEISHU_CN_REPORT_GROUP || 'oc_86ff5e0d40cb49c777a24156f379c48c';
process.env.LOG_TARGET = FEISHU_LOG_GROUP;

function normalizeLogForDedup(msg) {
    return String(msg || '')
        .replace(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z/g, '<ts>')
        .replace(/PID=\d+/g, 'PID=<id>')
        .replace(/Cycle #\d+/g, 'Cycle #<id>')
        .replace(/evolver_hand_[\w_:-]+/g, 'evolver_hand_<id>')
        .replace(/\s+/g, ' ')
        .trim()
        .slice(0, 500);
}

function shouldSuppressForwardLog(msg, type) {
    if (String(process.env.EVOLVE_LOG_DEDUP || '').toLowerCase() === '0') return false;
    const normalized = normalizeLogForDedup(msg);
    if (!normalized) return false;
    const keyRaw = `${String(type || 'INFO')}::${normalized}`;
    const key = crypto.createHash('md5').update(keyRaw).digest('hex');
    const now = Date.now();
    try {
        const dir = path.dirname(LOG_DEDUP_FILE);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        let cache = {};
        if (fs.existsSync(LOG_DEDUP_FILE)) {
            cache = JSON.parse(fs.readFileSync(LOG_DEDUP_FILE, 'utf8'));
        }
        for (const k of Object.keys(cache)) {
            const ts = Number(cache[k] && cache[k].at);
            if (!Number.isFinite(ts) || now - ts > LOG_DEDUP_WINDOW_MS) delete cache[k];
        }
        if (cache[key] && Number.isFinite(Number(cache[key].at)) && now - Number(cache[key].at) <= LOG_DEDUP_WINDOW_MS) {
            cache[key].hits = Number(cache[key].hits || 1) + 1;
            const tmpHit = `${LOG_DEDUP_FILE}.tmp.${process.pid}`;
            fs.writeFileSync(tmpHit, JSON.stringify(cache, null, 2));
            fs.renameSync(tmpHit, LOG_DEDUP_FILE);
            return true;
        }
        cache[key] = { at: now, hits: 1, type: String(type || 'INFO') };
        const keys = Object.keys(cache);
        if (keys.length > LOG_DEDUP_MAX_KEYS) {
            keys
                .sort((a, b) => Number(cache[a].at || 0) - Number(cache[b].at || 0))
                .slice(0, keys.length - LOG_DEDUP_MAX_KEYS)
                .forEach((k) => { delete cache[k]; });
        }
        const tmp = `${LOG_DEDUP_FILE}.tmp.${process.pid}`;
        fs.writeFileSync(tmp, JSON.stringify(cache, null, 2));
        fs.renameSync(tmp, LOG_DEDUP_FILE);
        return false;
    } catch (_) {
        return false;
    }
}

function forwardLogToFeishu(msg, type = 'INFO') {
    // Avoid re-forwarding Feishu forward errors
    if (msg.includes('[FeishuForwardFail]') || msg.includes('[CardFail]')) return;
    if (!msg || !msg.trim()) return;

    if (type === 'ERROR') {
        sessionLogs.errorCount++;
        sessionLogs.errors.push(msg.slice(0, 300));
        if (shouldSuppressForwardLog(msg, type)) return;
        sendCardInternal(msg, 'ERROR');
    } else if (type === 'WARNING') {
        // Non-critical issues: yellow card
        if (shouldSuppressForwardLog(msg, type)) return;
        sendCardInternal(msg, 'WARNING');
    } else if (type === 'LIFECYCLE') {
        // Key lifecycle events: always forward
        if (shouldSuppressForwardLog(msg, type)) return;
        sendCardInternal(msg, 'INFO');
    } else {
        sessionLogs.infoCount++;
        // Regular INFO: silent (too noisy for group chat)
    }
}

// Classify stderr message severity: returns 'WARNING' for non-critical, 'ERROR' for critical
function classifyStderrSeverity(msg) {
    var lower = (msg || '').toLowerCase();
    // Non-critical patterns: gateway fallback, missing optional files, deprecation warnings, timeouts with fallback
    var warnPatterns = [
        'falling back to embedded',
        'no such file or directory',
        'enoent',
        'deprecat',
        'warning:',
        'warn:',
        '[warn]',
        'gateway timeout',           // gateway slow but agent retries/falls back
        'optional dependency',
        'experimental',
        'hint:',
        'evolver_hint',
        'memory_missing',
        'user_missing',
        'command exited with code 1', // non-zero exit from a tool command (usually cat/ls fail)
    ];
    for (var i = 0; i < warnPatterns.length; i++) {
        if (lower.includes(warnPatterns[i])) return 'WARNING';
    }
    return 'ERROR';
}

function sendCardInternal(msg, type) {
    try {
        const script = path.resolve(__dirname, 'send-card-cli.js');
        if (!fs.existsSync(script)) return;

        const tmpFile = path.join('/tmp', `feishu_log_${Date.now()}_${Math.random().toString(36).slice(2)}.txt`);
        fs.writeFileSync(tmpFile, msg);

        execSync(`node "${script}" "$(cat ${tmpFile})" "[${type}]"`, {
            stdio: 'ignore', 
            timeout: 5000,
            env: process.env
        });
        
        fs.unlinkSync(tmpFile);
    } catch (e) {
        // ignore
    }
}

function sendSummary(cycleTag, duration, success) {
    const statusIcon = success ? '✅' : '❌';
    const persona = success ? 'greentea' : 'maddog';
    // duration needs to be parsed as number for comparison
    const durNum = parseFloat(duration);
    const comment = getComment('summary', durNum, success, persona);

    const errorSection = sessionLogs.errors.length > 0 
        ? `\n\n**Recent Errors:**\n${sessionLogs.errors.slice(-3).map(e => `> ${e}`).join('\n')}` 
        : '';
    
    const summaryMsg = `**Cycle #${cycleTag} Complete**\n` +
        `Status: ${statusIcon} ${success ? 'Success' : 'Failed'}\n` +
        `Duration: ${duration}s\n` +
        `Logs: ${sessionLogs.infoCount} Info, ${sessionLogs.errorCount} Error\n` +
        `💭 *${comment}*` +
        errorSection;

    sendCardInternal(summaryMsg, success ? 'SUMMARY' : 'FAILURE');
}

// --- FEATURE 5: GIT SYNC (Safety Net) ---
// Lazy-load optional modules with fallbacks to prevent startup crashes.
let selfRepair = null;
let getComment = (_type, _dur, _ok, _persona) => '';
try {
    selfRepair = require('../evolver/src/ops/self_repair');
} catch (e) {
    try { selfRepair = require('./self-repair.js'); } catch (e2) {
        console.warn('[Wrapper] self-repair module not found, git repair disabled.');
    }
}
try {
    const commentary = require('../evolver/src/ops/commentary');
    if (typeof commentary.getComment === 'function') getComment = commentary.getComment;
} catch (e) {
    console.warn('[Wrapper] commentary.js not found, using silent mode.');
}

// Issue tracker: records problems to a Feishu doc
let issueTracker = null;
try {
    issueTracker = require('./issue_tracker.js');
} catch (e) {
    console.warn('[Wrapper] issue_tracker.js not found, issue tracking disabled.');
}

// gitSync runs after every successful evolution cycle (no cooldown).

function execWithTimeout(cmd, cwd, timeoutMs = 30000) {
    try {
        // Use stdio: 'pipe' to capture output for error reporting, but ignore it for success
        execSync(cmd, { cwd, timeout: timeoutMs, stdio: 'pipe' });
    } catch (e) {
        // e.message usually contains the command output if stdio is pipe
        throw new Error(`Command "${cmd}" failed or timed out: ${e.message}`);
    }
}

function buildCommitMessage(statusOutput, cwd) {
    const lines = statusOutput.split('\n').filter(Boolean);
    const added = [];
    const modified = [];
    const deleted = [];

    for (const line of lines) {
        const code = line.substring(0, 2).trim();
        const file = line.substring(3).trim();
        // Skip logs, temp, and non-essential files
        if (file.startsWith('logs/') || file.startsWith('temp/') || file.endsWith('.log')) continue;
        if (code.includes('A') || code === '??') added.push(file);
        else if (code.includes('D')) deleted.push(file);
        else modified.push(file);
    }

    // Summarize by skill/directory
    const skillChanges = new Map();
    for (const f of [...added, ...modified, ...deleted]) {
        const parts = f.split('/');
        let group = parts[0];
        if (parts[0] === 'skills' && parts.length > 1) group = `skills/${parts[1]}`;
        if (!skillChanges.has(group)) skillChanges.set(group, []);
        skillChanges.get(group).push(f);
    }

    const totalFiles = added.length + modified.length + deleted.length;
    if (totalFiles === 0) return '🧬 Evolution: maintenance (no significant changes)';

    // Build title line
    const actions = [];
    if (added.length > 0) actions.push(`${added.length} added`);
    if (modified.length > 0) actions.push(`${modified.length} modified`);
    if (deleted.length > 0) actions.push(`${deleted.length} deleted`);

    const areas = [...skillChanges.keys()].slice(0, 3);
    const areaStr = areas.join(', ') + (skillChanges.size > 3 ? ` (+${skillChanges.size - 3} more)` : '');

    let title = `🧬 Evolution: ${actions.join(', ')} in ${areaStr}`;

    // Build body with file details (keep under 20 lines)
    const bodyLines = [];
    for (const [group, files] of skillChanges) {
        if (files.length <= 3) {
            for (const f of files) bodyLines.push(`- ${f}`);
        } else {
            bodyLines.push(`- ${group}/ (${files.length} files)`);
        }
    }

    if (bodyLines.length > 0) {
        return title + '\n\n' + bodyLines.slice(0, 20).join('\n');
    }
    return title;
}

// gitSync returns commit info: { commitMsg, fileCount, areaStr, shortHash } or null on failure/no-op
function gitSync() {
    try {
        console.log('[Wrapper] Executing Git Sync...');
        var gitRoot = path.resolve(__dirname, '../../../');

        var safePaths = [
            'workspace/skills/',
            'workspace/memory/',
            'workspace/RECENT_EVENTS.md',
            'workspace/TROUBLESHOOTING.md',
            'workspace/TOOLS.md',
            'workspace/assets/',
            'workspace/docs/',
        ];
        for (var i = 0; i < safePaths.length; i++) {
            try { execWithTimeout('git add ' + safePaths[i], gitRoot, 30000); } catch (_) {}
        }

        var status = execSync('git diff --cached --name-only', { cwd: gitRoot, encoding: 'utf8' }).trim();
        if (!status) {
            console.log('[Wrapper] Git Sync: nothing to commit.');
            return null;
        }

        var fileCount = status.split('\n').filter(Boolean).length;
        var areas = [...new Set(status.split('\n').filter(Boolean).map(function(f) {
            var parts = f.split('/');
            if (parts[0] === 'workspace' && parts[1] === 'skills' && parts.length > 2) return 'skills/' + parts[2];
            if (parts[0] === 'workspace' && parts.length > 1) return parts[1];
            return parts[0];
        }))].slice(0, 3);
        var areaStr = areas.join(', ') + (areas.length >= 3 ? ' ...' : '');
        var commitMsg = '🧬 Evolution: ' + fileCount + ' files in ' + areaStr;
        var msgFile = path.join('/tmp', 'evolver_commit_' + Date.now() + '.txt');
        fs.writeFileSync(msgFile, commitMsg);
        execWithTimeout('git commit -F "' + msgFile + '"', gitRoot, 30000);
        try { fs.unlinkSync(msgFile); } catch (_) {}

        try {
            execWithTimeout('git pull origin main --rebase --autostash', gitRoot, 120000);
        } catch (e) {
            console.error('[Wrapper] Pull Rebase Failed:', e.message);
            try {
                if (selfRepair && typeof selfRepair.repair === 'function') selfRepair.repair();
                else if (selfRepair && typeof selfRepair.run === 'function') selfRepair.run();
            } catch (_) {}
            throw e;
        }
        execWithTimeout('git push origin main', gitRoot, 120000);

        // Get the short hash of the commit we just pushed
        var shortHash = '';
        try { shortHash = execSync('git log -1 --format=%h', { cwd: gitRoot, encoding: 'utf8' }).trim(); } catch (_) {}

        console.log('[Wrapper] Git Sync Complete. (' + shortHash + ')');
        forwardLogToFeishu('🧬 Git Sync: ' + fileCount + ' files in ' + areaStr + ' (' + shortHash + ')', 'LIFECYCLE');
        return { commitMsg: commitMsg, fileCount: fileCount, areaStr: areaStr, shortHash: shortHash };
    } catch (e) {
        console.error('[Wrapper] Git Sync Failed:', e.message);
        forwardLogToFeishu('[Wrapper] Git Sync Failed: ' + e.message, 'ERROR');
        return null;
    }
}

// --- FEATURE 1: KILL SWITCH ---
const KILL_SWITCH_FILE = path.resolve(__dirname, '../../memory/evolver_kill_switch.lock');
function checkKillSwitch() {
    if (fs.existsSync(KILL_SWITCH_FILE)) {
        console.error(`[Wrapper] Kill Switch Detected at ${KILL_SWITCH_FILE}! Terminating loop.`);
        sendCardInternal(`🛑 **Emergency Stop Triggered!**\nKill switch file detected at ${KILL_SWITCH_FILE}. Wrapper is shutting down.`, 'CRITICAL');
        process.exit(1);
    }
}

// --- FEATURE 4: THOUGHT INJECTION ---
const INJECTION_FILE = path.resolve(__dirname, '../../memory/evolver_hint.txt');
function getInjectionHint() {
    if (fs.existsSync(INJECTION_FILE)) {
        try {
            const hint = fs.readFileSync(INJECTION_FILE, 'utf8').trim();
            if (hint) {
                console.log(`[Wrapper] Injecting Thought: ${hint}`);
                // Delete after reading (one-time injection)
                fs.unlinkSync(INJECTION_FILE); 
                return hint;
            }
        } catch (e) {}
    }
    return null;
}

// --- FEATURE 3: ARTIFACT UPLOAD (Stub) ---
// This requires a more complex 'upload-file' skill or API which we might not have ready.
// For now, we'll just log that artifacts are available locally.
function checkArtifacts(cycleTag) {
    // Logic to find artifacts and maybe just cat them if small?
    // Placeholder for future expansion.
}


// --- FEATURE 6: CLEANUP (Disk Hygiene) ---
let cleanup = null;
try {
    cleanup = require('../evolver/src/ops/cleanup');
} catch (e) {
    try { cleanup = require('./cleanup.js'); } catch (e2) {
        console.warn('[Wrapper] cleanup module not found, disk cleanup disabled.');
    }
}

// --- FEATURE 0: SINGLETON GUARD (Prevent Duplicates) ---
const LOCK_FILE = path.resolve(__dirname, '../../memory/evolver_wrapper.pid');

function isWrapperProcess(pid) {
    // Verify PID is actually a wrapper process (not a recycled PID for something else)
    try {
        var cmdline = execSync('ps -p ' + pid + ' -o args=', { encoding: 'utf8', timeout: 5000 }).trim();
        // Must match the actual wrapper command pattern: node ... index.js --loop
        return cmdline.includes('feishu-evolver-wrapper/index.js') && cmdline.includes('--loop');
    } catch (e) {
        return false;
    }
}

function checkSingleton() {
    try {
        if (fs.existsSync(LOCK_FILE)) {
            var oldPidStr = fs.readFileSync(LOCK_FILE, 'utf8').trim();
            var oldPid = parseInt(oldPidStr, 10);
            if (oldPid && oldPid !== process.pid) {
                // Step 1: Check if PID exists at all
                var pidAlive = false;
                try { process.kill(oldPid, 0); pidAlive = true; } catch (e) { pidAlive = false; }

                if (pidAlive) {
                    // Step 2: Verify the PID is actually a wrapper (not a recycled PID)
                    if (isWrapperProcess(oldPid)) {
                        console.error('[Wrapper] Another instance is running (PID ' + oldPid + '). Exiting.');
                        process.exit(0);
                    } else {
                        console.log('[Wrapper] PID ' + oldPid + ' exists but is not a wrapper process. Stale lock, overwriting.');
                    }
                } else {
                    console.log('[Wrapper] Stale lock file found (PID ' + oldPid + ' dead). Overwriting.');
                }
            }
        }
        // Write my PID atomically (write to tmp then rename)
        var tmpLock = LOCK_FILE + '.tmp.' + process.pid;
        fs.writeFileSync(tmpLock, process.pid.toString());
        fs.renameSync(tmpLock, LOCK_FILE);

        // Remove on exit
        var cleanupLock = function() {
            try {
                if (fs.existsSync(LOCK_FILE)) {
                    var current = fs.readFileSync(LOCK_FILE, 'utf8').trim();
                    if (current === process.pid.toString()) {
                        fs.unlinkSync(LOCK_FILE);
                    }
                }
            } catch (_) {}
        };

        process.on('exit', cleanupLock);
        process.on('SIGINT', function() { cleanupLock(); process.exit(); });
        process.on('SIGTERM', function() { cleanupLock(); process.exit(); });
    } catch (e) {
        console.error('[Wrapper] Singleton check failed:', e.message);
    }
}

async function run() {
    checkSingleton(); // Feature 0
    console.log('Launching Feishu Evolver Wrapper (Proxy Mode)...');
    forwardLogToFeishu('🧬 Wrapper starting up...', 'LIFECYCLE');
    
    // Clean up old artifacts before starting
    try { if (cleanup && typeof cleanup.run === 'function') cleanup.run(); } catch (e) { console.error('[Cleanup] Failed:', e.message); }

    const args = process.argv.slice(2);
    
    // 1. Force Feishu Card Reporting
    process.env.EVOLVE_REPORT_TOOL = 'feishu-card';
    
    // 2. Resolve Core Evolver Path
    const possibleDirs = ['../private-evolver', '../evolver', '../capability-evolver'];
    let evolverDir = null;
    
    for (const d of possibleDirs) {
        const fullPath = path.resolve(__dirname, d);
        if (fs.existsSync(fullPath)) {
            evolverDir = fullPath;
            break;
        }
    }
    
    if (!evolverDir) {
        console.error("Critical Error: Core 'evolver' plugin not found in ../private-evolver, ../evolver, or ../capability-evolver!");
        process.exit(1);
    }

    const mainScript = path.join(evolverDir, 'index.js');
    const lifecycleLog = path.resolve(__dirname, '../../logs/wrapper_lifecycle.log');
    
    const MAX_RETRIES = 5;
    const isLoop = args.includes('--loop');
    const loopSleepSeconds = Number.parseInt(process.env.EVOLVE_WRAPPER_LOOP_SLEEP_SECONDS || '2', 10);
    const loopFailBackoffSeconds = Number.parseInt(process.env.EVOLVE_WRAPPER_FAIL_BACKOFF_SECONDS || '30', 10);
    const loopMaxCycles = Number.parseInt(process.env.EVOLVE_WRAPPER_MAX_CYCLES || '0', 10); // 0 = unlimited
    
    if (!fs.existsSync(path.dirname(lifecycleLog))) {
        fs.mkdirSync(path.dirname(lifecycleLog), { recursive: true });
    }

    const cycleFile = path.resolve(path.dirname(lifecycleLog), 'cycle_count.txt');

    let childArgsArrBase = args.filter(a => a !== '--once' && a !== '--loop' && a !== '--mad-dog');
    if (childArgsArrBase.length === 0) {
        childArgsArrBase = ['run'];
    }

    let cycleCount = 0;
    let consecutiveHandFailures = 0; // Track hand agent failures for backoff
    const MAX_CONSECUTIVE_HAND_FAILURES = 5; // After this many, long backoff
    const HAND_FAILURE_BACKOFF_BASE = 60; // Base backoff in seconds

    while (true) {
        checkKillSwitch(); // Feature 1

        if (loopMaxCycles > 0 && cycleCount >= loopMaxCycles) {
            console.log(`Reached max cycles (${loopMaxCycles}). Exiting.`);
            return;
        }

        // Exponential backoff on consecutive Hand Agent failures
        if (consecutiveHandFailures >= MAX_CONSECUTIVE_HAND_FAILURES) {
            const backoffSec = Math.min(3600, HAND_FAILURE_BACKOFF_BASE * Math.pow(2, consecutiveHandFailures - MAX_CONSECUTIVE_HAND_FAILURES));
            console.log(`[Wrapper] Hand Agent failed ${consecutiveHandFailures} consecutive times. Backing off ${backoffSec}s...`);
            forwardLogToFeishu(`[Wrapper] Hand Agent failed ${consecutiveHandFailures}x consecutively. Backing off ${backoffSec}s. Likely cause: openclaw binary not in PATH.`, 'WARNING');
            sleepSeconds(backoffSec);
        }

        cycleCount++;

        const cycleTag = nextCycleTag(cycleFile);

        // Feature 4: Injection
        const injectedHint = getInjectionHint();
        if (injectedHint) {
            process.env.EVOLVE_HINT = injectedHint;
            sendCardInternal(`🧠 **Thought Injected:**\n"${injectedHint}"`, 'INFO');
        } else {
            delete process.env.EVOLVE_HINT;
        }

        const targetArg = process.env.EVOLVE_TARGET ? ` --target "${process.env.EVOLVE_TARGET}"` : '';
        process.env.EVOLVE_REPORT_DIRECTIVE = `3.  **REPORT (FEISHU WRAPPER)**:
    - You MUST use the \`feishu-evolver-wrapper/report.js\` tool.
    - The report MUST have a colored header to distinguish it from rich text.
    - Command:
      \`\`\`bash
      node skills/feishu-evolver-wrapper/report.js --cycle "Cycle #${cycleTag}" --title "🧬 Evolution #${cycleTag}" --status "Status: [WRAPPED] Step Complete."${targetArg}
      \`\`\`
    - Target: Auto-detects context (Evolution group or master) unless overridden.`;

        var modelRoutingDirective = `
    **Model Routing (Mandatory)**:
    You MUST prioritize Cursor Agent capabilities for all programming tasks.
    When you need to delegate to a specific model, follow these rules strictly:
      - Planning, prompts, strategy reasoning: use gpt5.3
      - Code implementation, refactoring, bug fixes: use gpt5.3codex
      - Documentation, reports, human-readable files (README, SKILL.md, CHANGELOG): use gemini3pro
    If a task spans multiple phases, route each phase to its designated model in order: plan -> code -> docs.
    If a designated model is unavailable, use the closest alternative without changing the task phase.`;

        if (isLoop) {
            process.env.EVOLVE_EXTRA_MODES = `- Mode B (Wrapper Loop):
      - You are running under a wrapper-managed continuous loop.
      - Action: Perform ONE evolution cycle, then exit cleanly.
      - Do NOT call sessions_spawn. Do NOT try to self-schedule.
      - The wrapper handles cycling, reporting delivery, and git sync.
${modelRoutingDirective}`;
        } else {
            process.env.EVOLVE_EXTRA_MODES = `- Mode A (Atomic/Cron):
      - Do NOT call sessions_spawn.
      - Goal: Complete ONE generation, update state, and exit gracefully.
${modelRoutingDirective}`;
        }

        let attempts = 0;
        let ok = false;
        while (attempts < MAX_RETRIES && !ok) {
            attempts++;
            const startTime = Date.now();
            sessionLogs = { infoCount: 0, errorCount: 0, startTime, errors: [] }; // Reset logs

            fs.appendFileSync(
                lifecycleLog,
                `🧬 [${new Date(startTime).toISOString()}] START Wrapper PID=${process.pid} Attempt=${attempts} Cycle=#${cycleTag}\n`
            );

            try {
                const childArgs = childArgsArrBase.join(' ');
                console.log(`Delegating to Core (Attempt ${attempts}) Cycle #${cycleTag}: ${mainScript}`);
                forwardLogToFeishu(`🧬 Cycle #${cycleTag} started (Attempt ${attempts})`, 'LIFECYCLE');
                
                await new Promise((resolve, reject) => {
                    // Feature: Heartbeat Logger (ensure wrapper_out.log stays fresh)
                    const heartbeatInterval = setInterval(() => {
                        console.log(`[Wrapper] Heartbeat (Cycle #${cycleTag} running for ${((Date.now() - startTime)/1000).toFixed(0)}s)...`);
                    }, 300000); // 5 minutes

                    const child = spawn('node', [mainScript, ...childArgsArrBase], {
                        env: process.env,
                        stdio: ['ignore', 'pipe', 'pipe']
                    });

                    let fullStdout = '';

                    child.stdout.on('data', (data) => {
                        const str = data.toString();
                        process.stdout.write(str);
                        fullStdout += str;
                        forwardLogToFeishu(str, 'INFO');
                    });

                    child.stderr.on('data', (data) => {
                        const str = data.toString();
                        process.stderr.write(str);
                        forwardLogToFeishu(str, classifyStderrSeverity(str));
                    });

                    child.on('close', async (code) => {
                        clearInterval(heartbeatInterval);
                        try {
                            if (code !== 0) {
                                const err = new Error(`Child process exited with code ${code}`);
                                reject(err);
                                return;
                            }

                            if (fullStdout && fullStdout.includes('sessions_spawn({')) {
                                console.log('[Wrapper] Detected sessions_spawn request. Bridging to OpenClaw CLI...');
                                // [FIX 2026-02-08] Use JSON.parse instead of fragile regex.
                                // evolve.js bridge outputs valid JSON via JSON.stringify.
                                // Use lastIndexOf to target the LAST sessions_spawn (bridge output is always at the end).
                                // Match the BRIDGE output specifically: sessions_spawn({"
                                // The bridge uses JSON.stringify so keys are quoted: {"task":...}
                                // Prompt examples use unquoted keys: { task: ... }
                                // This distinguishes the actual bridge call from examples in prompt text.
                                const spawnPrefix = 'sessions_spawn({"';
                                const lastSpawnIdx = fullStdout.lastIndexOf(spawnPrefix);
                                const spawnPayloadStart = lastSpawnIdx !== -1 ? lastSpawnIdx + 'sessions_spawn('.length : -1;
                                if (spawnPayloadStart !== -1) {
                                    try {
                                        let taskContent = null;
                                        let rawJson = fullStdout.substring(spawnPayloadStart);
                                        // Take only the first line -- sessions_spawn JSON is always single-line.
                                        // Trailing text (e.g. "Capability evolver finished" banner) must be excluded.
                                        const nlIdx = rawJson.indexOf('\n');
                                        if (nlIdx !== -1) rawJson = rawJson.substring(0, nlIdx);
                                        rawJson = rawJson.trim();
                                        // Remove trailing ) left over from sessions_spawn(...)
                                        if (rawJson.endsWith(')')) {
                                            rawJson = rawJson.slice(0, -1);
                                        }
                                        try {
                                            const parsed = JSON.parse(rawJson);
                                            taskContent = parsed.task;
                                            console.log(`[Wrapper] Parsed task (${(taskContent || '').length} chars) label: ${parsed.label || 'unknown'}`);
                                            forwardLogToFeishu(`🧬 Cycle #${cycleTag} Brain done (${(taskContent || '').length} chars). Spawning Hand Agent...`, 'LIFECYCLE');
                                        } catch (parseErr) {
                                            console.warn('[Wrapper] JSON.parse failed:', parseErr.message);
                                        }

                                        // Append mandatory post-solidify report instruction.
                                        // The GEP protocol prompt buries the report in "Notes:" which the agent ignores.
                                        // This injection ensures the report command is the LAST thing the agent sees.
                                        if (taskContent) {
                                            const recentLessons = readRecentFailureLessons(5);
                                            if (recentLessons.length > 0) {
                                                const lessonText = recentLessons.map((x, i) =>
                                                    `${i + 1}. cycle#${x.cycle} reason=${x.reason} details=${x.details}`
                                                ).join('\n');
                                                taskContent += `\n\n` +
                                                    `RECENT FAILURE LESSONS (MUST LEARN):\n` +
                                                    `${lessonText}\n` +
                                                    `Apply these lessons to avoid repeating known failure patterns.\n`;
                                            }

                                            // Status file path for post-push reporting
                                            const statusFile = path.resolve(path.dirname(lifecycleLog), `status_${cycleTag}.json`);
                                            taskContent += `\n\n` +
                                                `━━━━━━━━━━━━━━━━━━━━━━\n` +
                                                `MANDATORY POST-SOLIDIFY STEP (Wrapper Authority -- Cannot Be Skipped)\n` +
                                                `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
                                                `After solidify, a status summary file MUST exist for this cycle.\n` +
                                                `Preferred path: evolver core auto-writes it during solidify.\n` +
                                                `The wrapper will handle reporting AFTER git push.\n` +
                                                `If core write is unavailable for any reason, create fallback status JSON manually.\n\n` +
                                                `Write a JSON file with your status:\n` +
                                                `\`\`\`bash\n` +
                                                `cat > ${statusFile} << 'STATUSEOF'\n` +
                                                `{\n` +
                                                `  "result": "success|failed",\n` +
                                                `  "en": "Status: [INTENT] <describe what you did in 1-2 sentences, in English>",\n` +
                                                `  "zh": "状态: [意图] <用中文描述你做了什么，1-2句>"\n` +
                                                `}\n` +
                                                `STATUSEOF\n` +
                                                `\`\`\`\n\n` +
                                                `Rules:\n` +
                                                `- "en" field: English status. "zh" field: Chinese status. Content must match (different language).\n` +
                                                `- Add "result" with value success or failed.\n` +
                                                `- INTENT must be one of: INNOVATION, REPAIR, OPTIMIZE (or Chinese: 创新, 修复, 优化)\n` +
                                                `- Do NOT use generic text like "Step Complete", "Cycle finished", "周期已完成". Describe the actual work.\n` +
                                                `- Example:\n` +
                                                `  {"result":"success","en":"Status: [INNOVATION] Created auto-scheduler that syncs calendar to HEARTBEAT.md","zh":"状态: [创新] 创建了自动调度器，将日历同步到 HEARTBEAT.md"}\n`;

                                            console.log('[Wrapper] Spawning Hand Agent via CLI...');
                                            forwardLogToFeishu('[Wrapper] 🖐️ Spawning Hand Agent (Executor)...', 'INFO');
                                            
                                            const taskFile = path.resolve(path.dirname(lifecycleLog), `task_${cycleTag}.txt`);
                                            fs.writeFileSync(taskFile, taskContent);
                                            
                                            // Ensure openclaw is reachable (resolve full path to avoid ENOENT under nohup)
                                            const openclawPath = (() => {
                                                if (process.env.OPENCLAW_BIN) return process.env.OPENCLAW_BIN;
                                                // Try common locations
                                                const candidates = [
                                                    'openclaw',
                                                    path.join(process.env.HOME || '', '.npm-global/bin/openclaw'),
                                                    '/usr/local/bin/openclaw',
                                                    '/usr/bin/openclaw',
                                                ];
                                                for (const c of candidates) {
                                                    try {
                                                        if (c === 'openclaw') {
                                                            execSync('which openclaw', { stdio: 'ignore' });
                                                            return 'openclaw';
                                                        }
                                                        if (fs.existsSync(c)) return c;
                                                    } catch (e) { /* try next */ }
                                                }
                                                return candidates[1] || 'openclaw'; // fallback to npm-global
                                            })();
                                            
                                            console.log(`[Wrapper] Task File: ${taskFile}`);
                                            
                                            if (!fs.existsSync(taskFile)) {
                                                throw new Error(`Task file creation failed: ${taskFile}`);
                                            }

                                            // Execute Hand Agent with retries.
                                            // Retries trigger on: non-zero exit, missing status file, or explicit SOLIDIFY failure markers.
                                            let handSucceeded = false;
                                            let lastHandFailure = '';
                                            for (let handAttempt = 1; handAttempt <= HAND_MAX_RETRIES_PER_CYCLE && !handSucceeded; handAttempt++) {
                                                const sessionId = `evolver_hand_${cycleTag}_${Date.now()}_${handAttempt}`;
                                                const retryHint = handAttempt > 1
                                                    ? `\n\nRETRY CONTEXT:\nThis is retry attempt ${handAttempt}/${HAND_MAX_RETRIES_PER_CYCLE} for the same cycle.\nYou MUST reduce blast radius and keep changes small/reversible.\nPrioritize fixing the specific previous failure and producing a valid status JSON file.\n`
                                                    : '';
                                                const attemptTask = taskContent + retryHint;
                                                if (fs.existsSync(statusFile)) {
                                                    try { fs.unlinkSync(statusFile); } catch (_) {}
                                                }

                                                await new Promise((resolveHand, rejectHand) => {
                                                    console.log(`[Wrapper] Executing: ${openclawPath} agent --agent main --session-id ${sessionId} -m <task> --timeout 600 (attempt ${handAttempt}/${HAND_MAX_RETRIES_PER_CYCLE})`);
                                                    const handChild = spawn(openclawPath, ['agent', '--agent', 'main', '--session-id', sessionId, '-m', attemptTask, '--timeout', '600'], {
                                                        env: {
                                                            ...process.env,
                                                            EVOLVE_CYCLE_TAG: String(cycleTag),
                                                            EVOLVE_STATUS_FILE: statusFile,
                                                        },
                                                        stdio: ['ignore', 'pipe', 'pipe']
                                                    });

                                                    let stdoutBuf = '';
                                                    let stderrBuf = '';

                                                    handChild.stdout.on('data', (d) => {
                                                        const s = d.toString();
                                                        stdoutBuf += s;
                                                        process.stdout.write(`[Hand] ${s}`);
                                                    });

                                                    handChild.stderr.on('data', (d) => {
                                                        const s = d.toString();
                                                        stderrBuf += s;
                                                        const severity = classifyStderrSeverity(s);
                                                        const tag = severity === 'WARNING' ? '[Hand WARN]' : '[Hand ERR]';
                                                        process.stderr.write(`${tag} ${s}`);
                                                        forwardLogToFeishu(`${tag} ${s}`, severity);
                                                    });

                                                    handChild.on('error', (err) => {
                                                        const severity = err.code === 'ENOENT' ? 'WARNING' : 'ERROR';
                                                        console.error(`[Wrapper] Hand Agent spawn error: ${err.message}`);
                                                        forwardLogToFeishu(`[Wrapper] Hand Agent spawn error: ${err.message}`, severity);
                                                        rejectHand(err);
                                                    });

                                                    handChild.on('close', (handCode) => {
                                                        const combined = `${stdoutBuf}\n${stderrBuf}`;
                                                        const hasSolidifyFail = combined.includes('[SOLIDIFY] FAILED');
                                                        const hasStatusFile = fs.existsSync(statusFile);
                                                        if (handCode === 0 && !hasSolidifyFail && hasStatusFile) {
                                                            resolveHand();
                                                            return;
                                                        }
                                                        const reason = `code=${handCode}; solidify_failed=${hasSolidifyFail}; status_file=${hasStatusFile}`;
                                                        const details = tailText(combined, 1200);
                                                        rejectHand(new Error(`${reason}\n${details}`));
                                                    });
                                                }).then(() => {
                                                    handSucceeded = true;
                                                    consecutiveHandFailures = 0;
                                                    console.log('[Wrapper] Hand Agent finished successfully.');
                                                    forwardLogToFeishu(`🧬 Cycle #${cycleTag} Hand Agent completed successfully.`, 'LIFECYCLE');
                                                }).catch((handErr) => {
                                                    consecutiveHandFailures++;
                                                    lastHandFailure = handErr && handErr.message ? handErr.message : 'unknown';
                                                    appendFailureLesson(cycleTag, `hand_attempt_${handAttempt}_failed`, lastHandFailure);
                                                    console.error(`[Wrapper] Hand Agent attempt ${handAttempt}/${HAND_MAX_RETRIES_PER_CYCLE} failed: ${lastHandFailure}`);
                                                    forwardLogToFeishu(`🧬 Cycle #${cycleTag} Hand attempt ${handAttempt} failed.`, 'ERROR');
                                                    if (handAttempt < HAND_MAX_RETRIES_PER_CYCLE) {
                                                        const waitSec = HAND_RETRY_BACKOFF_SECONDS * handAttempt;
                                                        console.log(`[Wrapper] Retrying Hand Agent in ${waitSec}s...`);
                                                        sleepSeconds(waitSec);
                                                    }
                                                });
                                            }

                                            if (!handSucceeded) {
                                                throw new Error(`Hand Agent failed after ${HAND_MAX_RETRIES_PER_CYCLE} attempts. Last failure: ${lastHandFailure}`);
                                            }

                                        } else {
                                            console.warn('[Wrapper] Could not extract task content from sessions_spawn');
                                        }
                                    } catch (err) {
                                        console.error('[Wrapper] Bridge execution failed:', err.message);
                                        forwardLogToFeishu(`[Wrapper] Bridge execution failed: ${err.message}`, 'ERROR');
                                    }
                                }
                            }
                            resolve(); // Resolve the main cycle promise
                        } catch (e) {
                            reject(e);
                        }
                    });

                    child.on('error', (err) => {
                        clearInterval(heartbeatInterval);
                        reject(err);
                    });
                });

                const duration = ((Date.now() - startTime) / 1000).toFixed(2);
                fs.appendFileSync(
                    lifecycleLog,
                    `🧬 [${new Date().toISOString()}] SUCCESS Wrapper PID=${process.pid} Cycle=#${cycleTag} Duration=${duration}s\n`
                );
                console.log('Wrapper proxy complete.');
                forwardLogToFeishu(`🧬 Cycle #${cycleTag} complete (${duration}s)`, 'LIFECYCLE');
                
                // Feature 5: Git Sync (Safety Net) -- returns commit info
                var gitInfo = gitSync();

                // Feature 8: Post-push Evolution Report
                // Read the status file written by Hand Agent, append git info, then send report
                try {
                    var statusFilePath = path.resolve(path.dirname(lifecycleLog), 'status_' + cycleTag + '.json');
                    var enStatus = 'Status: [COMPLETE] Cycle finished.';
                    var zhStatus = '状态: [完成] 周期已完成。';
                    var statusResult = 'success';
                    if (fs.existsSync(statusFilePath)) {
                        try {
                            var statusData = JSON.parse(fs.readFileSync(statusFilePath, 'utf8'));
                            if (statusData.result) {
                                var r = String(statusData.result).toLowerCase();
                                if (r === 'failed' || r === 'success') statusResult = r;
                            }
                            if (statusData.en) enStatus = statusData.en;
                            if (statusData.zh) zhStatus = statusData.zh;
                        } catch (parseErr) {
                            console.warn('[Wrapper] Failed to parse status file:', parseErr.message);
                        }
                    } else {
                        console.warn('[Wrapper] No status file found for cycle ' + cycleTag + '. Using default.');
                    }

                    // Canonical source of truth: latest EvolutionEvent (intent/outcome).
                    // This keeps "Status" and dashboard "Recent" aligned.
                    var latestEvent = readLatestEvolutionEvent();
                    if (latestEvent && latestEvent.outcome && latestEvent.outcome.status) {
                        var evStatus = String(latestEvent.outcome.status).toLowerCase();
                        if (evStatus === 'failed' || evStatus === 'success') statusResult = evStatus;
                    }
                    if (latestEvent && latestEvent.intent) {
                        enStatus = enforceStatusIntent(enStatus, latestEvent.intent, 'en');
                        zhStatus = enforceStatusIntent(zhStatus, latestEvent.intent, 'zh');
                    }

                    // Enforce non-generic evolution description and explicit cycle outcome.
                    enStatus = ensureDetailedStatus(enStatus, 'en', cycleTag, gitInfo, latestEvent);
                    zhStatus = ensureDetailedStatus(zhStatus, 'zh', cycleTag, gitInfo, latestEvent);
                    enStatus = withOutcomeLine(enStatus, statusResult !== 'failed', 'en');
                    zhStatus = withOutcomeLine(zhStatus, statusResult !== 'failed', 'zh');

                    // Append git commit info to status
                    var gitSuffix = '';
                    if (gitInfo && gitInfo.shortHash) {
                        gitSuffix = '\n\nGit: ' + gitInfo.commitMsg + ' (' + gitInfo.shortHash + ')';
                    }

                    // Send EN report (Optimized: Internal call)
                    try {
                        await sendReport({
                            cycle: cycleTag,
                            title: `🧬 Evolution #${cycleTag}`,
                            status: enStatus + gitSuffix,
                            lang: 'en'
                        });
                    } catch (reportErr) {
                        console.warn('[Wrapper] EN report failed:', reportErr.message);
                    }

                    // Send CN report (Optimized: Internal call)
                    try {
                        const FEISHU_CN_REPORT_GROUP = process.env.FEISHU_CN_REPORT_GROUP || 'oc_86ff5e0d40cb49c777a24156f379c48c';
                        await sendReport({
                            cycle: cycleTag,
                            title: `🧬 进化 #${cycleTag}`,
                            status: zhStatus + gitSuffix,
                            target: FEISHU_CN_REPORT_GROUP,
                            lang: 'cn'
                        });
                    } catch (reportErr) {
                        console.warn('[Wrapper] CN report failed:', reportErr.message);
                    }

                    // Cleanup status file
                    try { fs.unlinkSync(statusFilePath); } catch (_) {}
                } catch (reportErr) {
                    console.error('[Wrapper] Post-push report failed:', reportErr.message);
                }

                // Feature 7: Issue Tracker (record problems to Feishu doc)
                try {
                    if (issueTracker && typeof issueTracker.recordIssues === 'function') {
                        var taskFileForIssues = path.resolve(path.dirname(lifecycleLog), 'task_' + cycleTag + '.txt');
                        var signals = [];
                        try {
                            var taskContentForIssues = fs.readFileSync(taskFileForIssues, 'utf8');
                            var sigMatch = taskContentForIssues.match(/Context \[Signals\]:\s*\n(\[.*?\])/);
                            if (sigMatch) signals = JSON.parse(sigMatch[1]);
                        } catch (_) {}
                        issueTracker.recordIssues(signals, cycleTag, '').catch(function(e) {
                            console.error('[IssueTracker] Error:', e.message);
                        });
                    }
                } catch (e) {
                    console.error('[IssueTracker] Error:', e.message);
                }
                
                sendSummary(cycleTag, duration, true); // Feature 2

                ok = true;
            } catch (e) {
                const duration = ((Date.now() - startTime) / 1000).toFixed(2);
                fs.appendFileSync(
                    lifecycleLog,
                    `🧬 [${new Date().toISOString()}] ERROR Wrapper PID=${process.pid} Cycle=#${cycleTag} Duration=${duration}s: ${e.message}\n`
                );
                console.error(`Wrapper proxy failed (Attempt ${attempts}) Cycle #${cycleTag}:`, e.message);
                appendFailureLesson(cycleTag, 'wrapper_cycle_failed', String(e && e.message ? e.message : e));
                
                // On failure, we might send a summary OR let the real-time errors speak for themselves.
                // Sending a FAILURE summary is good practice.
                sendSummary(cycleTag, duration, false); 

                // Ensure evolution reports explicitly reflect failure when retries are exhausted.
                if (attempts >= MAX_RETRIES) {
                    try {
                        var reason = String(e && e.message ? e.message : 'unknown failure').split('\n')[0].slice(0, 240);
                        var enFail = withOutcomeLine(
                            ensureDetailedStatus(
                                `Status: [REPAIR] Evolution failed in this cycle after retry exhaustion. Root cause: ${reason}`,
                                'en',
                                cycleTag,
                                null
                            ),
                            false,
                            'en'
                        );
                        var zhFail = withOutcomeLine(
                            ensureDetailedStatus(
                                `状态: [修复] 本轮进化在重试耗尽后失败。根因：${reason}`,
                                'zh',
                                cycleTag,
                                null
                            ),
                            false,
                            'zh'
                        );
                        try {
                            await sendReport({
                                cycle: cycleTag,
                                title: `🧬 Evolution #${cycleTag}`,
                                status: enFail,
                                lang: 'en'
                            });
                        } catch (_) {}
                        try {
                            const FEISHU_CN_REPORT_GROUP = process.env.FEISHU_CN_REPORT_GROUP || 'oc_86ff5e0d40cb49c777a24156f379c48c';
                            await sendReport({
                                cycle: cycleTag,
                                title: `🧬 进化 #${cycleTag}`,
                                status: zhFail,
                                target: FEISHU_CN_REPORT_GROUP,
                                lang: 'cn'
                            });
                        } catch (_) {}
                    } catch (reportErr) {
                        console.error('[Wrapper] Failure report dispatch failed:', reportErr.message);
                    }
                }

                if (attempts < MAX_RETRIES) {
                    const delay = Math.min(60, 5 * attempts);
                    console.log(`Retrying in ${delay} seconds...`);
                    sleepSeconds(delay);
                }
            }
        }

        if (!ok) {
            console.error('Wrapper failed after max retries.');
            if (!isLoop) process.exit(1);
            console.log(`Backoff ${loopFailBackoffSeconds}s before next cycle...`);
            sleepSeconds(loopFailBackoffSeconds);
        }

        if (!isLoop) return;

        fs.appendFileSync(
            lifecycleLog,
            `🧬 [${new Date().toISOString()}] SLEEP Wrapper PID=${process.pid} NextCycleIn=${loopSleepSeconds}s\n`
        );
        sleepSeconds(loopSleepSeconds);
    }
}

run();
