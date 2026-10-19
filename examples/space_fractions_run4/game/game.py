"""The Game aggregate: state machine, scoring, and per-question flow.

Mirrors the UML ``Game`` class (id, score; play(), viewScore()) while adding
the pause/resume/gameOver transitions from the state diagram.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from game.state import GameState, can_transition
from questions.question import Question

ROUND_SIZE = 10


@dataclass
class GameResult:
    """Final result of a finished game."""
    score: int
    total: int
    correct: int
    percentage: int
    stars: int


@dataclass
class Game:
    """A single play-through of ``ROUND_SIZE`` questions."""
    id: str = ""
    score: int = 0
    _state: GameState = GameState.PLAYING
    questions: List[Question] = field(default_factory=list)
    current_index: int = 0
    correct_count: int = 0

    # --- state machine -----------------------------------------------------
    @property
    def state(self) -> GameState:
        return self._state

    def _transition(self, target: GameState) -> None:
        if not can_transition(self._state, target):
            raise ValueError(
                f"Invalid transition '{self._state.value}' -> '{target.value}'"
            )
        self._state = target

    def pause(self) -> None:
        self._transition(GameState.PAUSED)

    def resume(self) -> None:
        self._transition(GameState.PLAYING)

    def gameOver(self) -> None:
        self._transition(GameState.GAMEOVER)

    # --- UML methods -------------------------------------------------------
    def play(self) -> None:
        """Start (or continue) the round."""
        self._state = GameState.PLAYING

    def viewScore(self) -> int:
        return self.score

    # --- round flow --------------------------------------------------------
    @property
    def current_question(self) -> Optional[Question]:
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def question_number(self) -> int:
        """1-based number of the question being answered."""
        return min(self.current_index + 1, self.total_questions)

    def submit(self, answer: Optional[str]) -> Tuple[bool, str]:
        """Submit the answer for the current question; advance to next.

        Returns ``(correct, expected_canonical)`` computed BEFORE advancing.
        Raises ValueError if the game is not currently Playing.
        """
        if self._state is not GameState.PLAYING:
            raise ValueError("Cannot submit while paused or over")
        q = self.current_question
        if q is None:
            raise ValueError("No current question to answer")
        correct, expected = q.checkAnswer(answer)
        if correct:
            self.score += 1
            self.correct_count += 1
        self.current_index += 1
        if self.current_index >= len(self.questions):
            self._state = GameState.GAMEOVER
        return correct, expected

    def result(self) -> GameResult:
        total = self.total_questions
        pct = 0 if total == 0 else round(100 * self.score / total)
        if pct >= 95:
            stars = 3
        elif pct >= 80:
            stars = 2
        elif pct >= 60:
            stars = 1
        else:
            stars = 0
        return GameResult(
            score=self.score,
            total=total,
            correct=self.correct_count,
            percentage=pct,
            stars=stars,
        )
