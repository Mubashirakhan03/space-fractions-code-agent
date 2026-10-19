"""Question persistence: load from a JSON file (data/questions.json).

Also exposes in-memory add/update/delete for the admin use case.
"""
import json
import random
from pathlib import Path
from typing import List, Optional

from .question import Question, QuestionType

_PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _PACKAGE_DIR.parent
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "questions.json"

QTYPE_BY_NAME = {qt.value: qt for qt in QuestionType}


def _question_from_dict(d: dict) -> Question:
    return Question(
        id=str(d["id"]),
        prompt=d["prompt"],
        options=list(d.get("options", [])),
        qtype=QTYPE_BY_NAME[d.get("type", "equivalent")],
        answer=str(d.get("answer", "")),
        is_choice=bool(d.get("is_choice", True)),
    )


def _question_to_dict(q: Question) -> dict:
    return {
        "id": q.id,
        "prompt": q.prompt,
        "options": list(q.options),
        "type": q.qtype.value,
        "answer": q.answer,
        "is_choice": q.is_choice,
    }


class QuestionRepository:
    """Load, cache and mutate the question bank (stdin of admin use case)."""

    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = Path(data_file) if data_file else DEFAULT_DATA_FILE
        self._questions: List[Question] = []
        self.load()

    def load(self) -> None:
        with self.data_file.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        items = raw if isinstance(raw, list) else raw.get("questions", [])
        self._questions = [_question_from_dict(d) for d in items]

    def save(self) -> None:
        data = [_question_to_dict(q) for q in self._questions]
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with self.data_file.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    # --- queries -----------------------------------------------------------
    def all(self) -> List[Question]:
        return list(self._questions)

    def count(self) -> int:
        return len(self._questions)

    def get(self, question_id: str) -> Optional[Question]:
        for q in self._questions:
            if q.id == str(question_id):
                return q
        return None

    def sample(self, n: int, rng: Optional[random.Random] = None) -> List[Question]:
        """Return a random round of ``n`` questions (without repeats when possible)."""
        rng = rng or random
        pool = list(self._questions)
        rng.shuffle(pool)
        return pool[:n]

    # --- admin mutations ---------------------------------------------------
    def add(self, question: Question) -> None:
        self._questions.append(question)

    def update(self, question: Question) -> None:
        for i, q in enumerate(self._questions):
            if q.id == question.id:
                self._questions[i] = question
                return
        self._questions.append(question)

    def delete(self, question_id: str) -> bool:
        before = len(self._questions)
        self._questions = [q for q in self._questions if q.id != str(question_id)]
        return len(self._questions) != before
