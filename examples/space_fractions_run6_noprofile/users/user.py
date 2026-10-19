"""User models (domain, tkinter-free)."""
from __future__ import annotations

from dataclasses import dataclass

from game.game import Game


@dataclass
class User:
    """End-user profile (UML class User)."""

    id: str
    username: str

    def play_game(self, game: Game) -> None:
        """Start/continue playing a round (ensures it is playable)."""
        game.play()

    def view_score(self, game: Game) -> int:
        """Return the game score."""
        return game.view_score()
