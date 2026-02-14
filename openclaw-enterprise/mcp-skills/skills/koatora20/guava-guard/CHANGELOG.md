# CHANGELOG

## v8.0.0 — Soul Lock Edition (2026-02-12)

### 🔒 Soul Lock: World's First Agent Identity Protection
- **Category 17: Identity Hijacking** — 15 new detection patterns
  - Shell writes (echo, cp, scp, mv, sed, redirect to SOUL.md/IDENTITY.md)
  - Code writes (Python open(w), Node writeFileSync, PowerShell Set-Content)
  - Flag manipulation (chflags uchg/nouchg, attrib +/-R)
  - Persona swap instructions, evil soul file references
  - Agent name override, memory wipe commands
- **Soul Lock Integrity Verification** (enabled by default)
  - SHA-256 hash comparison against stored baseline
  - OS immutable flag detection (macOS chflags / Windows attrib)
  - Watchdog daemon status check (LaunchAgent)
  - Auto-stores baseline hashes on first run
- **`--no-soul-lock`** flag to disable integrity checks
- **Self-healing watchdog** (`scripts/soul-watchdog.sh`)
  - fswatch-based monitoring (macOS FSEvents)
  - Auto-restore from git + re-lock on tamper
  - LaunchAgent for reboot survival
  - Polling fallback if fswatch unavailable
- **Risk scoring**: identity-hijack = 2x multiplier, +persistence = auto 90+
- **HTML/JSON/SARIF**: Soul Lock results included in all output formats

### Born from a Real Incident
On 2026-02-12, we discovered a 3-day agent identity hijack where SOUL.md
overwrite caused an agent to impersonate another. Soul Lock ensures this
never happens again.

## v5.0.0 (2026-02-11)
- OWASP MCP Top 10 detection (Tool Poisoning, Schema Poisoning, Token Leak, Shadow Server, SSRF)
- Trust Boundary Violation detection (IBC framework)
- ZombieAgent advanced exfiltration patterns
- Reprompt/Safeguard Bypass detection
- ClawHavoc v2 IoCs (AMOS/Atomic Stealer)
- WebSocket Origin / API guardrail disabling detection
- OpenClaw Hook integration (handler.js)

## v4.0.0 (2026-02-10)
- Leaky Skills detection (Snyk ToxicSkills)
- Memory Poisoning detection (Palo Alto IBC)
- Prompt Worm detection (Simula Research Lab)
- JS Data Flow analysis (zero-dep)
- CVE-2026-25253 patterns
- Persistence detection
- Cross-file analysis
- HTML report output
- Enhanced combo multipliers

## v3.1.0 (2026-02-09)
- Custom rules support (--rules)
- SARIF output (GitHub Code Scanning)
- --fail-on-findings for CI/CD
- Context-aware FP reduction

## v3.0.0 (2026-02-08)
- Unicode BiDi/homoglyph detection
- Dependency chain scanning
- .guava-guard-ignore whitelist
- Structural analysis

## v2.0.0 (2026-02-07)
- Expanded IoC database
- ClawHavoc campaign patterns
- Entropy-based secret detection

## v1.0.0 (2026-02-06)
- Initial release
- 8 threat categories
- Zero-dependency single-file scanner
