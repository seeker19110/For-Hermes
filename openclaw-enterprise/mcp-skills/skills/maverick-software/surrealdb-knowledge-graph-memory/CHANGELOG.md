# Changelog

All notable changes to the SurrealDB Memory skill will be documented in this file.

## [1.3.0] - 2026-02-11

### Added
- **Metadata transparency** for ClawHub compliance:
  - Declared `OPENAI_API_KEY` as required environment variable
  - Added `capabilities` section documenting system-modifying behaviors
  - Added `securityNotes` for credential and API key guidance
  - Added `installWarnings` array with pre-install considerations
- Security section in README.md with mitigation guidance
- Security section in SKILL.md with behavior table

### Fixed
- Fixed schema filename reference in `memory.ts` (`schema.surql` → `schema.sql`)

### Security
- Documented network installer behavior (`curl | sh`) with mitigation
- Documented source patching behavior with mitigation
- Documented default credential usage (root/root) with warning
- Documented API key scope requirements

### Changed
- Bumped version to 1.3.0 for metadata changes

## [1.2.0] - 2026-02-09

### Added
- **MCP Server** (`scripts/mcp-server.py`) with 4 tools:
  - `knowledge_search` - Semantic search for facts
  - `knowledge_recall` - Recall fact with full context
  - `knowledge_store` - Store new facts
  - `knowledge_stats` - Get knowledge graph statistics
- **Simple CLI** (`scripts/knowledge-tool.py`) for quick access
- MCP configuration in `package.json`

### Fixed
- Fixed recursive `close_db()` bug that caused stack overflow
- Fixed SQL `ORDER BY` clause to use alias instead of full expression
- Fixed `SELECT * FROM $fact_id` query to use `db.select()` method

## [1.1.0] - 2026-02-09

### Added
- Gateway integration (`clawdbot-integration/gateway/memory.ts`)
- Relation discovery with AI
- Control UI support
- Health checks and auto-repair

### Changed
- Improved extraction pipeline
- Better error handling

## [1.0.0] - 2026-01-31

### Added
- Initial release
- SurrealDB schema with vector search
- Knowledge extraction from memory files
- Confidence scoring with decay
- CLI tools for CRUD operations
- Entity and relationship management
