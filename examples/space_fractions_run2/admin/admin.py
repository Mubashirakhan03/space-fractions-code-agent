"""Admin domain model (AdminComponent).

Pure Python. Matches UML class Admin: id, username private;
updateQuestions(questions) public.
"""
from __future__ import annotations

import uuid
from typing import List

from questions.question import Question
from questions.repository import QuestionRepository


class Admin:
    def __init__(self, username: str = "Admin", repository: QuestionRepository = None):
        self._id = str(uuid.uuid4())
        self._username = username
        self._repository = repository or QuestionRepository()

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    def updateQuestions(self, questions: List[Question]) -> None:
        """Persist the provided questions (create or update)."""
        for q in questions:
            self._repository.update(q)

    def add_question(self, question: Question) -> None:
        self._repository.add(question)

    def delete_question(self, question_id: str) -> None:
        self._repository.delete(question_id)

    def list_questions(self) -> List[Question]:
        return self._repository.load_all()
