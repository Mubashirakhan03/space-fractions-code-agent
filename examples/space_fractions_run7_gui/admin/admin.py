"""Admin entity (pure Python, no Tkinter)."""
from __future__ import annotations

from typing import List

from question.question import Question


class Admin:
    """Manages the question pool (Admin --* Question composition)."""

    def __init__(self, id: str, username: str):
        self._id = id
        self._username = username
        self._questions: List[Question] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    @property
    def questions(self) -> List[Question]:
        return self._questions

    # ---- method required by the class diagram ----
    def updateQuestions(self, questions: List[Question]) -> None:
        """Replace the administered question set."""
        self._questions = list(questions)

    def addQuestion(self, question: Question) -> List[str]:
        errors = question.validate()
        if errors:
            return errors
        self._questions.append(question)
        return []

    def removeQuestion(self, question_id: str) -> bool:
        for i, q in enumerate(self._questions):
            if q.id == question_id:
                del self._questions[i]
                return True
        return False


__all__ = ["Admin"]
