-- SQLite DDL adapted from the spec's games DDL + question persistence (ASR-1)
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'identify',
    correct_value TEXT NOT NULL,
    choices TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state TEXT NOT NULL
);
