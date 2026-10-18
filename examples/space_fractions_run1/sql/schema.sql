-- Space Fractions — SQLite schema
-- Adapted from the document's `games` DDL (PostgreSQL SERIAL/JSONB -> SQLite INTEGER/TEXT JSON),
-- plus the `questions` and `scores` tables required for question persistence (ASR-1)
-- and score viewing.

CREATE TABLE IF NOT EXISTS games (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state  TEXT NOT NULL                       -- JSON document holding a game snapshot
);

CREATE TABLE IF NOT EXISTS questions (
    id          TEXT PRIMARY KEY,                   -- stable string id (seed or admin-created)
    prompt      TEXT NOT NULL,
    type        TEXT NOT NULL CHECK (type IN ('equivalent', 'compare', 'add_subtract', 'simplify')),
    options     TEXT NOT NULL DEFAULT '[]',         -- JSON list of answer options (may be empty for typed)
    answer      TEXT NOT NULL                       -- canonical answer as a Fraction string (e.g. "1/2")
);

CREATE TABLE IF NOT EXISTS scores (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL,
    score       INTEGER NOT NULL,
    total       INTEGER NOT NULL,
    percentage  REAL NOT NULL,
    stars       INTEGER NOT NULL,
    timestamp   TEXT NOT NULL                       -- ISO-8601 datetime
);

CREATE INDEX IF NOT EXISTS idx_scores_username ON scores(username);
