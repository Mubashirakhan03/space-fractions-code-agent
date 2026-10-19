"""Game state machine states."""
from enum import Enum


class GameState(Enum):
    """Lifecycle states of a game round."""

    PLAYING = "Playing"
    PAUSED = "Paused"
    GAMEOVER = "GameOver"
