"""User model: the local player identity."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from game.models import Game


@dataclass
class User:
    """A player. Matches UML `User` (id, username; playGame, viewScore)."""

    username: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def playGame(self, game: Game) -> None:
        """Associate this user with a game (composition relationship)."""
        game.id = game.id or uuid.uuid4().hex

    def viewScore(self, game: Game) -> int:
        return game.viewScore()
