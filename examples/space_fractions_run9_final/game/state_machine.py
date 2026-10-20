"""State machine for a Space Fractions game round.

States: Playing, Paused, GameOver.
Transitions: [*] -> Playing; Playing -> Paused (pause());
             Paused -> Playing (resume()); Playing -> GameOver (gameOver()).
"""
from __future__ import annotations

from enum import Enum


class State(Enum):
    PLAYING = "Playing"
    PAUSED = "Paused"
    GAME_OVER = "GameOver"


class InvalidTransitionError(Exception):
    """Raised when a transition is attempted from an invalid state."""


class GameStateMachine:
    """Finite state machine tracking lifecycle of a game round."""

    def __init__(self, initial_state: State = State.PLAYING) -> None:
        self._state = initial_state

    @property
    def state(self) -> State:
        return self._state

    def pause(self) -> None:
        if self._state is not State.PLAYING:
            raise InvalidTransitionError(
                f"Cannot pause from state {self._state.value}"
            )
        self._state = State.PAUSED

    def resume(self) -> None:
        if self._state is not State.PAUSED:
            raise InvalidTransitionError(
                f"Cannot resume from state {self._state.value}"
            )
        self._state = State.PLAYING

    def game_over(self) -> None:
        if self._state is not State.PLAYING:
            raise InvalidTransitionError(
                f"Cannot finish from state {self._state.value}"
            )
        self._state = State.GAME_OVER

    def transition(self, trigger: str) -> State:
        """Dispatch by trigger name (pause/resume/gameOver) and return new state."""
        if trigger == "pause":
            self.pause()
        elif trigger == "resume":
            self.resume()
        elif trigger == "gameOver":
            self.game_over()
        else:
            raise InvalidTransitionError(f"Unknown trigger {trigger!r}")
        return self._state
