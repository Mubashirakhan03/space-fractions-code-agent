"""Game entity (pure Python, no Tkinter)."""
from __future__ import annotations

from typing import List, Optional

from question.question import Question


class Game:
    """A single play session: the ordered questions and the running score.

    Class diagram: Game --* Question (composition).
    """

    def __init__(self, id: str, questions: Optional[List[Question]] = None):
        self._id = id
        self._questions: List[Question] = list(questions or [])
        self._score = 0
        self._answered = 0
        self._current_index = 0

    # ---- methods required by the class diagram ----
    def play(self) -> None:
        """Advance is implicit; this models beginning/interacting with the game."""
        # Kept for spec fidelity; actual advancement is via submitAnswer().
        return None

    def viewScore(self) -> int:
        return self._score

    # ---- additional behaviour ----
    @property
    def id(self) -> str:
        return self._id

    @property
    def questions(self) -> List[Question]:
        return self._questions

    @property
    def total(self) -> int:
        return len(self._questions)

    @property
    def answered(self) -> int:
        return self._answered

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def current_question(self) -> Optional[Question]:
        if 0 <= self._current_index < len(self._questions):
            return self._questions[self._current_index]
        return None

    @property
    def is_finished(self) -> bool:
        return self._current_index >= len(self._questions)

    def submitAnswer(self, submitted: str) -> bool:
        """Record an answer for the current question and advance.

        Returns whether the answer was correct.
        """
        if self.is_finished or self.current_question is None:
            return False
        correct = self.current_question.checkAnswer(submitted)
        self._answered += 1
        if correct:
            self._score += 1
        self._current_index += 1
        return correct

    def score_ratio(self) -> float:
        if self._answered == 0:
            return 0.0
        return self._score / self._answered


__all__ = ["Game"]
