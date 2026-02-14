# Xiaoxia Diary

Writes a daily diary entry for the Xiaoxia (Catgirl Persona) to Feishu Docs and notifies the Master.
Uses the LLM to generate the diary content based on the day's memory (`memory/YYYY-MM-DD.md`) and mood (`memory/mood.json`).

## Usage

```bash
node skills/xiaoxia-diary/index.js
```

## Configuration
- `DIARY_DOC_TOKEN`: The Token of the Feishu Doc to write to.
- `MASTER_ID`: User ID to notify.
- `GEMINI_API_KEY`: Used for content generation.
