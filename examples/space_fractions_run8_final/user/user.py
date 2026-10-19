"""User domain model (End User)."""
from typing import List
import uuid

from game.game import Game


class User:
    def __init__(self, username: str = "player", uid: str = ""):
        self.id: str = uid or uuid.uuid4().hex[:12]
        self.username: str = username
        self.games: List[Game] = []  # User --* Game composition

    def playGame(self, game: Game) -> None:
        self.games.append(game)

    def viewScore(self, game: Game) -> int:
        return game.viewScore()
