"""Persistence tests: SQLite temporary file, seed auto-load, CRUD, scores."""
import json
import tempfile
from pathlib import Path

from question.question import Question, QuestionKind
from question.repository import QuestionRepository


def _repo():
    tmp = tempfile.mkdtemp()
    db = str(Path(tmp) / "test.db")
    return QuestionRepository(db_path=db)


def test_fresh_db_is_seeded_from_file():
    r = _repo()
    try:
        qs = r.list_all()
        assert len(qs) >= 20
        kinds = {q.kind for q in qs}
        assert QuestionKind.COMPARE in kinds
        assert QuestionKind.ADD in kinds
    finally:
        r.close()


def test_add_update_delete():
    r = _repo()
    try:
        q = Question(id="new1", prompt="What is 1/5 + 1/5?", correct="2/5",
                     options=["2/5", "1/4", "3/5"], kind=QuestionKind.ADD)
        assert r.add(q) == []
        assert any(x.id == "new1" for x in r.list_all())
        q2 = Question(id="new1", prompt="Updated?", correct="2/5",
                      options=["2/5", "1/4", "3/5"], kind=QuestionKind.ADD)
        assert r.update(q2) == []
        updated = [x for x in r.list_all() if x.id == "new1"][0]
        assert updated.prompt == "Updated?"
        assert r.delete("new1") is True
        assert r.delete("new1") is False
    finally:
        r.close()


def test_add_invalid_returns_errors():
    r = _repo()
    try:
        q = Question(id="", prompt="", correct="", options=[], kind=QuestionKind.ADD)
        errors = r.add(q)
        assert errors
    finally:
        r.close()


def test_record_and_list_scores():
    r = _repo()
    try:
        r.record_score("Player", 3, 5)
        scores = r.list_scores()
        assert len(scores) >= 1
        assert scores[0]["score"] == 3
        assert scores[0]["total"] == 5
    finally:
        r.close()
