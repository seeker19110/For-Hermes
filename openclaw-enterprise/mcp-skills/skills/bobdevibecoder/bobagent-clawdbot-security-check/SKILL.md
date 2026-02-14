---
name: clawdbot-self-security-audit
description: Perform a comprehensive read-only security audit of Clawdbot's own configuration. This is a knowledge-based skill that teaches Clawdbot to identify hardening opportunities across the system. Use when user asks to "run security check", "audit clawdbot", "check security hardening", or "what vulnerabilities does my Clawdbot have". This skill uses Clawdbot's internal capabilities and file system access to inspect configuration, detect misconfigurations, and recommend remediations. It is designed to be extensible - new checks can be added by updating this skill's knowledge.
homepage: https://github.com/TheSethRose/Clawdbot-Security-Check
metadata: {"clawdbot":{"emoji":"🔒","os":["darwin","linux"],"requires":{"files":["read"],"tools":["exec","bash"]},"install":[{"id":"read-skill","kind":"skill","name":"clawdbot-self-security-audit","label":"Install security audit skill","bins":["SKILL.md"]}]}}
---

# Clawdbot Self-Security Audit Framework

This skill empowers Clawdbot to audit its own security posture using first-principles reasoning. Rather than relying on a static script, Clawdbot learns the framework and applies it dynamically to detect vulnerabilities, understand their impact, and recommend specific remediations.

## Core Philosophy

> "Security through transparency and self-awareness."

Clawdbot should know its own attack surface. This skill embeds that knowledge directly.

## Security Principles

Running an AI agent with shell access requires caution. Focus on three areas:

1. **Who can talk to the bot** - DM policies, group allowlists, channel restrictions
2. **Where the bot is allowed to act** - Network exposure, gateway binding, proxy configs
3. **What the bot can touch** - Tool access, file permissions, credential storage

Start with the smallest access possible and widen it as you gain confidence.

## Trust Hierarchy

| Level | Entity | Trust Model |
|-------|--------|-------------|
| 1 | **Owner** | Full trust - has all access |
| 2 | **AI** | Trust but verify - sandboxed, logged |
| 3 | **Allowlists** | Limited trust - only specified users |
| 4 | **Strangers** | No trust - blocked by default |

## Audit Commands

Use these commands to run security audits:

- `clawdbot security audit` - Standard audit of common issues
- `clawdbot security audit --deep` - Comprehensive audit with all checks
- `clawdbot security audit --fix` - Apply guardrail remediations

## The 12 Security Domains

When auditing Clawdbot, systematically evaluate these domains:

### 1. Gateway Exposure (CRITICAL)

**What to check:**
- Where is the gateway binding? (`gateway.bind`)
- Is authentication configured? (`gateway.auth_token` or `CLAWDBOT_GATEWAY_TOKEN` env var)
- What port is exposed? (default: 18789)
- Is WebSocket auth enabled?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -A10 '"gateway"'
env | grep CLAWDBOT_GATEWAY_TOKEN
```

**Vulnerability:** Binding to `0.0.0.0` or `lan` without auth allows network access.

**Remediation:**
```bash
clawdbot doctor --generate-gateway-token
export CLAWDBOT_GATEWAY_TOKEN="$(openssl rand -hex 32)"
```

### 2. DM Policy Configuration (HIGH)

**What to check:**
- What is `dm_policy` set to?
- If `allowlist`, who is explicitly allowed via `allowFrom`?

**How to detect:**
```bash
cat ~/.clawdbot/clawdbot.json | grep -E '"dm_policy|"allowFrom"'
```

**Vulnerability:** Setting to `allow` or `open` means any user can DM Clawdbot.

**Remediation:**
```json
{
  "channels": {
    "telegram": {
      "dmPolicy": "allowlist",
      "allowFrom": ["@trusteduser1", "@trusteduser2"]
    }
  }
}
```

### 3. Group Access Control (HIGH)

**What to check:**
- What is `groupPolicy` set to?
- Are groups explicitly allowlisted?
- Are mention gates configured?

**Vulnerability:** Open group policy allows anyone in the room to trigger commands.

### 4. Credentials Security (CRITICAL)

**Credential Storage Map:**
| Platform | Path |
|----------|------|
| WhatsApp | `~/.clawdbot/credentials/whatsapp/{accountId}/creds.json` |
| Telegram | `~/.clawdbot/clawdbot.json` or env |
| Discord | `~/.clawdbot/clawdbot.json` or env |
| Slack | `~/.clawdbot/clawdbot.json` or env |
| Pairing allowlists | `~/.clawdbot/credentials/channel-allowFrom.json` |
| Auth profiles | `~/.clawdbot/agents/{agentId}/auth-profiles.json` |
| Legacy OAuth | `~/.clawdbot/credentials/oauth.json` |

**Remediation:**
```bash
chmod 700 ~/.clawdbot
chmod 600 ~/.clawdbot/credentials/oauth.json
chmod 600 ~/.clawdbot/clawdbot.json
```

### 5. Browser Control Exposure (HIGH)

**What to check:**
- Is browser control enabled?
- Are authentication tokens set for remote control?
- Is HTTPS required for Control UI?
- Is a dedicated browser profile configured?

**Vulnerability:** Exposed browser control without auth allows remote UI takeover.

### 6. Gateway Bind & Network Exposure (HIGH)

**Vulnerability:** Public binding without auth allows internet access to gateway.

**Remediation:**
```json
{
  "gateway": {
    "bind": "127.0.0.1",
    "mode": "local",
    "trustedProxies": ["127.0.0.1", "10.0.0.0/8"]
  }
}
```

### 7. Tool Access & Sandboxing (MEDIUM)

**Workspace Access Levels:**
| Mode | Description |
|------|-------------|
| `none` | Workspace is off limits |
| `ro` | Workspace mounted read-only |
| `rw` | Workspace mounted read-write |

**Vulnerability:** Broad tool access means more blast radius if compromised.

### 8. File Permissions & Local Disk Hygiene (MEDIUM)

**What to check:**
- Directory permissions (should be 700)
- Config file permissions (should be 600)

**Remediation:**
```bash
chmod 700 ~/.clawdbot
chmod 600 ~/.clawdbot/clawdbot.json
chmod 600 ~/.clawdbot/credentials/*
```

### 9. Plugin Trust & Model Hygiene (MEDIUM)

**Vulnerability:** Untrusted plugins can execute code. Legacy models may lack modern safety.

### 10. Logging & Redaction (MEDIUM)

**Remediation:**
```json
{
  "logging": {
    "redactSensitive": "tools",
    "path": "~/.clawdbot/logs/"
  }
}
```

### 11. Prompt Injection Protection (MEDIUM)

**Prompt Injection Mitigation Strategies:**
- Keep DMs locked to `pairing` or `allowlists`
- Use mention gating in groups
- Treat all links and attachments as hostile
- Run sensitive tools in a sandbox

### 12. Dangerous Command Blocking (MEDIUM)

**Remediation:**
```json
{
  "blocked_commands": [
    "rm -rf",
    "curl |",
    "git push --force",
    "mkfs",
    ":(){:|:&}"
  ]
}
```

## High-Level Audit Checklist

Treat findings in this priority order:

1. **CRITICAL: Lock down DMs and groups** if tools are enabled on open settings
2. **CRITICAL: Fix public network exposure** immediately
3. **HIGH: Secure browser control** with tokens and HTTPS
4. **HIGH: Correct file permissions** for credentials and config
5. **MEDIUM: Only load trusted plugins**
6. **MEDIUM: Use modern models** for bots with tool access

## Incident Response

If a compromise is suspected:

### Containment
1. **Stop the gateway process** - `clawdbot daemon stop`
2. **Set gateway.bind to loopback** - `"bind": "127.0.0.1"`
3. **Disable risky DMs and groups** - Set to `disabled`

### Rotation
1. **Change the gateway auth token** - `clawdbot doctor --generate-gateway-token`
2. **Rotate browser control and hook tokens**
3. **Revoke and rotate API keys** for model providers

### Review
1. **Check gateway logs and session transcripts** - `~/.clawdbot/logs/`
2. **Review recent config changes**
3. **Re-run the security audit with the deep flag** - `clawdbot security audit --deep`

## Report Template

```
CLAWDBOT SECURITY AUDIT
Timestamp: $(date -Iseconds)

SUMMARY
- Critical:  $CRITICAL_COUNT
- High:      $HIGH_COUNT
- Medium:    $MEDIUM_COUNT
- Passed:    $PASSED_COUNT

FINDINGS
[CRITICAL] $VULN_NAME
   Finding: $DESCRIPTION
   Fix: $REMEDIATION

[HIGH] $VULN_NAME
   ...

This audit was performed by Clawdbot's self-security framework.
No changes were made to your configuration.
```

## Principles Applied

- **Zero modification** - This skill only reads; never changes configuration
- **Defense in depth** - Multiple checks catch different attack vectors
- **Actionable output** - Every finding includes a concrete remediation
- **Extensible design** - New checks integrate naturally

**Remember:** This skill exists to make Clawdbot self-aware of its security posture. Use it regularly, extend it as needed, and never skip the audit.
