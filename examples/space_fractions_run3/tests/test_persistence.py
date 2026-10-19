"""Persistence tests using a temporary SQLite file (questions, scores, games)."""
import json
import os
import sqlite3
import tempfile

import pytest

from questions.repository import QuestionRepository
from questions.question import Question
from ui.score_repository import ScoreRepository


def test_questions_crud(tmp_path):
    db = str(tmp_path / "test.db")
    conn = sqlite3.connect(db)
    repo = QuestionRepository(db)
    repo.init_schema(conn)
    q = Question(id="q1", prompt="p", options=["a", "b"], answer="a", qtype="equivalent")
    repo.upsert(conn, q)
    conn.commit()
    got = repo.get(conn, "q1")
    assert got.prompt == "p"
    assert got.options == ["a", "b"]
    assert repo.count(conn) == 1
    assert repo.delete(conn, "q1") is True
    assert repo.count(conn) == 0


def test_seed_from_json(tmp_path):
    db = str(tmp_path / "test.db")
    seed = tmp_path / "questions.json"
    seed.write_text(json.dumps([
        {"id": "s1", "qtype": "equivalent", "prompt": "p", "options": [], "answer": "1/2", "explanation": ""}
    ]))
    conn = sqlite3.connect(db)
    repo = QuestionRepository(db, str(seed))
    repo.init_schema(conn)
    n = repo.seed_from_json(conn)
    conn.commit()
    assert n == 1
    assert repo.count(conn) == 1


def test_games_table(tmp_path):
    db = str(tmp_path / "test.db")
    conn = sqlite3.connect(db)
    conn.executescript(open("sql/schema.sql").read())
    conn.execute("INSERT INTO games (game_state) VALUES (?)", (json.dumps({"state": "Playing"}),))
    conn.commit()
    row = conn.execute("SELECT game_state FROM games").fetchone()
    assert json.loads(row[0])["state"] == "Playing"


def test_scores(tmp_path):
    db = str(tmp_path / "test.db")
    conn = sqlite3.connect(db)
    repo = ScoreRepository(db)
    repo.init_schema(conn)
    repo.add_score(conn, "kid", 800, 10, 80.0, 2)
    repo.add_score(conn, "kid2", 900, 10, 90.0, 3)
    rows = repo.top_scores(10)
    assert rows[0][0] == "kid2"  # highest percentage first
    assert rows[1][0] == "kid"
