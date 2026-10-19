"""Pure domain model for the game (no tkinter imports)."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from questions.model import Question


@dataclass
class Game:
    """A single play session: a series of fraction questions with a score.

    Matches the UML `Game` class (id: string, score: int) plus the round data
    needed to actually drive a session.
    """

    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    score: int = 0
    questions: List[Question] = field(default_factory=list)
    current_index: int = 0
    correct_count: int = 0
    answered_count: int = 0

    def play(self) -> None:
        """Start/continue the game (state is driven by the state machine)."""
        # Domain placeholder that mirrors the UML method; real flow lives in
        # GameController which owns question progression.
        pass

    def viewScore(self) -> int:
        """Return the current score (number of correct answers)."""
        return self.score

    @property
    def current_question(self) -> Optional[Question]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def percentage(self) -> float:
        """Percentage correct (0..100)."""
        if self.answered_count == 0:
            return 0.0
        return 100.0 * self.correct_count / self.answered_count

    def stars(self) -> int:
        """Earn 1-3 stars from the final percentage."""
        p = self.percentage
        if p >= 85:
            return 3
        if p >= 60:
            return 2
        if p > 0:
            return 1
        return 0

    def is_finished(self) -> bool:
        return self.current_index >= self.total
