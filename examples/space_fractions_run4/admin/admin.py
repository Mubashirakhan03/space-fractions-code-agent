"""Admin entity (mirrors UML ``Admin``: id, username; updateQuestions).

The passcode gate maps the untraced ASR-2 (security) requirement to a
desktop-appropriate control.
"""
from dataclasses import dataclass
from typing import List

from questions.question import Question
from questions.repository import QuestionRepository

DEFAULT_PASSCODE = "admin"


@dataclass
class Admin:
    id: str = ""
    username: str = "admin"
    passcode: str = DEFAULT_PASSCODE
    repository: QuestionRepository = None

    def authenticate(self, passcode: str) -> bool:
        """Verify an entered passcode (string compare)."""
        return passcode == self.passcode

    def updateQuestions(self, questions: List[Question]) -> None:
        """Replace the entire question bank (SequenceDiagram2: update)."""
        if self.repository is None:
            raise ValueError("No repository attached to Admin")
        self.repository._questions = list(questions)

    def addQuestion(self, question: Question) -> None:
        if self.repository is None:
            raise ValueError("No repository attached to Admin")
        self.repository.add(question)

    def deleteQuestion(self, question_id: str) -> bool:
        if self.repository is None:
            raise ValueError("No repository attached to Admin")
        return self.repository.delete(question_id)
