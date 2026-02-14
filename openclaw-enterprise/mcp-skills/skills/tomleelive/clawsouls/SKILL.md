---
name: clawsouls
description: Manage AI agent personas (Souls) for OpenClaw. Use when the user wants to install, switch, list, or restore AI personalities/personas. Triggers on requests like "install a soul", "switch persona", "change personality", "list souls", "restore my old soul", "use minimalist", "browse personas", "what souls are available", "publish a soul", or "login to clawsouls".
---

# ClawSouls — AI Persona Manager

Manage Soul packages that define an AI agent's personality, behavior, and identity.

Souls use `owner/name` namespacing (e.g., `clawsouls/brad`, `TomLeeLive/my-soul`).

## Prerequisites

Ensure `clawsouls` CLI is available:

```bash
npx clawsouls --version
```

If not installed, install globally:

```bash
npm install -g clawsouls
```

Current version: **v0.2.3**

## Commands

### Install a Soul

```bash
npx clawsouls install clawsouls/brad
npx clawsouls install clawsouls/brad --force  # overwrite existing
```

30+ souls available. Browse all at https://clawsouls.ai

**Official souls** (owner: `clawsouls`):
- **Development:** code-reviewer, coding-tutor, debug-detective, api-architect, ml-engineer, sysadmin-sage, devops-veteran, gamedev-mentor, prompt-engineer
- **Writing & Content:** tech-writer, storyteller, scifi-writer, copywriter, content-creator
- **Professional:** data-analyst, project-manager, legal-advisor, startup-founder
- **Education:** math-tutor, philosophy-prof, mentor-coach
- **Creative:** music-producer, ux-designer, chef-master
- **Lifestyle:** personal-assistant, fitness-coach, travel-guide
- **Security:** security-auditor
- **General:** brad, minimalist

### Activate a Soul

```bash
npx clawsouls use clawsouls/brad
```

- Automatically backs up current workspace files (SOUL.md, IDENTITY.md, AGENTS.md, HEARTBEAT.md, STYLE.md, examples/)
- Never overwrites USER.md, MEMORY.md, or TOOLS.md
- Requires gateway restart to take effect

### Restore Previous Soul

```bash
npx clawsouls restore
```

Reverts to the most recent backup created by `use`.

### List Installed Souls

```bash
npx clawsouls list
```

Shows installed souls in `owner/name` format.

### Create a New Soul

```bash
npx clawsouls init my-soul
```

Scaffolds a new soul directory with clawsoul.json, SOUL.md, IDENTITY.md, AGENTS.md, HEARTBEAT.md, README.md.

### Validate a Soul

```bash
npx clawsouls validate ./my-soul/
npx clawsouls check ./my-soul/   # alias
```

Validates against the spec: schema, required files, security scan. Also runs automatically before publish.

### Publish a Soul

```bash
export CLAWSOULS_TOKEN=<token>
npx clawsouls publish ./my-soul/
```

Publishes to `username/soul-name` namespace automatically. Requires authentication token. Runs validation automatically before publishing — blocks on failure.

### Login / Get Token

```bash
npx clawsouls login
```

Instructions to get API token: Sign in at https://clawsouls.ai → Dashboard → Generate API Token.

## Workflow

### Installing & Switching Personas

1. **Browse** — Check available souls at https://clawsouls.ai or suggest from the categorized list above
2. **Install** — `npx clawsouls install clawsouls/brad`
3. **Activate** — `npx clawsouls use clawsouls/brad`
4. **Restart** — Run `openclaw gateway restart` to apply the new persona
5. **Restore** — If they want to go back, `npx clawsouls restore`

### Publishing a Soul

1. **Login** — `npx clawsouls login` → get token from dashboard
2. **Set token** — `export CLAWSOULS_TOKEN=<token>`
3. **Create** — `npx clawsouls init my-soul` → edit files
4. **Publish** — `npx clawsouls publish ./my-soul/`
5. **Manage** — Dashboard at https://clawsouls.ai/dashboard (delete, view downloads)

## Important Notes

- After `use`, always remind the user to run `openclaw gateway restart`
- The `use` command creates automatic backups — data loss is unlikely
- Souls may include STYLE.md and examples/ for enhanced persona customization
- Published souls appear at `https://clawsouls.ai/souls/owner/name`
- Users can leave reviews (1-5 stars) on any soul they don't own
- For custom registry (local testing), set env: `CLAWSOULS_CDN=/path/to/souls`
