"""Game state machine (Playing <=> Paused -> GameOver)."""
from __future__ import annotations

from enum import Enum


class GameState(Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, current: GameState, target: GameState):
        super().__init__(f"Invalid transition: {current.value} -> {target.value}")
        self.current = current
        self.target = target


# Valid transitions: [*]->Playing, Playing->Paused, Paused->Playing, Playing->GameOver
VALID_TRANSITIONS = {
    None: {GameState.PLAYING},
    GameState.PLAYING: {GameState.PAUSED, GameState.GAME_OVER},
    GameState.PAUSED: {GameState.PLAYING},
    GameState.GAME_OVER: set(),
}


def can_transition(current: "GameState | None", target: GameState) -> bool:
    return target in VALID_TRANSITIONS.get(current, set())
