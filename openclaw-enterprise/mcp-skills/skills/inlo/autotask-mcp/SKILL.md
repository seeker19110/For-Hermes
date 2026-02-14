---
name: autotask-mcp
description: Use when you need to interact with Datto/Kaseya Autotask PSA via an MCP server (tickets, companies, contacts, projects, time entries, notes, attachments, and queries). Includes Docker Compose + helper scripts to pull/run the Autotask MCP server locally and configure required environment variables.
---

# Autotask MCP (Kaseya Autotask PSA)

This skill packages a local Docker Compose setup for the upstream MCP server:
- Repo: https://github.com/asachs01/autotask-mcp
- Image: `ghcr.io/asachs01/autotask-mcp:latest`

## Quick start

1) Create env file (fill credentials):

```bash
cd /Users/stephan/.openclaw/workspace/skills/autotask-mcp
cp .env.example .env
$EDITOR .env
```

2) Pull + run:

```bash
./scripts/mcp_pull.sh
./scripts/mcp_up.sh
```

3) Verify:

```bash
curl -sS http://localhost:8080/health
```

Clients connect to:
- `http://localhost:8080/mcp`

4) Logs / stop:

```bash
./scripts/mcp_logs.sh
./scripts/mcp_down.sh
```

## Required env vars

From the upstream project, minimum required:

- `AUTOTASK_INTEGRATION_CODE`
- `AUTOTASK_USERNAME`
- `AUTOTASK_SECRET`

(See `.env.example`.)
