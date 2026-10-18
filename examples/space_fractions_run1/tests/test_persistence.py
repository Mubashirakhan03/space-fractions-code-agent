"""Persistence tests: repository seed load, CRUD, scores, games DDL."""
import json
import os

from questions import QuestionRepository
from users import ScoreRepository


def test_seed_questions_loaded(tmp_db):
    repo = QuestionRepository(tmp_db)
    n = repo.count()
    assert n >= 20
    # All four types present
    types = {q.type for q in repo.all()}
    assert types == {"equivalent", "compare", "add_subtract", "simplify"}
    repo.close()


def test_crud(tmp_db):
    repo = QuestionRepository(tmp_db, seed_path=None)
    from questions import Question
    q = Question(id="x1", prompt="p", type="simplify", options=["1/2", "2/4"], answer="1/2")
    repo.add(q)
    got = repo.get("x1")
    assert got.prompt == "p"
    assert got.get_options() == ["1/2", "2/4"]
    repo.update(Question(id="x1", prompt="p2", type="simplify", options=[], answer="1/3"))
    assert repo.get("x1").prompt == "p2"
    repo.delete("x1")
    assert repo.get("x1") is None
    repo.close()


def test_sample_count(tmp_db):
    repo = QuestionRepository(tmp_db)
    sample = repo.sample(10)
    assert len(sample) == 10
    repo.close()


def test_score_roundtrip(tmp_db):
    sr = ScoreRepository(tmp_db)
    sr.add_score("kid", 8, 10, 80.0, 2)
    sr.add_score("kid2", 10, 10, 100.0, 3)
    rows = sr.high_scores()
    assert len(rows) == 2
    # Highest percentage first
    assert rows[0]["username"] == "kid2"
    assert rows[0]["stars"] == 3
    sr.close()


def test_games_table_exists(tmp_db):
    import sqlite3
    repo = QuestionRepository(tmp_db, seed_path=None)
    conn = sqlite3.connect(tmp_db)
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='games'"
    )
    assert cur.fetchone() is not None
    conn.close()
    repo.close()
