-- SQLite DDL adapted from the spec's PostgreSQL DDL (games + question tables).
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    correct TEXT NOT NULL,
    options TEXT NOT NULL,
    kind TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    played_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    role TEXT NOT NULL
);
