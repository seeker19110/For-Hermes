# FlowFi API reference (for OpenClaw agents)

This document describes how an OpenClaw agent can call the FlowFi backend when using the FlowFi OpenClaw skill.

## Authentication

- Use **Bearer token** authentication.
- Header: `Authorization: Bearer <token>`
- The token is typically provided by FlowFi (secrets or environment) and passed to the agent context (e.g. via the OpenClaw node or gateway config).

## Base URL

- Use the FlowFi backend base URL (e.g. from FlowFi deployment or `FLOWFI_API_URL`).
- Example: `https://api.flowfi.example` (no trailing slash for path concatenation).

## Common endpoints (overview)

- **Workflows**
  - `GET /api/workflows` – List workflows (query params may apply).
  - `GET /api/workflows/:id` – Get one workflow.
  - `POST /api/workflows` – Create workflow (body: workflow payload).
  - `PATCH /api/workflows/:id` – Update workflow (partial).
  - `DELETE /api/workflows/:id` – Delete workflow (if supported).

- **Deploy / execution**
  - Deploy and run endpoints are typically under the same API prefix (e.g. `/api/workflows/:id/deploy`, run endpoints as documented in the backend). Use the exact paths and methods provided by your FlowFi backend version.

- **Comments** (if applicable)
  - Endpoints for comments on workflows or runs; see backend docs for path and body format.

## OpenClaw Gateway (used by the OpenClaw node)

The FlowFi **OpenClaw node** does not call FlowFi for agent execution; it calls the **OpenClaw Gateway**:

- **URL**: Configured per node (e.g. `gateway_url` or `OPENCLAW_GATEWAY_URL`), e.g. `http://127.0.0.1:18789`
- **Endpoint**: `POST /v1/responses`
- **Headers**: `Content-Type: application/json`, `x-openclaw-agent-id: <agent_id>`, optional `Authorization: Bearer <token>`
- **Body**: `{ "model": "openclaw:<agent_id>", "input": "<user input>", "instructions": "...", "user": "..." }`

The agent running behind that gateway can then use **this skill** to call back into the FlowFi API (workflows, deploy, etc.) when the user or workflow requires it.

## Errors

- On 4xx/5xx, parse the response body and expose a clear error message to the user or to the FlowFi node (e.g. `error` field or logs).
- Network or timeouts should be reported as short, actionable messages.

## See also

- **SKILL.md** – When and how to use this skill.
- **nodes.md** – OpenClaw node config and I/O.
