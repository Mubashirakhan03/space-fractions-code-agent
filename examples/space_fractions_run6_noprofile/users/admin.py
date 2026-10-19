"""Admin model (domain, tkinter-free)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from questions.question import Question
from questions.repository import QuestionRepository


@dataclass
class Admin:
    """Administrator profile (UML class Admin)."""

    id: str
    username: str

    def update_questions(self, questions: List[Question], repo: QuestionRepository) -> None:
        """Replace the persisted question set with ``questions``.

        SequenceDiagram2: Admin -> Question update() -> return success.
        """
        repo.replace_all(questions)
