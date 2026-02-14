# SurrealDB Memory

Knowledge graph memory system with semantic search, MCP tools, and LLM-powered extraction.

## Features

- 🔍 **Semantic Search** - Vector embeddings with cosine similarity
- 🧠 **MCP Tools** - 4 tools for search, recall, store, stats
- 📊 **Confidence Scoring** - With decay and relationship boosts
- 🔗 **Knowledge Graph** - Facts, entities, and relationships
- 🤖 **LLM Extraction** - Auto-extract facts from memory files

## ⚠️ Security Considerations

Before installing, please review:

| Behavior | Description | Mitigation |
|----------|-------------|------------|
| **Network Installer** | `scripts/install.sh` runs `curl https://install.surrealdb.com \| sh` | Install SurrealDB manually from [official releases](https://surrealdb.com/install) |
| **Source Patching** | `scripts/integrate-clawdbot.sh` patches Clawdbot source files | Run integration manually or skip UI integration |
| **Service Management** | Gateway can start SurrealDB and run schema imports | Start SurrealDB manually |
| **Default Credentials** | Examples use `root/root` | Change credentials for any network-exposed deployment |
| **API Key Usage** | Requires `OPENAI_API_KEY` for embeddings/extraction | Use a scoped key with minimal permissions |

**Recommended safe install path:**
1. Install SurrealDB manually from official releases
2. Create a Python venv and review `scripts/requirements.txt`
3. Set `OPENAI_API_KEY` with a scoped, non-admin key
4. Run initialization steps manually
5. Skip `integrate-clawdbot.sh` or review diffs carefully

## Requirements

- Python 3.10+
- SurrealDB 2.0+
- `OPENAI_API_KEY` environment variable (for embeddings and LLM extraction)

## Quick Start

```bash
# Install SurrealDB (or install manually from surrealdb.com/install)
./scripts/install.sh

# Start database (change credentials in production!)
surreal start --bind 127.0.0.1:8000 --user root --pass root file:~/.clawdbot/memory/knowledge.db

# Initialize schema
./scripts/init-db.sh

# Setup Python env
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt

# Set API key
export OPENAI_API_KEY="sk-..."

# Run extraction
python3 scripts/extract-knowledge.py extract --full
```

## MCP Tools

```bash
# Via mcporter
mcporter call surrealdb-memory.knowledge_stats
mcporter call surrealdb-memory.knowledge_search query="topic" limit:5
mcporter call surrealdb-memory.knowledge_recall query="topic"
mcporter call surrealdb-memory.knowledge_store content="New fact"
```

## License

MIT
