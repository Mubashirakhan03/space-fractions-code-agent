"""Admin domain class (AdminComponent): update questions."""
from __future__ import annotations

from typing import List

from questions.question import Question
from questions.repository import QuestionRepository


class Admin:
    """Administrator who can add / edit / delete questions."""

    DEFAULT_PIN = "space-admin"

    def __init__(self, username: str = "admin", admin_id: str = "admin-1"):
        self._id: str = admin_id
        self._username: str = username

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    @staticmethod
    def verify_pin(pin: str) -> bool:
        return pin == Admin.DEFAULT_PIN

    def update_questions(
        self, repository: QuestionRepository, questions: List[Question]
    ) -> None:
        for q in questions:
            repository.update(q)

    def add_question(self, repository: QuestionRepository, question: Question) -> None:
        repository.add(question)

    def delete_question(self, repository: QuestionRepository, question_id: str) -> None:
        repository.delete(question_id)
