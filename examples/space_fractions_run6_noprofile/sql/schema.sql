-- SQLite schema for Space Fractions (adapted from PostgreSQL DDL).
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id   TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    role  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id       TEXT PRIMARY KEY,
    prompt   TEXT NOT NULL,
    correct  TEXT NOT NULL,
    kind     TEXT NOT NULL CHECK (kind IN ('choice', 'typed')),
    options  TEXT NOT NULL  -- JSON array for choice questions
);

CREATE TABLE IF NOT EXISTS games (
    id         TEXT PRIMARY KEY,
    game_state TEXT NOT NULL,     -- 'Playing' | 'Paused' | 'GameOver'
    score      INTEGER NOT NULL,
    played_at  TEXT NOT NULL
);
