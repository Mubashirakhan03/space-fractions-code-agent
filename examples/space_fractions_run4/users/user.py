"""User entity (mirrors UML ``User``: id, username; playGame, viewScore)."""
from dataclasses import dataclass

from game.game import Game


@dataclass
class User:
    id: str
    username: str = ""

    def playGame(self, game: Game) -> None:
        game.play()

    def viewScore(self, game: Game) -> int:
        return game.viewScore()
