# Wang Weichao Daily Push Skill

Automated knowledge dissemination service for user `ou_cea17106dcef3d45a73387d049bf2ebe`.
Follows the protocol defined in `memory/protocols/wangweichao_push_protocol.md`.

## Features
- **Auto-Generation**: Uses LLM to generate 3 daily topics (Humanities, Tech, Game Design).
- **Rich Formatting**: Sends structured Feishu Post messages.
- **Tracking**: Logs daily pushes to prevent duplicates.

## Usage
```bash
node skills/wangweichao-push/push.js --force
```

## Dependencies
- `feishu-post` (for sending rich text)
- `memory/protocols/wangweichao_push_protocol.md` (source of truth)
