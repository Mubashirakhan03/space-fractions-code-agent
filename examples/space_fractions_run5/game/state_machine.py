"""State machine for a game session: Playing <-> Paused -> GameOver."""
from __future__ import annotations

from enum import Enum, auto


class InvalidTransitionError(Exception):
    """Raised when a state transition is not allowed by the state diagram."""


class GameState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class GameStateMachine:
    """Implements the Playing/Paused/GameOver state diagram.

    Transitions:
      [*] -> Playing       (start)
      Playing -> Paused    (pause)
      Paused -> Playing    (resume)
      Playing -> GameOver  (gameOver)
    Any other transition raises InvalidTransitionError.
    """

    def __init__(self) -> None:
        self.state: GameState = GameState.PLAYING

    def _require(self, allowed: set, trigger: str) -> None:
        if self.state not in allowed:
            raise InvalidTransitionError(
                f"Cannot {trigger}() from {self.state.name} state."
            )

    @property
    def is_playing(self) -> bool:
        return self.state is GameState.PLAYING

    @property
    def is_paused(self) -> bool:
        return self.state is GameState.PAUSED

    @property
    def is_game_over(self) -> bool:
        return self.state is GameState.GAME_OVER

    def pause(self) -> None:
        self._require({GameState.PLAYING}, "pause")
        self.state = GameState.PAUSED

    def resume(self) -> None:
        self._require({GameState.PAUSED}, "resume")
        self.state = GameState.PLAYING

    def game_over(self) -> None:
        self._require({GameState.PLAYING}, "gameOver")
        self.state = GameState.GAME_OVER
