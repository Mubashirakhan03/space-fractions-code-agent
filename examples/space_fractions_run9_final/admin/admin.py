"""Admin question repository (in-process equivalent of the update service)."""
from __future__ import annotations

from typing import List, Optional

from question.question import Question
from store.store import QuestionStore


class QuestionRepository:
    """Allows the Admin role to list/add/update/delete questions persistently."""

    def __init__(self, store: Optional[QuestionStore] = None) -> None:
        self.store = store

    def list_all(self) -> List[Question]:
        if self.store is None:
            return []
        return self.store.list_questions()

    def add(self, question: Question) -> Question:
        if self.store is not None:
            self.store.add_question(question)
        return question

    def update(self, question: Question) -> Question:
        if self.store is not None:
            self.store.update_question(question)
        return question

    def delete(self, question_id: str) -> bool:
        if self.store is not None:
            return self.store.delete_question(question_id)
        return False
