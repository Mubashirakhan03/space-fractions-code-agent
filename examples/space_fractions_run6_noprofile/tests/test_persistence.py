"""Persistence and repository tests (temporary SQLite file)."""
import pytest

from questions.question import Question


def test_seeded_on_empty_db(repo):
    assert repo.count() >= 2


def test_list_all_returns_questions(repo):
    qs = repo.list_all()
    assert all(isinstance(q, Question) for q in qs)


def test_insert_update_delete(repo):
    q = Question(id="x", prompt="New", correct="1/2", kind="choice",
                 options=["1/2", "1/4"])
    repo.insert(q)
    assert repo.get("x") is not None
    q2 = Question(id="x", prompt="Changed", correct="1/2", kind="choice",
                  options=["1/2", "1/4"])
    repo.update(q2)
    assert repo.get("x").prompt == "Changed"
    repo.delete("x")
    assert repo.get("x") is None


def test_delete_missing_raises(repo):
    with pytest.raises(KeyError):
        repo.delete("nope")


def test_replace_all(repo):
    qs = [Question(id="y1", prompt="A", correct="1/2", kind="choice",
                   options=["1/2", "1/4"]),
          Question(id="y2", prompt="B", correct="1", kind="typed", options=[])]
    repo.replace_all(qs)
    assert repo.count() == 2
    assert repo.get("y1").prompt == "A"
