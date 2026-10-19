"""Design class Admin (id, username; updateQuestions)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from questions.question import Question


@dataclass
class Admin:
    id: str
    username: str
    questions: List[Question] = field(default_factory=list)

    def update_questions(self, questions: List[Question]) -> None:
        """Design method Admin.updateQuestions(questions: List<Question>)."""
        self.questions = list(questions)
