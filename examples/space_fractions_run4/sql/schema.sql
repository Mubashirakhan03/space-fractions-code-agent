-- Space Fractions: SQLite schema (adapted from the document's DDL).
--
-- games   : kept for data-durability parity with the original `games` table
--           (stores a JSON snapshot of the game state).
-- questions: the question bank (QuestionComponent / ASR-1).
-- scores  : high-score persistence for the View Score use case.

CREATE TABLE IF NOT EXISTS games (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id        TEXT PRIMARY KEY,
    prompt    TEXT NOT NULL,
    options   TEXT NOT NULL DEFAULT '[]',  -- JSON array
    qtype     TEXT NOT NULL DEFAULT 'equivalent',
    answer    TEXT NOT NULL,
    is_choice INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS scores (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT NOT NULL,
    score     INTEGER NOT NULL,
    total     INTEGER NOT NULL,
    percentage INTEGER NOT NULL,
    stars     INTEGER NOT NULL,
    played_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_scores_score ON scores (score DESC);
