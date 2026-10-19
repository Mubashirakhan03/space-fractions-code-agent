"""Game state machine: Playing / Paused / GameOver.

Valid transitions mirror spec.domain_model.transitions.
"""
from enum import Enum


class GameState(str, Enum):
    PLAYING = "Playing"
    PAUSED = "Paused"
    GAMEOVER = "GameOver"


class InvalidTransition(Exception):
    pass


class GameStateMachine:
    _TRANSITIONS = {
        (GameState.PLAYING, "pause"): GameState.PAUSED,
        (GameState.PAUSED, "resume"): GameState.PLAYING,
        (GameState.PLAYING, "game_over"): GameState.GAMEOVER,
        (GameState.PAUSED, "game_over"): GameState.GAMEOVER,
    }

    def __init__(self):
        self.state: GameState = GameState.PLAYING

    def pause(self) -> None:
        self._apply("pause")

    def resume(self) -> None:
        self._apply("resume")

    def game_over(self) -> None:
        self._apply("game_over")

    def _apply(self, trigger: str) -> None:
        nxt = self._TRANSITIONS.get((self.state, trigger))
        if nxt is None:
            raise InvalidTransition(
                f"Cannot {trigger} from state {self.state.value}"
            )
        self.state = nxt

    def can(self, trigger: str) -> bool:
        return (self.state, trigger) in self._TRANSITIONS
