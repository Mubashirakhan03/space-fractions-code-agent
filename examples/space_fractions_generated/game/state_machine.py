"""Game state machine: Playing -> Paused -> ... -> GameOver.

Invalid transitions raise StateError (pure Python, headless-testable).
"""
from __future__ import annotations

from enum import Enum, auto


class StateError(Exception):
    """Raised when a transition is not allowed in the current state."""


class GameState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


_TRANSITIONS = {
    GameState.PLAYING: {"pause": GameState.PAUSED, "game_over": GameState.GAME_OVER},
    GameState.PAUSED: {"resume": GameState.PLAYING, "game_over": GameState.GAME_OVER},
    GameState.GAME_OVER: {},
}


class GameStateMachine:
    def __init__(self, initial: GameState = GameState.PLAYING):
        self._state = initial

    @property
    def state(self) -> GameState:
        return self._state

    def _apply(self, trigger: str) -> None:
        allowed = _TRANSITIONS.get(self._state, {})
        if trigger not in allowed:
            raise StateError(
                f"Cannot {trigger} from state {self._state.name}")
        self._state = allowed[trigger]

    def pause(self) -> None:
        self._apply("pause")

    def resume(self) -> None:
        self._apply("resume")

    def game_over(self) -> None:
        self._apply("game_over")
