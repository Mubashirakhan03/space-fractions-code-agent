"""Game domain logic and state machine (GameComponent).

Pure Python, no Tkinter — fully testable headless.
"""
from __future__ import annotations

from .state import GameState, InvalidTransitionError


class Game:
    """A single round of fraction questions."""

    def __init__(self, game_id: str = ""):
        self._id: str = game_id
        self._score: int = 0
        self._total: int = 0
        self._state: GameState = GameState.PLAYING

    @property
    def id(self) -> str:
        return self._id

    @property
    def score(self) -> int:
        return self._score

    @property
    def total(self) -> int:
        return self._total

    @property
    def state(self) -> GameState:
        return self._state

    def play(self) -> None:
        """Start/resume playing."""
        self._state = GameState.PLAYING

    def pause(self) -> None:
        if self._state is not GameState.PLAYING:
            raise InvalidTransitionError(self._state, GameState.PAUSED)
        self._state = GameState.PAUSED

    def resume(self) -> None:
        if self._state is not GameState.PAUSED:
            raise InvalidTransitionError(self._state, GameState.PLAYING)
        self._state = GameState.PLAYING

    def game_over(self) -> None:
        if self._state is not GameState.PLAYING:
            raise InvalidTransitionError(self._state, GameState.GAME_OVER)
        self._state = GameState.GAME_OVER

    def record_answer(self, correct: bool) -> None:
        """Record one answered question and update the score."""
        self._total += 1
        if correct:
            self._score += 1

    def view_score(self) -> int:
        return self._score

    def percentage(self) -> float:
        if self._total == 0:
            return 0.0
        return round(self._score / self._total * 100, 2)

    def stars(self) -> int:
        """1-3 stars by percentage."""
        pct = self.percentage()
        if pct >= 90:
            return 3
        if pct >= 75:
            return 2
        if pct >= 50:
            return 1
        return 0

    def to_state(self) -> dict:
        return {
            "id": self._id,
            "score": self._score,
            "total": self._total,
            "state": self._state.value,
        }

    @classmethod
    def from_state(cls, data: dict) -> "Game":
        game = cls(str(data.get("id", "")))
        game._score = int(data.get("score", 0))
        game._total = int(data.get("total", 0))
        game._state = GameState(data.get("state", "playing"))
        return game
