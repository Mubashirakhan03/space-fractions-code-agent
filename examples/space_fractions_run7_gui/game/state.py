"""Game state machine: Playing / Paused / GameOver."""
from __future__ import annotations

from enum import Enum, auto
from typing import Dict, List


class GameState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    GAMEOVER = auto()


class GameStateMachine:
    """Enforces valid transitions from the class/state diagram.

    Transitions:
      [*] -> Playing
      Playing -> Paused   (pause())
      Paused  -> Playing  (resume())
      Playing -> GameOver (gameOver())
    """

    _ALLOWED: Dict[GameState, List[GameState]] = {
        GameState.PLAYING: [GameState.PAUSED, GameState.GAMEOVER],
        GameState.PAUSED: [GameState.PLAYING, GameState.GAMEOVER],
        GameState.GAMEOVER: [],
    }

    def __init__(self) -> None:
        self._state = GameState.PLAYING

    @property
    def state(self) -> GameState:
        return self._state

    def can(self, target: GameState) -> bool:
        return target in self._ALLOWED.get(self._state, [])

    def transition(self, target: GameState) -> None:
        if not self.can(target):
            raise ValueError(
                f"Invalid transition {self._state.name} -> {target.name}"
            )
        self._state = target

    def pause(self) -> None:
        self.transition(GameState.PAUSED)

    def resume(self) -> None:
        self.transition(GameState.PLAYING)

    def gameOver(self) -> None:
        self.transition(GameState.GAMEOVER)


__all__ = ["GameState", "GameStateMachine"]
