---
name: Chrome Bridge Automation
description: |
  AI-powered browser automation using Midscene Bridge mode. Use this skill when the user wants to:
  - Browse, navigate, or open web pages in the user's own Chrome browser
  - Interact with pages that require login sessions, cookies, or existing browser state
  - Scrape, extract, or collect data from websites using the user's real browser
  - Fill out forms, click buttons, or interact with web elements
  - Verify, validate, or test frontend UI behavior
  - Take screenshots of web pages
  - Automate multi-step web workflows
  - Check website content or appearance

  This mode connects to the user's real Chrome browser via the Midscene Chrome Extension,
  preserving cookies, sessions, and login state.

  Trigger keywords: browse, navigate, open url, web page, website, scrape, extract, crawl,
  fill form, click, interact, verify, validate, test, assert, screenshot, frontend, UI test,
  web automation, search web, check page, login, submit, chrome, bridge
allowed-tools:
  - Bash
---

# Chrome Bridge Automation

> **CRITICAL RULES — VIOLATIONS WILL BREAK THE WORKFLOW:**
>
> 1. **NEVER set `run_in_background: true`** on any Bash tool call for midscene commands. Every `npx @midscene/web` command MUST use `run_in_background: false` (or omit the parameter entirely). Background execution causes notification spam after the task ends and breaks the screenshot-analyze-act loop.
> 2. **Send only ONE midscene CLI command per Bash tool call.** Wait for its result, read the screenshot, then decide the next action. Do NOT chain commands with `&&`, `;`, or `sleep`.
> 3. **Set `timeout: 60000`** (60 seconds) on each Bash tool call to allow sufficient time for midscene commands to complete synchronously.

Automate the user's real Chrome browser via the Midscene Chrome Extension (Bridge mode), preserving cookies, sessions, and login state. You (the AI agent) act as the brain, deciding which actions to take based on screenshots.

## Command Format

**CRITICAL — Every command MUST follow this EXACT format. Do NOT modify the command prefix.**

```
npx @midscene/web --bridge <subcommand> [args]
```

- `--bridge` flag is **MANDATORY** — it activates Bridge mode to connect to the user's real Chrome
- Without `--bridge`, the CLI launches a separate headless browser (wrong behavior for this skill)
- Do NOT use `-p` flag, do NOT use environment variables as substitutes — use `--bridge` exactly as shown

## Prerequisites

The user has already prepared Chrome and the Midscene Extension. Do NOT check browser or extension status — just connect directly.

The CLI automatically loads `.env` from the current working directory. Before first use, verify the `.env` file exists and contains the API key:

```bash
cat .env | grep MIDSCENE_MODEL_API_KEY | head -c 30
```

If no `.env` file or no API key, ask the user to create one. See [Model Configuration](https://midscenejs.com/zh/model-common-config.html) for supported providers.

**Do NOT run `echo $MIDSCENE_MODEL_API_KEY`** — the key is loaded from `.env` at runtime, not from shell environment.

## Commands

### Connect to a Web Page

```bash
npx @midscene/web --bridge connect --url https://example.com
```

### Take Screenshot

```bash
npx @midscene/web --bridge take_screenshot
```

After taking a screenshot, read the saved image file to understand the current page state before deciding the next action.

### Perform Actions

```bash
npx @midscene/web --bridge Tap --locate '{"prompt":"the Login button"}'
npx @midscene/web --bridge Input --locate '{"prompt":"the email field"}' --value 'user@example.com'
npx @midscene/web --bridge Scroll --direction down
npx @midscene/web --bridge Hover --locate '{"prompt":"the navigation menu"}'
npx @midscene/web --bridge KeyboardPress --value Enter
npx @midscene/web --bridge DragAndDrop --locate '{"prompt":"the draggable item"}' --target '{"prompt":"the drop zone"}'
```

### Natural Language Action

Use `act` to execute multi-step operations in a single command — useful for transient UI interactions:

```bash
npx @midscene/web --bridge act --prompt "click the country dropdown and select Japan"
```

### Disconnect

```bash
npx @midscene/web --bridge disconnect
```

## Workflow Pattern

Since CLI commands are stateless between invocations, follow this pattern:

1. **Connect** to a URL to establish a session
2. **Take screenshot** to see the current state
3. **Analyze** the screenshot to decide the next action
4. **Execute action** (Tap, Input, Scroll, etc.)
5. **Take screenshot** again to verify the result
6. **Repeat** steps 3-5 until the task is complete
7. **Disconnect** when done

## Best Practices

1. **Always connect first**: Navigate to the target URL with `connect --url` before any interaction.
2. **Take screenshots frequently**: Before and after each action to verify state changes.
3. **Be specific in locate prompts**: Instead of `"the button"`, say `"the blue Submit button in the contact form"`.
4. **Use natural language**: Describe what you see on the page, not CSS selectors. Say `"the red Buy Now button"` instead of `"#buy-btn"`.
5. **Handle loading states**: After navigation or actions that trigger page loads, take a screenshot to verify the page has loaded.
6. **Disconnect when done**: Always disconnect to free resources.
7. **Never run in background**: On every Bash tool call, either omit `run_in_background` or explicitly set it to `false`. Never set `run_in_background: true`.

### Handle Transient UI

Dropdowns, autocomplete popups, tooltips, and confirm dialogs **disappear** between commands. When interacting with transient UI:

- **Use `act` for multi-step transient interactions** — it executes everything in a single process
- **Or execute commands rapidly in sequence** — do NOT take screenshots between steps
- **Do NOT pause to analyze** — run all commands for the transient interaction back-to-back
- Persistent UI (page content, navigation bars, sidebars) is fine to interact with across separate commands

**Example — Dropdown selection using `act` (recommended for transient UI):**

```bash
npx @midscene/web --bridge act --prompt "click the country dropdown and select Japan"
npx @midscene/web --bridge take_screenshot
```

**Example — Dropdown selection using individual commands (alternative):**

```bash
# These commands must be run back-to-back WITHOUT screenshots in between
npx @midscene/web --bridge Tap --locate '{"prompt":"the country dropdown"}'
npx @midscene/web --bridge Tap --locate '{"prompt":"Japan option in the dropdown list"}'
# NOW take a screenshot to verify the result
npx @midscene/web --bridge take_screenshot
```

## Common Patterns

### Simple Browsing

```bash
npx @midscene/web --bridge connect --url 'https://news.ycombinator.com'
npx @midscene/web --bridge take_screenshot
# Read the screenshot, then decide next action
npx @midscene/web --bridge disconnect
```

### Multi-Step Interaction

```bash
npx @midscene/web --bridge connect --url 'https://example.com'
npx @midscene/web --bridge Tap --locate '{"prompt":"the Sign In link"}'
npx @midscene/web --bridge take_screenshot
npx @midscene/web --bridge Input --locate '{"prompt":"the email field"}' --value 'user@example.com'
npx @midscene/web --bridge Input --locate '{"prompt":"the password field"}' --value 'password123'
npx @midscene/web --bridge Tap --locate '{"prompt":"the Log In button"}'
npx @midscene/web --bridge take_screenshot
npx @midscene/web --bridge disconnect
```

## Troubleshooting

### Bridge Mode Connection Failures
- Ensure Chrome is open with the Midscene Extension installed and enabled.
- Check that the extension shows "Connected" status.
- See the [Bridge Mode documentation](https://midscenejs.com/bridge-mode-by-chrome-extension.html).

### API Key Errors
- Check `.env` file contains `MIDSCENE_MODEL_API_KEY=<your-key>`.
- Verify the key is valid for the configured model provider.

### Timeouts
- Web pages may take time to load. After connecting, take a screenshot to verify readiness before interacting.
- For slow pages, wait briefly between steps.

### Screenshots Not Displaying
- The screenshot path is an absolute path to a local file. Use the Read tool to view it.
