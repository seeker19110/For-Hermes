---
name: Desktop Computer Automation
description: |
  AI-powered desktop automation using Midscene. Control your desktop (macOS, Windows, Linux) with natural language commands.
  Triggers: open app, press key, desktop, computer, click on screen, type text, screenshot desktop,
  launch application, switch window, desktop automation, control computer, mouse click, keyboard shortcut,
  screen capture, find on screen, read screen, verify window, close app, minimize window, maximize window
allowed-tools:
  - Bash
---

# Desktop Computer Automation

> **CRITICAL RULES — VIOLATIONS WILL BREAK THE WORKFLOW:**
>
> 1. **NEVER set `run_in_background: true`** on any Bash tool call for midscene commands. Every `npx @midscene/computer` command MUST use `run_in_background: false` (or omit the parameter entirely). Background execution causes notification spam after the task ends and breaks the screenshot-analyze-act loop.
> 2. **Send only ONE midscene CLI command per Bash tool call.** Wait for its result, read the screenshot, then decide the next action. Do NOT chain commands with `&&`, `;`, or `sleep`.
> 3. **Set `timeout: 60000`** (60 seconds) on each Bash tool call to allow sufficient time for midscene commands to complete synchronously.

Control your desktop (macOS, Windows, Linux) using `npx @midscene/computer`. Each CLI command maps directly to an MCP tool — you (the AI agent) act as the brain, deciding which actions to take based on screenshots.

## Prerequisites

The CLI automatically loads `.env` from the current working directory. Before first use, verify the `.env` file exists and contains the API key:

```bash
cat .env | grep MIDSCENE_MODEL_API_KEY | head -c 30
```

If no `.env` file or no API key, ask the user to create one. See [Model Configuration](https://midscenejs.com/zh/model-common-config.html) for supported providers.

**Do NOT run `echo $MIDSCENE_MODEL_API_KEY`** — the key is loaded from `.env` at runtime, not from shell environment.

## Commands

### Connect to Desktop

```bash
npx @midscene/computer connect
npx @midscene/computer connect --displayId <id>
```

### List Displays

```bash
npx @midscene/computer list_displays
```

### Take Screenshot

```bash
npx @midscene/computer take_screenshot
```

After taking a screenshot, read the saved image file to understand the current screen state before deciding the next action.

### Perform Actions

Use actionSpace tools to interact with the desktop:

```bash
npx @midscene/computer Tap --locate '{"prompt":"the Safari icon in the Dock"}'
npx @midscene/computer DoubleClick --locate '{"prompt":"the Documents folder"}'
npx @midscene/computer RightClick --locate '{"prompt":"the desktop background"}'
npx @midscene/computer Input --locate '{"prompt":"the search field"}' --content 'hello world'
npx @midscene/computer Scroll --direction down
npx @midscene/computer KeyboardPress --value 'Command+Space'
npx @midscene/computer DragAndDrop --locate '{"prompt":"the file icon"}' --target '{"prompt":"the Trash icon"}'
```

### Natural Language Action

Use `act` to execute multi-step operations in a single command — useful for transient UI interactions like Spotlight:

```bash
npx @midscene/computer act --prompt "press Command+Space, type Safari, press Enter"
```

### Disconnect

```bash
npx @midscene/computer disconnect
```

## Workflow Pattern

Since CLI commands are stateless between invocations, follow this pattern:

1. **Connect** to establish a session
2. **Take screenshot** to see the current state
3. **Analyze** the screenshot to decide the next action
4. **Execute action** (Tap, Input, KeyboardPress, etc.)
5. **Take screenshot** again to verify the result
6. **Repeat** steps 3-5 until the task is complete
7. **Disconnect** when done

## Best Practices

1. **Take screenshots frequently**: Before and after each action to verify state changes.
2. **Use keyboard shortcuts for reliability**: `KeyboardPress --value 'Command+C'` is often more reliable than clicking UI elements.
3. **Be specific about UI elements**: Instead of vague descriptions, provide clear, specific details. Say `"the red close button in the top-left corner of the Safari window"` instead of `"the close button"`.
4. **Describe locations when possible**: Help target elements by describing their position (e.g., `"the icon in the top-right corner of the menu bar"`, `"the third item in the left sidebar"`).
5. **Never run in background**: On every Bash tool call, either omit `run_in_background` or explicitly set it to `false`. Never set `run_in_background: true`.

### Handle Transient UI — MUST Use `act`

Each CLI command runs as a **separate process**. When a process exits, the OS may return focus to the terminal, which can dismiss transient UI (app launchers, context menus, dropdown menus, notification popups, etc.). This means **individual commands like `KeyboardPress` → `Input` will NEVER work for transient UI** — the UI disappears between commands.

**You MUST use `act` for ANY interaction that involves transient UI.** The `act` command executes all steps within a single process, keeping focus intact — just like `agent.aiAct()` in JavaScript.

- Persistent UI (app windows, file managers, taskbars/docks) is fine to interact with across separate commands with screenshots in between

**Example — Open an app via launcher (macOS Spotlight / Windows Start / Linux app menu):**

```bash
npx @midscene/computer act --prompt "open the app launcher, type Visual Studio Code, press Enter"
npx @midscene/computer take_screenshot
```

**Example — Context menu interaction:**

```bash
npx @midscene/computer act --prompt "right-click the file icon, then click Delete in the context menu"
npx @midscene/computer take_screenshot
```

**Example — Dropdown menu:**

```bash
npx @midscene/computer act --prompt "click the File menu, then click New Window"
npx @midscene/computer take_screenshot
```

## Common Patterns

### Open an Application via Launcher

**MUST use `act`** — the launcher dismisses when the CLI process exits, so individual commands will always fail.

```bash
# macOS
npx @midscene/computer act --prompt "press Command+Space, type Visual Studio Code, press Enter"
# Windows
npx @midscene/computer act --prompt "press the Windows key, type Visual Studio Code, press Enter"
# Linux (varies by DE)
npx @midscene/computer act --prompt "open the application menu, type Visual Studio Code, press Enter"
npx @midscene/computer take_screenshot
```

### Keyboard Shortcuts

```bash
# macOS uses Command, Windows/Linux use Ctrl
npx @midscene/computer KeyboardPress --value 'Command+C'
npx @midscene/computer KeyboardPress --value 'Ctrl+C'
```

### Window Management

```bash
# macOS
npx @midscene/computer KeyboardPress --value 'Command+W'
npx @midscene/computer KeyboardPress --value 'Command+Tab'
# Windows/Linux
npx @midscene/computer KeyboardPress --value 'Alt+F4'
npx @midscene/computer KeyboardPress --value 'Alt+Tab'
```

## Troubleshooting

### macOS: Accessibility Permission Denied
Your terminal app does not have Accessibility access:
1. Open **System Settings > Privacy & Security > Accessibility**
2. Add your terminal app and enable it
3. Restart your terminal app after granting permission

### macOS: Xcode Command Line Tools Not Found
```bash
xcode-select --install
```

### API Key Not Set
Check `.env` file contains `MIDSCENE_MODEL_API_KEY=<your-key>`.

### AI Cannot Find the Element
1. Take a screenshot to verify the element is actually visible
2. Use more specific descriptions (include color, position, surrounding text)
3. Ensure the element is not hidden behind another window
