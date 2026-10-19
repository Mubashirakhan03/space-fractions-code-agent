"""Game state machine: [*] -> Playing; Playing <-> Paused; Playing -> GameOver.

Invalid transitions raise GameStateError.
"""
from __future__ import annotations

from enum import Enum


class GameState(Enum):
    PLAYING = "Playing"
    PAUSED = "Paused"
    GAME_OVER = "GameOver"


class GameStateError(Exception):
    """Raised when an invalid state transition is attempted."""


# Transition table: (from_state, trigger) -> to_state.  None from-state = initial.
_TRANSITIONS = {
    (None, "start"): GameState.PLAYING,
    (GameState.PLAYING, "pause"): GameState.PAUSED,
    (GameState.PAUSED, "resume"): GameState.PLAYING,
    (GameState.PLAYING, "game_over"): GameState.GAME_OVER,
    (GameState.GAME_OVER, "restart"): GameState.PLAYING,
}


def can_transition(from_state, trigger: str) -> bool:
    return (from_state, trigger) in _TRANSITIONS


def next_state(from_state, trigger: str) -> GameState:
    """Return the next state, raising GameStateError if the transition is invalid."""
    result = _TRANSITIONS.get((from_state, trigger))
    if result is None:
        raise GameStateError(
            f"Invalid transition: {trigger}() from {getattr(from_state, 'value', '<start>')}"
        )
    return result


def transition(from_state, trigger: str) -> GameState:
    """Apply a transition and return the new state."""
    return next_state(from_state, trigger)
