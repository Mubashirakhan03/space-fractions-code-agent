"""Tests for persistence with a temporary SQLite file."""
import tempfile
from pathlib import Path

from questions.repository import QuestionRepository
from scores.repository import ScoreRepository
from questions.model import Question


def test_question_repository_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "test.db"
        repo = QuestionRepository(db)
        qs = [
            Question(prompt="half?", answer="1/2", options=["1/2", "1/3"],
                     qtype="choice", id="q1"),
            Question(prompt="simplify", answer="1/2", qtype="simplify",
                     id="q2"),
        ]
        repo.replace_all(qs)
        loaded = repo.all()
        assert len(loaded) == 2
        assert loaded[0].getOptions() == ["1/2", "1/3"]
        assert repo.get("q2").prompt == "simplify"


def test_question_repository_upsert_and_delete():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "test.db"
        repo = QuestionRepository(db)
        q = Question(prompt="p", answer="a", id="q1")
        repo.upsert(q)
        assert repo.get("q1") is not None
        q.prompt = "edited"
        repo.upsert(q)
        assert repo.get("q1").prompt == "edited"
        assert repo.delete("q1")
        assert repo.get("q1") is None
        assert not repo.delete("q1")


def test_question_repository_seed_from_file():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "test.db"
        repo = QuestionRepository(db)
        seed = Path(d) / "seed.json"
        seed.write_text(
            '{"questions": [{"prompt":"p","answer":"a","options":[],'
            '"qtype":"simplify","id":"q1"}]}'
        )
        repo.seed_from_file(seed)
        assert len(repo.all()) == 1


def test_score_repository_top():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "test.db"
        repo = ScoreRepository(db)
        repo.save("alice", 9, 10, 90.0)
        repo.save("bob", 5, 10, 50.0)
        repo.save("carol", 8, 10, 100.0)
        top = repo.top(10)
        assert top[0][0] == "carol"
        assert top[0][3] == 100.0
        assert top[1][0] == "alice"
        assert top[2][0] == "bob"
