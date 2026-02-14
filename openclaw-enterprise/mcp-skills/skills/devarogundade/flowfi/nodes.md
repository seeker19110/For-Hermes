# FlowFi nodes reference

This document summarizes FlowFi builder nodes that are relevant to OpenClaw integration.

## Node summary (excerpt)

| id         | label     | inputs | outputs | description                          |
|-----------|-----------|--------|---------|--------------------------------------|
| openclaw  | OpenClaw  | 1      | 1       | Run OpenClaw agent via Gateway       |

## openclaw

Runs an OpenClaw agent via the Gateway OpenResponses API (`POST /v1/responses`). One input, one output.

### Config / inputs

- **gateway_url** (text, optional) – Gateway base URL, e.g. `http://127.0.0.1:18789`
- **agent_id** (text, optional) – OpenClaw agent id, e.g. `main`
- **token** (text, optional) – Bearer token / password; e.g. `{{secrets.openclaw_gateway_token}}`
- **instructions** (textarea, optional) – System instructions for the agent
- **user** (text, optional) – User/session routing key (e.g. wallet or execution id)
- **headers** (textarea, optional) – Extra headers as JSON, e.g. `{"x-openclaw-agent-id":"main"}`
- **input** (textarea, required) – What the agent should do (sent as `input` in the request body)
- **response_path** (text, optional) – Dot-path to extract from the JSON response (e.g. `output.0.content.0.text`)

### Output

- **response** – Extracted or raw text response from the agent
- **raw** – Raw response body when needed
- **error** – Set if the request or parsing failed

### Usage

Use this node to delegate work to an external OpenClaw agent (e.g. tool use, long instructions). The agent can in turn use the FlowFi OpenClaw skill to call back into FlowFi (workflows, deploy, etc.) when configured with the same skill and token.
