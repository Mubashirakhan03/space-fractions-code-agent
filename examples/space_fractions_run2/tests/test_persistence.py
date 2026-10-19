"""Persistence tests: SQLite schema, seed loading, question CRUD, scores."""
import json
import sqlite3

from questions.repository import QuestionRepository


def test_seed_has_twenty_plus_questions():
    repo = QuestionRepository(seed_path="data/questions.json")
    qs = repo.load_seed()
    assert len(qs) >= 20
    types = {q.qtype.value for q in qs}
    assert {"equivalent", "compare", "add_subtract", "simplify"} <= types


def test_seed_database_then_load(tmp_path):
    db = str(tmp_path / "db.sqlite")
    repo = QuestionRepository(db_path=db, seed_path="data/questions.json")
    # create the schema first
    conn = sqlite3.connect(db)
    with open("sql/schema.sql", "r", encoding="utf-8") as fh:
        conn.executescript(fh.read())
    conn.commit()
    conn.close()
    repo.seed_database()
    qs = repo.load_all()
    assert len(qs) >= 20


def test_add_update_delete(tmp_path):
    db = str(tmp_path / "db.sqlite")
    repo = QuestionRepository(db_path=db, seed_path="data/questions.json")
    conn = sqlite3.connect(db)
    with open("sql/schema.sql", "r", encoding="utf-8") as fh:
        conn.executescript(fh.read())
    conn.commit()
    conn.close()

    from questions.question import Question
    q = Question(id="qtest", prompt="test", answer="1/2")
    repo.add(q)
    assert any(x.id == "qtest" for x in repo.load_all())

    q2 = Question(id="qtest", prompt="test2", answer="2/4")
    repo.update(q2)
    loaded = {x.id: x for x in repo.load_all()}
    assert loaded["qtest"].getPrompt() == "test2"

    repo.delete("qtest")
    assert all(x.id != "qtest" for x in repo.load_all())


def test_schema_tables_exist(tmp_path):
    db = str(tmp_path / "db.sqlite")
    conn = sqlite3.connect(db)
    with open("sql/schema.sql", "r", encoding="utf-8") as fh:
        conn.executescript(fh.read())
    conn.commit()
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"games", "questions", "scores"} <= tables
