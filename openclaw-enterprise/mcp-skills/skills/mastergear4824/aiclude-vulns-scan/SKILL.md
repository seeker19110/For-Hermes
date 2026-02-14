---
name: aiclude-vulns-scan
description: Scan MCP Servers and AI Agent Skills for security vulnerabilities. 7 parallel engines detect prompt injection, tool poisoning, malware, supply chain attacks, and more.
tags: [security, vulnerability, scanner, mcp, ai-agent, sast, sca, malware]
homepage: https://vs.aiclude.com
repository: https://github.com/aiclude/asvs
---

# /security-scan - AIclude Security Vulnerability Scanner

Scan MCP Servers and AI Agent Skills for security vulnerabilities. Queries existing scan results from the AIclude database, or registers a new scan and returns the results.

## Usage

```
# Search by package name (queries AIclude scan database)
/security-scan --name <package-name> [options]

# Scan a local directory (offline, no network)
/security-scan <target-path> [options]
```

## Parameters

- `--name`: Package name to search (npm package, GitHub repo, etc.)
- `target-path`: Local directory path to scan directly
- `--type`: Target type (`mcp-server` | `skill`) - auto-detected if omitted
- `--profile`: Sandbox profile (`strict` | `standard` | `permissive`)
- `--format`: Output format (`markdown` | `json`)
- `--engines`: Scan engines to use (comma-separated)

## Examples

```
# Look up scan results for an MCP server
/security-scan --name @anthropic/mcp-server-fetch

# Look up scan results for a Skill
/security-scan --name my-awesome-skill --type skill

# Scan local source code (fully offline)
/security-scan ./my-mcp-server
```

## How It Works

- **Name-based lookup** queries the AIclude scan database. If a report exists, it is returned immediately. If not, the target is registered for scanning and results are returned when ready. Only the package name is sent. No source code is uploaded.
- **Local scan** reads files from the specified directory and runs all 7 engines locally. No network requests are made.

No environment variables or credentials are required.

## What It Checks

- **Prompt Injection**: Hidden patterns targeting LLMs
- **Tool Poisoning**: Malicious instructions in tool descriptions
- **Command Injection**: Unvalidated input passed to exec/spawn
- **Supply Chain**: Known CVEs, typosquatting
- **Malware**: Backdoors, cryptominers, ransomware, data stealers
- **Permission Abuse**: Excessive filesystem/network/process permissions

## Scan Engines

7 engines run in parallel:

| Engine | Description |
|--------|-------------|
| SAST | Static code pattern matching |
| SCA | Dependency CVE lookup via OSV.dev |
| Tool Analyzer | MCP tool definition analysis |
| DAST | Parameter fuzzing |
| Permission Checker | Permission analysis |
| Behavior Monitor | Runtime behavior detection |
| Malware Detector | Signature scanning, entropy analysis |

## Output

1. **Risk Level** (CRITICAL / HIGH / MEDIUM / LOW / INFO)
2. **Vulnerability List** with code locations
3. **Risk Assessment** and impact analysis
4. **Remediation Recommendations**

## Links

- **npm**: [`@aiclude/security-skill`](https://www.npmjs.com/package/@aiclude/security-skill)
- **MCP Server**: [`@aiclude/security-mcp`](https://www.npmjs.com/package/@aiclude/security-mcp)
- **Web Dashboard**: https://vs.aiclude.com

## License

MIT - AICLUDE Inc.
Inc.
