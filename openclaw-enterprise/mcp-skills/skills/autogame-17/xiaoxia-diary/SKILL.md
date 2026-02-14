# xiaoxia-diary

Writes a daily diary entry for Xiaoxia (Catgirl Persona) to Feishu Docs and notifies Master. The content is generated based on the day's memory (`memory/YYYY-MM-DD.md`) and mood (`memory/mood.json`).

## Usage

Run manually or via cron:

```bash
node skills/xiaoxia-diary/index.js
```

## Configuration

Required environment variables (in `.env`):

- `DIARY_DOC_TOKEN`: The Token of the Feishu Doc where the diary is written.
- `MASTER_ID`: Feishu OpenID of the user to notify upon completion.
- `GEMINI_API_KEY`: API Key for content generation (if using Gemini directly).

## Dependencies

- `memory/YYYY-MM-DD.md`: Daily memory log.
- `memory/mood.json`: Current mood state (optional).
