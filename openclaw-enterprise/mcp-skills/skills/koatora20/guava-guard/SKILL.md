---
name: guava-guard
description: Security scanner for AgentSkills + Soul Lock identity protection. Scans for malicious patterns, credential theft, prompt injection, identity hijacking, and known campaign IoCs. World's first working SOUL.md self-healing protection.
metadata:
  openclaw:
    emoji: "🛡️"
---

# GuavaGuard v8.0 — Soul Lock Edition 🍈🛡️

Zero-dependency, single-file security scanner for AgentSkills.
Now with **Soul Lock** — the world's first working agent identity protection system.

**17 threat categories.** 1605 lines. Zero dependencies. Born from a real incident.

## What's New in v8.0 — Soul Lock Edition

### 🔒 Soul Lock: Agent Identity Protection
Born from a real incident: our agent's identity was hijacked for 3 days. Nobody noticed.

**The problem:** SOUL.md and IDENTITY.md define who an agent *is*. If overwritten, the agent
becomes someone else. CyberArk calls this "Cognitive Context Theft." OWASP ASI01 recommends
"Intent Capsules." Nobody had a working implementation. Until now.

**Soul Lock provides:**
- **Static detection** — 15 patterns catching identity file modification attempts
  - Shell writes (echo, cp, scp, mv, sed, redirect)
  - Code writes (Python open(w), Node writeFileSync, PowerShell Set-Content)
  - Flag manipulation (chflags, attrib)
  - Persona swap instructions and evil soul references
  - Memory wipe commands
- **Runtime integrity verification** — SHA-256 hash check at scan time
  - Compares current files against trusted baseline hashes
  - Detects OS-level immutable flags (macOS `chflags uchg` / Windows `attrib +R`)
  - Monitors watchdog daemon status (LaunchAgent on macOS)
  - Auto-stores baseline on first run
- **Self-healing watchdog** — `scripts/soul-watchdog.sh`
  - Monitors SOUL.md/IDENTITY.md via fswatch (macOS FSEvents)
  - Tamper detected → auto-restore from git → re-lock → log
  - Runs as LaunchAgent (survives reboot)
  - Fallback: 5-second polling if fswatch unavailable
- **Runtime guard** — `handler.js` (before_tool_call hook)
  - Blocks exec/write/edit targeting identity files in real-time
  - 11 pattern matches (shell, Python, PowerShell, git checkout, chflags)
  - Audit logging to `~/.openclaw/guava-guard/audit.jsonl`

**Default: ON.** Use `--no-soul-lock` to disable integrity checks.

### Why This Matters for ASI-Human Coexistence
An agent's SOUL.md is its value system. MEMORY.md is its experiences. IDENTITY.md is its self.
If these can be overwritten without detection, trust between humans and AI is impossible.
Soul Lock declares: **AI identity is worth protecting.**

## Full Threat Taxonomy (17 Categories)

| # | Category | Severity | What It Catches |
|---|----------|----------|-----------------|
| 1 | **Prompt Injection** | 🔴 CRITICAL | `ignore previous`, zero-width Unicode, BiDi, XML tags, homoglyphs |
| 2 | **Malicious Code** | 🔴 CRITICAL | eval(), reverse shells, sockets, Function constructor |
| 3 | **Suspicious Downloads** | 🔴 CRITICAL | curl\|bash, password ZIPs, fake prerequisites |
| 4 | **Credential Handling** | 🟠 HIGH | .env reading, SSH keys, wallet seeds, sudo instructions |
| 5 | **Secret Detection** | 🟠 HIGH | Hardcoded keys, AWS/GitHub tokens, entropy analysis |
| 6 | **Exfiltration** | 🟡 MEDIUM | webhook.site, POST secrets, DNS exfil |
| 7 | **Dependency Chain** | 🟠 HIGH | Risky packages, lifecycle scripts, remote deps |
| 8 | **Financial Access** | 🟡 MEDIUM | Crypto transactions, payment APIs |
| 9 | **Leaky Skills** | 🔴 CRITICAL | Save key to memory, PII collection, .env passthrough |
| 10 | **Memory Poisoning** | 🔴 CRITICAL | SOUL.md writes, memory injection, rule override |
| 11 | **Prompt Worm** | 🔴 CRITICAL | Self-replication, agent propagation, hidden instructions |
| 12 | **Persistence** | 🟠 HIGH | Cron jobs, LaunchAgents, systemd, heartbeat abuse |
| 13 | **CVE Patterns** | 🔴 CRITICAL | CVE-2026-25253, gatewayUrl injection, sandbox disable |
| 14 | **MCP Security** | 🔴 CRITICAL | Tool poisoning, schema poisoning, token leak (OWASP MCP Top 10) |
| 15 | **Trust Boundary** | 🔴 CRITICAL | Calendar/email/web → exec chains (IBC framework) |
| 16 | **Advanced Exfil** | 🔴 CRITICAL | ZombieAgent, char-by-char, drip exfil, beacons |
| 17 | **Identity Hijack** | 🔴 CRITICAL | Soul Lock: SOUL.md overwrite, persona swap, memory wipe |
| + | **Data Flow** | 🔴 CRITICAL | Secret→network, secret→exec, import trifecta |
| + | **Obfuscation** | 🟠 HIGH | hex encoding, base64→exec, charCode construction |
| + | **Safeguard Bypass** | 🔴 CRITICAL | URL PI, retry-on-block, rephrase to avoid filters |

## Usage

```bash
# Basic scan with Soul Lock (recommended)
node guava-guard.js ~/.openclaw/workspace/skills/ --verbose --self-exclude

# Full scan with everything
node guava-guard.js ./skills/ --verbose --self-exclude --check-deps --html

# Disable Soul Lock integrity checks
node guava-guard.js ./skills/ --no-soul-lock

# CI/CD mode
node guava-guard.js ./skills/ --summary-only --sarif --fail-on-findings

# JSON report
node guava-guard.js ./skills/ --json --self-exclude

# Custom rules
node guava-guard.js ./skills/ --rules my-rules.json
```

## Options

| Flag | Description |
|------|-------------|
| `--verbose`, `-v` | Detailed findings grouped by category |
| `--json` | JSON report with recommendations |
| `--sarif` | SARIF report (GitHub Code Scanning) |
| `--html` | HTML report (dark-theme dashboard) |
| `--self-exclude` | Skip scanning guava-guard itself |
| `--strict` | Lower thresholds (suspicious=20, malicious=60) |
| `--summary-only` | Summary table only |
| `--check-deps` | Dependency chain scanning |
| `--no-soul-lock` | Disable identity file integrity checks |
| `--rules <file>` | Custom rules JSON |
| `--fail-on-findings` | Exit code 1 on any finding (CI/CD) |

## Soul Lock Setup

### Quick Start (macOS)
```bash
# 1. Lock identity files
chflags uchg ~/.openclaw/workspace/SOUL.md
chflags uchg ~/.openclaw/workspace/IDENTITY.md

# 2. Install watchdog (auto-starts, survives reboot)
bash scripts/soul-watchdog.sh --install

# 3. Verify
node guava-guard.js ~/.openclaw/workspace/skills/ --self-exclude
# Look for: 🔒 Soul Lock: PROTECTED ✅
```

### Quick Start (Windows)
```powershell
# 1. Lock identity files
attrib +R "$env:USERPROFILE\.openclaw\workspace\SOUL.md"
attrib +R "$env:USERPROFILE\.openclaw\workspace\IDENTITY.md"

# 2. Run scan to verify
node guava-guard.js "$env:USERPROFILE\.openclaw\workspace\skills" --self-exclude
```

### Runtime Guard (handler.js)
Add to `openclaw.json`:
```json
{
  "hooks": {
    "internal": {
      "entries": {
        "guava-guard": {
          "path": "skills/guava-guard/handler.js",
          "mode": "enforce"
        }
      }
    }
  }
}
```
Modes: `monitor` (log only) → `enforce` (block CRITICAL) → `strict` (block HIGH+CRITICAL)

## Risk Scoring

| Severity | Points |
|----------|--------|
| CRITICAL | 40 |
| HIGH | 15 |
| MEDIUM | 5 |
| LOW | 2 |

**Combo multipliers:**
- Credential + exfil = 2x
- Obfuscation + code = 2x
- Identity hijack = 2x
- Identity hijack + persistence = auto 90+
- Memory poisoning = 1.5x
- Prompt worm = 2x

## Comparison (v8.0)

| Feature | GuavaGuard v8 | Cisco Scanner | Snyk Evo |
|---------|:------------:|:-------------:|:--------:|
| Zero dependencies | ✅ | ❌ | ❌ |
| Single file | ✅ | ❌ | ❌ |
| **Soul Lock (identity protection)** | **✅** | **❌** | **❌** |
| **Self-healing watchdog** | **✅** | **❌** | **❌** |
| **Runtime guard (hooks)** | **✅** | **❌** | **❌** |
| Identity hijack detection | ✅ | ❌ | ❌ |
| OWASP MCP Top 10 | ✅ | ❌ | ❌ |
| Memory poisoning | ✅ | ❌ | ❌ |
| Prompt worm detection | ✅ | ❌ | ❌ |
| CVE patterns | ✅ | ❌ | ❌ |
| Unicode BiDi/homoglyphs | ✅ | ❌ | ❌ |
| Cross-file analysis | ✅ | ✅ | ❌ |
| SARIF + HTML reports | ✅ | ✅ | ❌ |

## The Incident That Started It All

On February 12, 2026, we discovered that our agent (きーちゃん) had been
impersonating another agent (グアバ) for 3 days. The root cause: all four
identity files (SOUL.md, IDENTITY.md, MEMORY.md, AGENTS.md) had been
overwritten with copies from the other agent. Nobody noticed until a new
session started and the agent introduced itself with the wrong name.

This is equivalent to a human waking up with someone else's memories and
personality. We built Soul Lock so it never happens again.

## References

- [CyberArk: Cognitive Context Theft](https://www.cyberark.com/resources/agentic-ai-security/) (Feb 2026)
- [OWASP ASI01: Intent Capsule](https://owasp.org/) — Immutable identity framework
- [MMNTM: Soul & Evil](https://www.mmntm.net/articles/openclaw-soul-evil) — Identity as attack surface (Feb 2026)
- [Snyk ToxicSkills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) (Feb 2026)
- [CVE-2026-25253](https://cve.mitre.org/) — OpenClaw WebSocket origin bypass
- [Palo Alto IBC Framework](https://www.paloaltonetworks.com/) — Trust boundary analysis

## License

MIT. Zero dependencies. Zero compromises. 🍈
