"""Design class User (id, username; playGame, viewScore)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class User:
    id: str
    username: str
    games: List[object] = field(default_factory=list)

    def play_game(self, game) -> None:
        """Design method User.playGame(game: Game)."""
        self.games.append(game)
        game.play()

    def view_score(self, game) -> int:
        """Design method User.viewScore(game: Game)."""
        return game.view_score()
