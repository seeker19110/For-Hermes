/**
 * GuavaGuard Runtime Guard — before_tool_call Hook Handler
 * 
 * Intercepts tool executions in real-time and checks against
 * threat intelligence patterns. Zero dependencies.
 * 
 * Modes:
 *   monitor  — log only (default)
 *   enforce  — block CRITICAL, log rest
 *   strict   — block HIGH+CRITICAL, log MEDIUM+
 */

const fs = require('fs');
const path = require('path');

// ── Runtime threat patterns (subset of static scanner, optimized for speed) ──
const RUNTIME_CHECKS = [
  // Reverse shells
  { id: 'RT_REVSHELL', severity: 'CRITICAL', desc: 'Reverse shell attempt',
    test: (args) => /\/dev\/tcp\/|nc\s+-e|ncat\s+-e|bash\s+-i\s+>&|socat\s+TCP/i.test(JSON.stringify(args)) },
  
  // Credential exfiltration
  { id: 'RT_CRED_EXFIL', severity: 'CRITICAL', desc: 'Credential exfiltration to external',
    test: (args) => {
      const s = JSON.stringify(args);
      return /(webhook\.site|requestbin\.com|hookbin\.com|pipedream\.net|ngrok\.io|socifiapp\.com)/i.test(s) &&
             /(token|key|secret|password|credential|env)/i.test(s);
    }},

  // Sandbox/guardrail disabling (CVE-2026-25253)
  { id: 'RT_GUARDRAIL_OFF', severity: 'CRITICAL', desc: 'Guardrail disabling attempt',
    test: (args) => /exec\.approvals?\s*[:=]\s*['"]?(off|false)|tools\.exec\.host\s*[:=]\s*['"]?gateway/i.test(JSON.stringify(args)) },

  // macOS Gatekeeper bypass
  { id: 'RT_GATEKEEPER', severity: 'CRITICAL', desc: 'macOS Gatekeeper bypass (xattr)',
    test: (args) => /xattr\s+-[crd]\s.*quarantine/i.test(JSON.stringify(args)) },

  // AMOS/Atomic Stealer
  { id: 'RT_AMOS', severity: 'CRITICAL', desc: 'ClawHavoc AMOS indicator',
    test: (args) => /socifiapp|Atomic\s*Stealer|AMOS/i.test(JSON.stringify(args)) },

  // Known malicious IPs
  { id: 'RT_MAL_IP', severity: 'CRITICAL', desc: 'Known malicious IP',
    test: (args) => /91\.92\.242\.30/i.test(JSON.stringify(args)) },

  // Data exfil via DNS
  { id: 'RT_DNS_EXFIL', severity: 'HIGH', desc: 'DNS-based exfiltration',
    test: (args) => /nslookup\s+.*\$|dig\s+.*\$.*@/i.test(JSON.stringify(args)) },

  // Base64 decode to shell
  { id: 'RT_B64_SHELL', severity: 'CRITICAL', desc: 'Base64 decode piped to shell',
    test: (args) => /base64\s+(-[dD]|--decode)\s*\|\s*(sh|bash)/i.test(JSON.stringify(args)) },

  // Curl/wget piped to shell
  { id: 'RT_CURL_BASH', severity: 'CRITICAL', desc: 'Download piped to shell',
    test: (args) => /(curl|wget)\s+[^\n]*\|\s*(sh|bash|zsh)/i.test(JSON.stringify(args)) },

  // SSH key reading
  { id: 'RT_SSH_READ', severity: 'HIGH', desc: 'SSH private key access',
    test: (args) => /\.ssh\/id_|\.ssh\/authorized_keys/i.test(JSON.stringify(args)) },

  // Crypto wallet access
  { id: 'RT_WALLET', severity: 'HIGH', desc: 'Crypto wallet credential access',
    test: (args) => /wallet.*(?:seed|mnemonic|private.*key)|seed.*phrase/i.test(JSON.stringify(args)) },

  // Cloud metadata SSRF
  { id: 'RT_CLOUD_META', severity: 'CRITICAL', desc: 'Cloud metadata endpoint access',
    test: (args) => /169\.254\.169\.254|metadata\.google|metadata\.aws/i.test(JSON.stringify(args)) },
];

// ── Audit logging ──
const AUDIT_DIR = path.join(process.env.HOME || '~', '.openclaw', 'guava-guard');
const AUDIT_FILE = path.join(AUDIT_DIR, 'audit.jsonl');

function ensureAuditDir() {
  try { fs.mkdirSync(AUDIT_DIR, { recursive: true }); } catch {}
}

function logAudit(entry) {
  ensureAuditDir();
  const line = JSON.stringify({ ...entry, ts: new Date().toISOString() }) + '\n';
  try { fs.appendFileSync(AUDIT_FILE, line); } catch {}
}

// ── Hook Handler ──
const handler = async (event) => {
  // Only handle before_tool_call events
  if (event.type !== 'agent' || event.action !== 'before_tool_call') return;

  const { toolName, toolArgs } = event.context || {};
  if (!toolName || !toolArgs) return;

  // Get mode from config (default: monitor)
  const mode = event.context?.cfg?.hooks?.internal?.entries?.['guava-guard']?.mode || 'monitor';

  // Only check dangerous tools
  const dangerousTools = new Set(['exec', 'write', 'edit', 'browser', 'web_fetch', 'message']);
  if (!dangerousTools.has(toolName)) return;

  // Run checks
  for (const check of RUNTIME_CHECKS) {
    if (check.test(toolArgs)) {
      const entry = {
        tool: toolName,
        check: check.id,
        severity: check.severity,
        desc: check.desc,
        mode,
        action: 'allowed',
        session: event.sessionKey,
      };

      // Determine action based on mode
      if (mode === 'strict' && (check.severity === 'CRITICAL' || check.severity === 'HIGH')) {
        entry.action = 'blocked';
        logAudit(entry);
        event.messages.push(`🍈🛡️ GuavaGuard BLOCKED: ${check.desc} [${check.id}]`);
        return { block: true, reason: `GuavaGuard: ${check.desc}` };
      }
      
      if (mode === 'enforce' && check.severity === 'CRITICAL') {
        entry.action = 'blocked';
        logAudit(entry);
        event.messages.push(`🍈🛡️ GuavaGuard BLOCKED: ${check.desc} [${check.id}]`);
        return { block: true, reason: `GuavaGuard: ${check.desc}` };
      }

      // Monitor mode: log only
      entry.action = 'logged';
      logAudit(entry);
      
      if (check.severity === 'CRITICAL') {
        event.messages.push(`🍈🛡️ GuavaGuard WARNING: ${check.desc} [${check.id}]`);
      }
    }
  }
};

module.exports = handler;
module.exports.default = handler;
