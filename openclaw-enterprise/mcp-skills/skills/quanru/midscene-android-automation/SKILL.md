---
name: Android Device Automation
description: >
  AI-powered Android device automation using Midscene.
  Control Android devices with natural language commands via ADB.
  Perform taps, swipes, text input, app launches, screenshots, and more.
triggers:
  - android
  - phone
  - mobile app
  - tap
  - swipe
  - install app
  - open app on phone
  - android device
  - mobile automation
  - adb
  - launch app
  - mobile screen
allowed-tools:
  - Bash
---

# Android Device Automation

> **CRITICAL RULES — VIOLATIONS WILL BREAK THE WORKFLOW:**
>
> 1. **NEVER set `run_in_background: true`** on any Bash tool call for midscene commands. Every `npx @midscene/android` command MUST use `run_in_background: false` (or omit the parameter entirely). Background execution causes notification spam after the task ends and breaks the screenshot-analyze-act loop.
> 2. **Send only ONE midscene CLI command per Bash tool call.** Wait for its result, read the screenshot, then decide the next action. Do NOT chain commands with `&&`, `;`, or `sleep`.
> 3. **Set `timeout: 60000`** (60 seconds) on each Bash tool call to allow sufficient time for midscene commands to complete synchronously.

Automate Android devices using `npx @midscene/android`. Each CLI command maps directly to an MCP tool — you (the AI agent) act as the brain, deciding which actions to take based on screenshots.

## Prerequisites

The CLI automatically loads `.env` from the current working directory. Before first use, verify the `.env` file exists and contains the API key:

```bash
cat .env | grep MIDSCENE_MODEL_API_KEY | head -c 30
```

If no `.env` file or no API key, ask the user to create one. See [Model Configuration](https://midscenejs.com/zh/model-common-config.html) for supported providers.

**Do NOT run `echo $MIDSCENE_MODEL_API_KEY`** — the key is loaded from `.env` at runtime, not from shell environment.

## Commands

### Connect to Device

```bash
npx @midscene/android connect
npx @midscene/android connect --deviceId emulator-5554
```

### Take Screenshot

```bash
npx @midscene/android take_screenshot
```

After taking a screenshot, read the saved image file to understand the current screen state before deciding the next action.

### Perform Actions

Use actionSpace tools to interact with the device. Each action uses `--locate` to describe which element to target:

```bash
npx @midscene/android Tap --locate '{"prompt":"the Settings icon"}'
npx @midscene/android Input --locate '{"prompt":"search field"}' --content 'hello world'
npx @midscene/android Scroll --direction down
npx @midscene/android Swipe --locate '{"prompt":"the notification panel"}' --direction down
npx @midscene/android KeyboardPress --value Enter
npx @midscene/android LongPress --locate '{"prompt":"the message bubble"}'
npx @midscene/android Launch --uri 'com.android.settings'
```

### Natural Language Action

Use `act` to execute multi-step operations in a single command — useful for transient UI interactions:

```bash
npx @midscene/android act --prompt "long press the message, then tap Delete in the popup menu"
```

### Disconnect

```bash
npx @midscene/android disconnect
```

## Workflow Pattern

Since CLI commands are stateless between invocations, follow this pattern:

1. **Connect** to establish a session
2. **Take screenshot** to see the current state
3. **Analyze** the screenshot to decide the next action
4. **Execute action** (Tap, Input, Scroll, etc.)
5. **Take screenshot** again to verify the result
6. **Repeat** steps 3-5 until the task is complete
7. **Disconnect** when done

## Best Practices

1. **Take screenshots frequently**: Before and after each action to verify state changes.
2. **Describe UI elements clearly**: Use visible text labels, icons, or positional descriptions (e.g., `"the search icon at the top right"` rather than vague references).
3. **Use JSON for locate parameter**: Always pass `--locate` as a JSON string with a `prompt` field describing the target element visually.
4. **Chain actions sequentially**: Execute one action at a time and verify the result before moving to the next step.
5. **Never run in background**: On every Bash tool call, either omit `run_in_background` or explicitly set it to `false`. Never set `run_in_background: true`.

### Handle Transient UI

Popup menus, toasts, bottom sheets, and snackbars **disappear** between commands. When interacting with transient UI:

- **Use `act` for multi-step transient interactions** — it executes everything in a single process
- **Or execute commands rapidly in sequence** — do NOT take screenshots between steps
- **Do NOT pause to analyze** — run all commands for the transient interaction back-to-back
- Persistent UI (app screens, navigation drawers that stay open) is fine to interact with across separate commands

**Example — Long press popup menu using `act` (recommended for transient UI):**

```bash
npx @midscene/android act --prompt "long press the message bubble, then tap Delete in the popup menu"
npx @midscene/android take_screenshot
```

**Example — Long press popup menu using individual commands (alternative):**

```bash
# These commands must be run back-to-back WITHOUT screenshots in between
npx @midscene/android LongPress --locate '{"prompt":"the message bubble"}'
npx @midscene/android Tap --locate '{"prompt":"Delete option in the popup menu"}'
# NOW take a screenshot to verify the result
npx @midscene/android take_screenshot
```

## Troubleshooting

| Problem | Solution |
|---|---|
| **ADB not found** | Install Android SDK Platform Tools: `brew install android-platform-tools` (macOS) or download from [developer.android.com](https://developer.android.com/tools/releases/platform-tools). |
| **Device not listed** | Check USB connection, ensure USB debugging is enabled in Developer Options, and run `adb devices`. |
| **Device shows "unauthorized"** | Unlock the device and accept the USB debugging authorization prompt. Then run `adb devices` again. |
| **Device shows "offline"** | Disconnect and reconnect the USB cable. Run `adb kill-server && adb start-server`. |
| **Command timeout** | The device screen may be off or locked. Wake the device with `adb shell input keyevent KEYCODE_WAKEUP` and unlock it. |
| **API key error** | Check `.env` file contains `MIDSCENE_MODEL_API_KEY=<your-key>`. See [Model Configuration](https://midscenejs.com/zh/model-common-config.html). |
| **Wrong device targeted** | If multiple devices are connected, use `--deviceId <id>` flag with the `connect` command. |
