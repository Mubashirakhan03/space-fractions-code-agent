"""User domain class (UserComponent) and score persistence."""
from __future__ import annotations

from game.game import Game


class User:
    """A player (End User)."""

    def __init__(self, username: str, user_id: str = ""):
        self._id: str = user_id
        self._username: str = username
        self._game: Game | None = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    def play_game(self, game: Game) -> None:
        self._game = game
        game.play()

    def view_score(self, game: Game | None = None) -> int:
        g = game if game is not None else self._game
        if g is None:
            return 0
        return g.view_score()
