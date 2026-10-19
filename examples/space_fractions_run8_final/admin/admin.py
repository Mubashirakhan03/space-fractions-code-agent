"""Admin domain model + question management (Update Questions use case)."""
from typing import List
import uuid

from question.question import Question


class Admin:
    def __init__(self, username: str = "admin", uid: str = ""):
        self.id: str = uid or uuid.uuid4().hex[:12]
        self.username: str = username
        self.questions: List[Question] = []  # Admin --* Question composition

    def updateQuestions(self, questions: List[Question]) -> None:
        self.questions = list(questions)

    def addQuestion(self, q: Question) -> None:
        self.questions.append(q)
