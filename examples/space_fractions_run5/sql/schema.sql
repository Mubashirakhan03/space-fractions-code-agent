-- Space Fractions SQLite schema (adapted from the document's `games` DDL).
-- The document specified: CREATE TABLE games (id SERIAL PRIMARY KEY, game_state JSONB NOT NULL).
-- Adapted to SQLite and extended with `questions` and `scores`.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS games (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id      TEXT PRIMARY KEY,
    prompt  TEXT NOT NULL,
    answer  TEXT NOT NULL,
    options TEXT NOT NULL DEFAULT '',  -- JSON array of strings
    qtype   TEXT NOT NULL DEFAULT 'choice'
);

CREATE TABLE IF NOT EXISTS scores (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT NOT NULL,
    score     INTEGER NOT NULL,
    total     INTEGER NOT NULL,
    percentage REAL NOT NULL,
    played_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_scores_percentage ON scores (percentage DESC, score DESC, played_at DESC);
