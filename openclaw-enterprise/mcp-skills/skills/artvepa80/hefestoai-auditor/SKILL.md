---
name: hefestoai-auditor
version: "1.2.0"
description: "AI-powered code analysis with HefestoAI. Run security audits, detect code smells, analyze complexity, and get ML-enhanced suggestions across 17 languages. Use when a user asks to analyze code, run a security audit, check code quality, or find vulnerabilities."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔨",
        "requires": { "bins": ["hefesto"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "package": "hefesto-ai",
              "bins": ["hefesto"],
              "label": "Install HefestoAI (pip)"
            }
          ]
      }
  }
---

# HefestoAI Auditor Skill

AI-powered code quality guardian. Analyzes code for security vulnerabilities, complexity issues, code smells, and best practice violations across 17 languages.

## Quick Start

### Run a full audit

```bash
# IMPORTANTE: Cargar environment primero para activar licencia
source /home/user/.hefesto_env 2>/dev/null
hefesto analyze /ruta/absoluta/al/proyecto --severity HIGH --exclude venv,node_modules,.git
```

### Severity levels

```bash
hefesto analyze /path/to/project --severity CRITICAL   # Solo criticos
hefesto analyze /path/to/project --severity HIGH        # High y Critical
hefesto analyze /path/to/project --severity MEDIUM      # Medium, High, Critical
hefesto analyze /path/to/project --severity LOW         # Todo
```

### Output formats

```bash
hefesto analyze /path/to/project --output text          # Default, terminal
hefesto analyze /path/to/project --output json          # JSON estructurado
hefesto analyze /path/to/project --output html --save-html report.html  # Reporte HTML
hefesto analyze /path/to/project --quiet                # Solo resumen
```

### Check status and version

```bash
hefesto status
hefesto --version
```


## Recommended: Wrapper Script

For reliable results, create a wrapper script that always loads your license:

```bash
#!/bin/bash
# Save as /usr/local/bin/hefesto (replaces direct binary)
source /path/to/.hefesto_env 2>/dev/null
exec /path/to/venv/bin/hefesto "$@"
```

This ensures your license tier is always active, regardless of how hefesto is called.

### Pre-built audit scripts

```bash
# Save as ~/hefesto_tools/run_audit.sh
#!/bin/bash
SEVERITY="${1:-HIGH}"
TARGET="${2:-/path/to/your/project}"
source /path/to/.hefesto_env 2>/dev/null
exec hefesto analyze "$TARGET" --severity "$SEVERITY" --exclude venv,node_modules,.git
```

Usage:
```bash
bash ~/hefesto_tools/run_audit.sh              # HIGH severity, default project
bash ~/hefesto_tools/run_audit.sh CRITICAL     # CRITICAL only
bash ~/hefesto_tools/run_audit.sh MEDIUM /other/project  # Custom
```

## Important Notes

- **SIEMPRE** usa rutas absolutas, nunca `." ni rutas relativas
- **SIEMPRE** carga el environment (`source /home/user/.hefesto_env`) antes de ejecutar para activar tu licencia
- **SIEMPRE** excluye `venv,node_modules,.git` para evitar falsos positivos de dependencias
- **Reporta SOLO** lo que hefesto devuelve en su output. No inventes ni agregues issues adicionales.

## Supported Languages (17)

**Code:** Python, TypeScript, JavaScript, Java, Go, Rust, C#
**DevOps/Config:** Dockerfile, Jenkins/Groovy, JSON, Makefile, PowerShell, Shell, SQL, Terraform, TOML, YAML

## What It Detects

### Security Issues
- SQL injection vulnerabilities
- Hardcoded secrets and API keys
- Command injection risks
- Insecure configurations

### Code Quality
- Cyclomatic complexity (functions too complex)
- Deep nesting (>4 levels)
- Long functions (>50 lines)
- Code smells and anti-patterns

### DevOps Issues
- Dockerfile: missing USER, no HEALTHCHECK, running as root
- Shell: missing `set -euo pipefail`, unquoted variables
- Terraform: missing tags, hardcoded values

## Interpreting Results

HefestoAI outputs results in this format:

```
📄 <file>:<line>:<col>
├─ Issue: <description>
├─ Function: <name>
├─ Type: <issue_type>
├─ Severity: CRITICAL | HIGH | MEDIUM | LOW
└─ Suggestion: <fix recommendation>
```

### Severity Guide
- **CRITICAL**: Cyclomatic complexity >20. Fix immediately.
- **HIGH**: Complexity 10-20, deep nesting, SQL injection risks. Fix in current sprint.
- **MEDIUM**: Style issues, minor improvements. Fix when convenient.
- **LOW**: Informational, best practice suggestions.

### Issue Types
- `VERY_HIGH_COMPLEXITY`: Cyclomatic complexity >20
- `HIGH_COMPLEXITY`: Cyclomatic complexity 10-20
- `DEEP_NESTING`: Nesting level exceeds threshold (default: 4)
- `SQL_INJECTION_RISK`: Potential SQL injection via string concatenation
- `LONG_FUNCTION`: Function exceeds line threshold

## Pro Tips

### Exclude directories
Always exclude dependencies to avoid false positives:
```bash
hefesto analyze /path/to/project --severity HIGH --exclude venv,node_modules,.git
```

### CI/CD gate
Fail the build if issues are found:
```bash
hefesto analyze /path/to/project --fail-on HIGH --exclude venv
```

### Install pre-push hook
```bash
hefesto install-hook
```

### Limit output
```bash
hefesto analyze /path/to/project --max-issues 10
```

### Exclude specific issue types
```bash
hefesto analyze /path/to/project --exclude-types VERY_HIGH_COMPLEXITY,LONG_FUNCTION
```

## Licensing Tiers

| Tier | Price | Key Features |
|------|-------|-------------|
| **FREE** | USD0/mo | Static analysis, 17 languages, pre-push hooks |
| **PRO** | USD8/mo (launch) | ML semantic analysis, REST API, BigQuery, custom rules |
| **OMEGA** | USD19/mo (launch) | IRIS monitoring, auto-correlation, real-time alerts, team dashboard |

All paid tiers include a **14-day free trial**.

### Upgrade Links
- **PRO**: https://buy.stripe.com/4gM00i6jE6gV3zE4HseAg0b
- **OMEGA**: https://buy.stripe.com/14A9AS23o20Fgmqb5QeAg0c

### Activate License
```bash
export HEFESTO_LICENSE_KEY=<your-key>
hefesto status  # verify tier
```

## About

Created by **Narapa LLC** (Miami, FL) — Arturo Velasquez (@artvepa)
GitHub: https://github.com/artvepa80/Agents-Hefesto
Support: support@narapallc.com

> "El codigo limpio es codigo seguro"
