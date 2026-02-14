// lib/db.js – SQLite connection + helpers
const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const BASE_DIR = path.resolve(__dirname, '..');
let _db = null;

function getConfig() {
  const cfgPath = path.join(BASE_DIR, 'config.json');
  if (!fs.existsSync(cfgPath)) {
    throw new Error('config.json not found. Run: node setup.js');
  }
  return JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
}

function getDb() {
  if (_db) return _db;
  const config = getConfig();
  const dbPath = path.resolve(BASE_DIR, config.paths.dbFile);
  const dir = path.dirname(dbPath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  _db = new Database(dbPath);
  _db.pragma('journal_mode = WAL');
  _db.pragma('foreign_keys = ON');

  // Auto-migrations (safe to run repeatedly)
  runMigrations(_db);

  return _db;
}

function runMigrations(db) {
  const migrations = [
    // === v1.2.0 ===
    "ALTER TABLE proposals ADD COLUMN follow_up TEXT",

    // === v1.3.0 – Dedup ===
    "ALTER TABLE proposals ADD COLUMN topic_hash TEXT",
    "ALTER TABLE proposals ADD COLUMN times_presented INTEGER DEFAULT 1",
    "ALTER TABLE proposals ADD COLUMN last_presented_at DATETIME",
    "ALTER TABLE proposals ADD COLUMN presentation_variant INTEGER DEFAULT 1",
    "ALTER TABLE proposals ADD COLUMN dedup_parent_id INTEGER",
    "CREATE INDEX IF NOT EXISTS idx_proposals_topic_hash ON proposals(topic_hash)",

    // === v1.3.0 – Proposal Events ===
    `CREATE TABLE IF NOT EXISTS proposal_events (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      proposal_id INTEGER NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
      action      TEXT NOT NULL,
      note        TEXT,
      created_at  DATETIME DEFAULT (datetime('now'))
    )`,
    "CREATE INDEX IF NOT EXISTS idx_proposal_events_proposal ON proposal_events(proposal_id)",
    "CREATE INDEX IF NOT EXISTS idx_proposal_events_action ON proposal_events(action)",

    // === v1.3.0 – Proposals FTS (standalone, NOT content-external) ===
    `CREATE VIRTUAL TABLE IF NOT EXISTS proposals_fts USING fts5(
      title, description
    )`,
    `CREATE TRIGGER IF NOT EXISTS proposals_fts_ai AFTER INSERT ON proposals BEGIN
      INSERT INTO proposals_fts(rowid, title, description)
      VALUES (new.id, new.title, new.description);
    END`,
    `CREATE TRIGGER IF NOT EXISTS proposals_fts_ad AFTER DELETE ON proposals BEGIN
      DELETE FROM proposals_fts WHERE rowid = old.id;
    END`,
    `CREATE TRIGGER IF NOT EXISTS proposals_fts_au AFTER UPDATE ON proposals BEGIN
      DELETE FROM proposals_fts WHERE rowid = old.id;
      INSERT INTO proposals_fts(rowid, title, description)
      VALUES (new.id, new.title, new.description);
    END`,
  ];

  for (const sql of migrations) {
    try { db.exec(sql); } catch { /* already applied */ }
  }

  // Backfill FTS for existing proposals (simple INSERT for standalone FTS)
  try {
    const hasFts = db.prepare(
      "SELECT name FROM sqlite_master WHERE name = 'proposals_fts' AND type = 'table'"
    ).get();
    if (hasFts) {
      const ftsCount = db.prepare("SELECT COUNT(*) as c FROM proposals_fts").get();
      const propCount = db.prepare("SELECT COUNT(*) as c FROM proposals").get();
      if (ftsCount.c === 0 && propCount.c > 0) {
        db.exec(`
          INSERT INTO proposals_fts(rowid, title, description)
          SELECT id, title, description FROM proposals
        `);
        console.log(`[DB] Backfilled proposals_fts with ${propCount.c} entries`);
      }
    }
  } catch (e) {
    console.warn(`[DB] FTS backfill warning: ${e.message}`);
  }
}

function initSchema() {
  const db = getDb();
  const schema = fs.readFileSync(
    path.join(BASE_DIR, 'templates', 'schema.sql'), 'utf8'
  );
  db.exec(schema);
  return db;
}

function closeDb() {
  if (_db) { _db.close(); _db = null; }
}

// Lockfile mechanism to prevent cron overlap
function acquireLock(jobName) {
  const config = getConfig();
  const lockPath = path.resolve(BASE_DIR, config.paths.lockFile);
  const lockData = fs.existsSync(lockPath)
    ? JSON.parse(fs.readFileSync(lockPath, 'utf8'))
    : {};

  if (lockData[jobName]) {
    const age = Date.now() - lockData[jobName];
    if (age < 30 * 60 * 1000) { // 30 min stale threshold
      console.log(`[SKIP] ${jobName} already running (${Math.round(age/1000)}s ago)`);
      return false;
    }
  }
  lockData[jobName] = Date.now();
  fs.writeFileSync(lockPath, JSON.stringify(lockData, null, 2));
  return true;
}

function releaseLock(jobName) {
  const config = getConfig();
  const lockPath = path.resolve(BASE_DIR, config.paths.lockFile);
  if (!fs.existsSync(lockPath)) return;
  const lockData = JSON.parse(fs.readFileSync(lockPath, 'utf8'));
  delete lockData[jobName];
  fs.writeFileSync(lockPath, JSON.stringify(lockData, null, 2));
}

// Rough token estimate (~4 chars per token for mixed content)
function estimateTokens(text) {
  return Math.ceil(text.length / 4);
}

// Update system_state timestamp
function updateState(key, value) {
  const db = getDb();
  db.prepare(
    'UPDATE system_state SET value = ?, updated_at = datetime(\'now\') WHERE key = ?'
  ).run(value || new Date().toISOString(), key);
}

function getState(key) {
  const db = getDb();
  const row = db.prepare('SELECT value FROM system_state WHERE key = ?').get(key);
  return row ? row.value : null;
}

// Log proposal lifecycle events
function logProposalEvent(proposalId, action, note = null) {
  const db = getDb();
  db.prepare(`
    INSERT INTO proposal_events (proposal_id, action, note)
    VALUES (?, ?, ?)
  `).run(proposalId, action, note);
}

module.exports = {
  getDb, initSchema, closeDb, getConfig,
  acquireLock, releaseLock,
  estimateTokens, updateState, getState,
  logProposalEvent,
  BASE_DIR
};
