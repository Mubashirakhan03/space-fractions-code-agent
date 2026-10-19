-- Space Fractions — SQLite schema
-- Adapted from the document's games DDL (PostgreSQL JSONB -> SQLite TEXT) and
-- the referenced-but-missing question_ddl.sql; plus a scores table for high scores.

-- Master question bank managed by Admin (Update Questions).
CREATE TABLE IF NOT EXISTS questions (
    id         TEXT PRIMARY KEY,
    qtype      TEXT NOT NULL,            -- equivalent | compare | add_subtract | simplify
    prompt     TEXT NOT NULL,
    options    TEXT NOT NULL,            -- JSON array of strings (empty for typed answers)
    answer     TEXT NOT NULL,            -- canonical answer; equivalent forms accepted
    explanation TEXT NOT NULL DEFAULT ''
);

-- A played game session. game_state serialised as JSON text (PostgreSQL JSONB -> TEXT).
CREATE TABLE IF NOT EXISTS games (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state TEXT NOT NULL
);

-- High scores recorded at the end of a game.
CREATE TABLE IF NOT EXISTS scores (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    score      INTEGER NOT NULL,
    total      INTEGER NOT NULL,         -- questions answered
    percentage REAL NOT NULL,
    stars      INTEGER NOT NULL,
    played_at  TEXT NOT NULL             -- ISO-8601 timestamp
);

CREATE INDEX IF NOT EXISTS idx_scores_pct ON scores (percentage DESC, played_at DESC);
