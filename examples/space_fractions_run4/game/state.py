"""Game state machine: Playing <-> Paused -> GameOver.

Unspecified (invalid) transitions raise ValueError so that misuse is loud
and testable.
"""
from enum import Enum


class GameState(str, Enum):
    PLAYING = "Playing"
    PAUSED = "Paused"
    GAMEOVER = "GameOver"


_TRANSITIONS = {
    GameState.PLAYING: {GameState.PAUSED, GameState.GAMEOVER},
    GameState.PAUSED: {GameState.PLAYING},
    GameState.GAMEOVER: set(),
}


def can_transition(current: GameState, target: GameState) -> bool:
    """Whether ``current -> target`` is a valid state transition."""
    return target in _TRANSITIONS.get(current, set())
