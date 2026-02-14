---
name: flowfi-openclaw
description: Interact with FlowFi API from OpenClaw agents using Bearer token authentication; create/read/update workflows, deploy, and lifecycle actions. Use when the agent must call FlowFi backend for workflows or automation.
---

# FlowFi – OpenClaw skill

Use this skill when an OpenClaw agent needs to call the FlowFi backend: create workflows, list/update/deploy them, or manage comments.

## When to use

- The user or a FlowFi node invokes an OpenClaw agent that must talk to FlowFi (workflows, deployments, comments).
- The agent needs to use FlowFi’s REST API with Bearer token authentication.

## Instructions

1. **Authentication**  
   Use the FlowFi Bearer token (from FlowFi secrets or environment). Send it in the `Authorization` header as `Bearer <token>`.

2. **Base URL**  
   Use the FlowFi backend base URL (e.g. from FlowFi config or `FLOWFI_API_URL`). Append the path from the reference (e.g. `/api/workflows`, `/api/workflows/:id/deploy`).

3. **Workflows**  
   - Create: `POST /api/workflows` with the workflow payload.
   - Read: `GET /api/workflows` or `GET /api/workflows/:id`.
   - Update: `PATCH` or `PUT` on the workflow resource as documented.

4. **Deploy / lifecycle**  
   Use the endpoints described in `reference.md` for deploy, run, or other lifecycle actions.

5. **Errors**  
   On non-2xx responses, read the response body and surface a short error message to the user or to the FlowFi node (e.g. in `error` or logs).

## Reference

See **reference.md** in this folder for endpoint details, request/response shapes, and examples. See **nodes.md** for the FlowFi OpenClaw node (inputs/outputs and config).
