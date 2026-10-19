"""Game domain logic for Space Fractions (pure Python, no Tkinter)."""
from .state import GameState
from .game import Game, GameResult

__all__ = ["Game", "GameResult", "GameState"]
