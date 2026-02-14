---
name: cursor-cloud-agents
description: "Deploy Cursor AI agents to GitHub repos. Automatically write code, generate tests, create documentation, and open PRs using your existing Cursor subscription."
---

# Cursor Cloud Agents Skill

## Overview

This skill wraps the Cursor Cloud Agents HTTP API, allowing OpenClaw to dispatch coding tasks to Cursor's cloud agents, monitor their progress, and incorporate results.

### When to Use

Use this skill when you need to:

- Delegate coding tasks to Cursor agents running on GitHub repositories
- Generate code, tests, or documentation on existing codebases
- Perform refactoring or feature implementation asynchronously
- Get a "second opinion" on code changes

### When NOT to Use

- For simple questions that don't require code changes
- When you need real-time streaming responses (use local Cursor CLI instead)
- For tasks outside of GitHub repositories

## Authentication

The skill automatically discovers your Cursor API key from these locations (in order):

1. **Environment variable:** `CURSOR_API_KEY`
2. **OpenClaw env file:** `~/.openclaw/.env`
3. **OpenClaw local env:** `~/.openclaw/.env.local`
4. **Project env:** `.env` in current directory
5. **Cursor config:** `~/.cursor/config.json`

**Recommended:** Add to `~/.openclaw/.env`:
```bash
CURSOR_API_KEY=your_cursor_api_key_here
```

To get your API key:
1. Open Cursor IDE
2. Go to Settings → General
3. Copy your API key

**Verify it's working:**
```bash
cursor-api.sh me
```

## Workflow Patterns

### Pattern A: Fire-and-Forget

Launch an agent and let it work independently. Check back later.

```bash
# Launch agent (uses default model: gpt-5.2)
cursor-api.sh launch --repo owner/repo --prompt "Add comprehensive tests for auth module"

# Launch with specific model
cursor-api.sh launch --repo owner/repo --prompt "Add tests" --model claude-4-opus

# Response: {"id": "agent_123", "status": "CREATING", ...}

# Later - check status
cursor-api.sh status agent_123
```

**Note:** If no `--model` is specified, the default model (`gpt-5.2`) will be used automatically. You'll see a message indicating which model is being used.

**Best for:** Tasks that don't need immediate attention, exploratory work

### Pattern B: Supervised Dispatch

Launch, monitor, and report results when complete.

```bash
# 1. Launch
cursor-api.sh launch --repo owner/repo --prompt "Implement user authentication"

# 2. Poll for completion (check every 60 seconds)
while true; do
    status=$(cursor-api.sh status agent_123)
    if [[ $(echo "$status" | jq -r '.status') == "FINISHED" ]]; then
        break
    fi
    sleep 60
done

# 3. Get results
cursor-api.sh conversation agent_123 | jq -r '.messages[] | select(.role == "assistant") | .content'
```

**Best for:** Important tasks where you want to report completion

### Pattern C: Iterative Collaboration

Launch, review, and send follow-ups to refine work.

```bash
# 1. Launch initial task
cursor-api.sh launch --repo owner/repo --prompt "Add login page"

# 2. Review conversation
cursor-api.sh conversation agent_123

# 3. Send follow-up
cursor-api.sh followup agent_123 --prompt "Also add form validation and error handling"

# 4. Final review when done
cursor-api.sh conversation agent_123
```

**Best for:** Complex tasks requiring multiple iterations

## Commands Reference

### List Agents

```bash
cursor-api.sh list
```

Returns all agents with status, repo, and creation time.

### Launch Agent

```bash
cursor-api.sh launch --repo owner/repo --prompt "Your task description" [--model model-name] [--branch branch-name] [--no-pr]
```

Options:
- `--repo` (required): Repository in `owner/repo` format
- `--prompt` (required): Initial instructions for the agent
- `--model` (optional): Model to use (defaults to `gpt-5.2` if not specified)
- `--branch` (optional): Target branch name (auto-generated if omitted)
- `--no-pr` (optional): Don't auto-create a PR

**Note:** When launched without `--model`, the skill automatically uses `gpt-5.2` and displays a message indicating which model is being used.

### Check Status

```bash
cursor-api.sh status <agent-id>
```

Returns:
- `status`: CREATING, RUNNING, FINISHED, STOPPED, ERROR
- `summary`: Summary of work done (if finished)
- `prUrl`: URL to created PR (if any)

### Get Conversation

```bash
cursor-api.sh conversation <agent-id>
```

Returns full message history including all prompts and responses.

### Send Follow-up

```bash
cursor-api.sh followup <agent-id> --prompt "Additional instructions"
```

Resumes a stopped or finished agent with new instructions.

### Stop Agent

```bash
cursor-api.sh stop <agent-id>
```

Stops a running agent gracefully.

### Delete Agent

```bash
cursor-api.sh delete <agent-id>
```

Permanently deletes an agent and its conversation history.

### List Models

```bash
cursor-api.sh models
```

Returns available models for agent tasks.

### Account Info

```bash
cursor-api.sh me
```

Returns account information including subscription tier.

### Verify Repository

```bash
cursor-api.sh verify owner/repo
```

Checks if the specified repository is accessible by Cursor agents.

Exit code 4 if repository not accessible.

### Usage/Cost Tracking

```bash
cursor-api.sh usage
```

Returns usage information including:
- Agents used vs. limit
- Compute consumption
- Subscription tier

### Clear Cache

```bash
cursor-api.sh clear-cache
```

Clears the response cache.

## Rate Limiting

The skill enforces a **1 request per second** rate limit locally to avoid API rate limits. This is applied automatically to all API calls.

If you hit Cursor's API rate limit (HTTP 429), the script exits with code 3.

## Caching

GET requests (`list`, `status`, `conversation`, `models`, `me`) are cached for 60 seconds by default. To disable caching for a command:

```bash
cursor-api.sh --no-cache status agent_123
```

To change the cache TTL, set the environment variable:

```bash
export CURSOR_CACHE_TTL=120  # 2 minutes
cursor-api.sh status agent_123
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API error (including non-existent resources) |
| 2 | Authentication missing or invalid |
| 3 | Rate limited |
| 4 | Repository not accessible |
| 5 | Invalid arguments |

## Testing

The skill includes a comprehensive test suite (`cca-comprehensive-test.sh`) that validates:

- **Authentication**: Auto-discovery, missing key, invalid key handling
- **Account Commands**: me, usage, models
- **Agent Lifecycle**: list, launch (with/without model), status, conversation, followup, stop
- **Error Handling**: Invalid formats, missing args, non-existent agents (all return correct exit codes)
- **Options**: --verbose, --no-cache, pagination

All tests pass with proper exit codes. Error conditions are correctly handled and return appropriate exit codes.

## Concurrent Agent Limits

Based on available documentation and API behavior, Cursor Cloud Agents have the following limits:

| Tier | Concurrent Agents | Notes |
|------|-------------------|-------|
| Free | 1 | Limited to basic models |
| Pro | 3 | Access to most models |
| Ultra | 5 | Full model access, priority queue |

These limits are enforced at the account level across all agents. If you exceed the limit, the API returns HTTP 429 with code `CONCURRENT_LIMIT`.

**To check your current usage:**
```bash
cursor-api.sh usage | jq '.usage.agentsUsed, .limits.concurrentAgents'
```

**Best practices:**
1. Stop finished agents when no longer needed
2. Use `cursor-api.sh list` to monitor active agents
3. Consider batching work into fewer, larger agents rather than many small ones

> **Note:** Concurrent limits are subject to change. Check `cursor-api.sh usage` for your current account limits.

## Best Practices

### 1. Always Verify Repository Access

Before launching, verify the repository is accessible:

```bash
if cursor-api.sh verify owner/repo >/dev/null 2>&1; then
    cursor-api.sh launch --repo owner/repo --prompt "..."
else
    echo "Repository not accessible. Install the Cursor GitHub App."
fi
```

### 2. Use Clear, Specific Prompts

Good prompt:
> "Add comprehensive unit tests for the auth module in src/auth/, covering login, logout, and token refresh. Use Jest and mock external API calls."

Bad prompt:
> "Add some tests"

### 3. Check Usage Before Launching

Monitor your quota:

```bash
cursor-api.sh usage | jq '.usage'
```

### 4. Clean Up Finished Agents

Delete agents you no longer need:

```bash
cursor-api.sh list | jq -r '.[] | select(.status == "FINISHED") | .id' | while read id; do
    cursor-api.sh delete "$id"
done
```

### 5. Handle Errors Gracefully

Always check exit codes in scripts:

```bash
if ! response=$(cursor-api.sh launch --repo owner/repo --prompt "..." 2>&1); then
    case $? in
        2) echo "Authentication error - check CURSOR_API_KEY" ;;
        3) echo "Rate limited - try again later" ;;
        4) echo "Repository not accessible" ;;
        *) echo "API error: $response" ;;
    esac
fi
```

## Follow-up Templates

Use these templates for common follow-up scenarios:

### "Add more tests"
```
Also add tests for edge cases: empty input, null values, and maximum length limits.
```

### "Fix the implementation"
```
The current implementation doesn't handle [specific case]. Please update it to [requirement].
```

### "Add documentation"
```
Add comprehensive JSDoc comments to all public functions and a brief README section explaining the feature.
```

### "Refactor for clarity"
```
Refactor the code to use more descriptive variable names and extract complex logic into helper functions.
```

## Companion Setup: CLI Backend

For local tasks (not on GitHub repos), also configure the Cursor Agent CLI as a `cliBackend`:

```json5
// In your OpenClaw config
{
  "cliBackends": {
    "cursor-agent": {
      "command": "agent",
      "args": ["-p", "--force", "--output-format", "text"],
      "output": "text",
      "input": "arg",
      "env": {
        "CURSOR_API_KEY": "${CURSOR_API_KEY}"
      }
    }
  }
}
```

This enables `cursor-agent` as a backend for local file operations, while this skill handles Cloud Agents for GitHub repos.

## Troubleshooting

### "Repository not accessible" (exit code 4)

1. Ensure the Cursor GitHub App is installed on the repository
2. Check that you have admin/write access to the repo
3. Verify the repo name is correct (`owner/repo` format)

### "Authentication failed" (exit code 2)

1. Check that `CURSOR_API_KEY` is set in your environment
2. Verify the API key is valid in Cursor IDE settings
3. Ensure the key hasn't expired

### "Rate limited" (exit code 3)

1. Wait a few seconds and retry
2. Check your usage with `cursor-api.sh usage`
3. Consider stopping unused agents

### Agent stuck in "CREATING" status

Agents may take 1-2 minutes to start. If stuck longer:
1. Check Cursor status page for outages
2. Try stopping and relaunching
3. Contact Cursor support if persistent
