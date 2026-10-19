"""Persistence tests: SQLite schema creation and score round-trip."""
import sqlite3
from pathlib import Path

from game.game import GameResult

SCHEMA = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


def test_schema_creates_tables(tmp_path):
    db = tmp_path / "test.db"
    conn = sqlite3.connect(str(db))
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.commit()
    names = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"games", "questions", "scores"} <= names


def test_score_round_trip(tmp_path):
    db = tmp_path / "test.db"
    conn = sqlite3.connect(str(db))
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.execute(
        "INSERT INTO scores (username, score, total, percentage, stars)"
        " VALUES (?, ?, ?, ?, ?)", ("mia", 8, 10, 80, 2))
    conn.commit()
    row = conn.execute(
        "SELECT username, score, percentage, stars FROM scores").fetchone()
    conn.close()
    assert row == ("mia", 8, 80, 2)
