-- Space Fractions — SQLite DDL (adapted from spec's PostgreSQL DDL:
--   games table (JSONB game_state -> flattened columns), questions from question_ddl.sql)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    kind TEXT NOT NULL,
    options TEXT NOT NULL,          -- JSON array of option strings
    correct_index INTEGER NOT NULL,
    explanation TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    total INTEGER NOT NULL,
    score INTEGER NOT NULL,
    rating TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
