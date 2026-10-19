"""The Game domain object (composition: Game *-- Question) and User relation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from game.game_state import GameState, GameStateError, transition
from game.scoring import POINTS_PER_CORRECT, percentage, stars_for


@dataclass
class Game:
    """Represents one round of Space Fractions (composition of Questions)."""

    id: str
    score: int = 0
    correct: int = 0
    answered: int = 0
    state: GameState = GameState.PLAYING
    questions: List[object] = field(default_factory=list)
    current_index: int = 0

    # -- state machine ----------------------------------------------------
    def pause(self) -> None:
        self.state = transition(self.state, "pause")

    def resume(self) -> None:
        self.state = transition(self.state, "resume")

    def game_over(self) -> None:
        self.state = transition(self.state, "game_over")

    def restart(self) -> None:
        self.state = transition(self.state, "restart")

    # -- play / ViewScore API (class diagram) -----------------------------
    def play(self) -> None:
        """Start (or restart) the round; mirrors design method Game.play()."""
        self.score = 0
        self.correct = 0
        self.answered = 0
        self.current_index = 0
        self.state = GameState.PLAYING

    def view_score(self) -> int:
        """Design method Game.viewScore()."""
        return self.score

    # -- question flow ----------------------------------------------------
    @property
    def current_question(self) -> Optional[object]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def submit_answer(self, answer: str) -> bool:
        """Submit an answer for the current question; returns correctness.

        Only allowed while Playing (pausing is between answers).
        """
        if self.state != GameState.PLAYING:
            raise GameStateError(
                f"Cannot submit while {self.state.value}"
            )
        q = self.current_question
        if q is None:
            raise GameStateError("No current question to answer")
        correct = q.check_answer(answer)
        self.answered += 1
        if correct:
            self.correct += 1
            self.score += POINTS_PER_CORRECT
        self.current_index += 1
        if self.current_index >= len(self.questions):
            self.game_over()
        return correct

    @property
    def percent(self) -> float:
        return percentage(self.correct, self.answered)

    @property
    def stars(self) -> int:
        return stars_for(self.percent)
