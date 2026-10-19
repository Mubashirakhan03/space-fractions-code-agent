"""Pytest fixtures."""
from __future__ import annotations

import random

import pytest

from questions.repository import QuestionRepository


@pytest.fixture
def repo(tmp_path):
    db = str(tmp_path / "test.db")
    seed = _seed_file(tmp_path)
    r = QuestionRepository(db, seed)
    yield r
    r.close()


def _seed_file(tmp_path):
    import json
    p = tmp_path / "seed.json"
    p.write_text(json.dumps([
        {"id": "a", "prompt": "Which is bigger: 1/2 or 1/4?", "correct": "1/2",
         "kind": "choice", "options": ["1/2", "1/4"]},
        {"id": "b", "prompt": "Add: 1/2 + 1/2", "correct": "1", "kind": "typed",
         "options": []},
    ]), encoding="utf-8")
    return str(p)


def make_choice_questions(n=4):
    from questions.question import Question
    return [
        Question(id=f"c{i}", prompt=f"Q{i}", correct="1/2", kind="choice",
                 options=["1/2", "1/4", "1/3", "2/5"])
        for i in range(n)
    ]
