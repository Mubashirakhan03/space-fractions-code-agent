"""User (End User) entity (pure Python, no Tkinter)."""
from __future__ import annotations

from game.game import Game


class User:
    """A local player; owns one game at a time (User --* Game composition)."""

    def __init__(self, id: str, username: str):
        self._id = id
        self._username = username
        self._current_game: Game | None = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    @property
    def current_game(self) -> Game | None:
        return self._current_game

    # ---- methods required by the class diagram ----
    def playGame(self, game: Game) -> None:
        self._current_game = game
        game.play()

    def viewScore(self, game: Game) -> int:
        return game.viewScore()


__all__ = ["User"]
