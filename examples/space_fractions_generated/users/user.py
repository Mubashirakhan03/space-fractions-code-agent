"""User domain model (UserComponent).

Pure Python. Matches UML class User: id, username private;
playGame(game), viewScore(game) public.
"""
from __future__ import annotations

import uuid
from typing import List

from game.game import Game


class User:
    def __init__(self, username: str = ""):
        self._id = str(uuid.uuid4())
        self._username = username
        self._games: List[Game] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    def playGame(self, game: Game) -> None:
        """Start the given game for this user."""
        self._games.append(game)
        game.play()

    def viewScore(self, game: Game) -> int:
        """Return the score of a completed (or current) game."""
        return game.viewScore()

    @property
    def games(self) -> List[Game]:
        return list(self._games)
