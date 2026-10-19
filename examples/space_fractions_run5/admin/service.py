"""Admin service: add / edit / delete questions (Update Questions use case)."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List

from questions.model import Question


@dataclass
class Admin:
    """Matches UML `Admin` (id, username; updateQuestions)."""

    username: str = "admin"
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def updateQuestions(self, questions: List[Question]) -> None:
        """Replace the managed question set (composition relationship)."""
        self._questions = list(questions)

    def add_question(self, question: Question) -> None:
        if not hasattr(self, "_questions"):
            self._questions = []
        self._questions.append(question)

    def remove_question(self, question_id: str) -> bool:
        if not hasattr(self, "_questions"):
            return False
        before = len(self._questions)
        self._questions = [q for q in self._questions if q.id != question_id]
        return len(self._questions) != before

    def replace_question(self, question: Question) -> None:
        """Replace a question matching by id, or append if absent."""
        if not hasattr(self, "_questions"):
            self._questions = []
        for i, q in enumerate(self._questions):
            if q.id == question.id:
                self._questions[i] = question
                return
        self._questions.append(question)

    @property
    def questions(self) -> List[Question]:
        return list(getattr(self, "_questions", []))
