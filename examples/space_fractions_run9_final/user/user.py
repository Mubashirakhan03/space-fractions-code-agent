"""User and Admin domain entities.

User --* Game composition; Admin --* Question composition.
"""
from __future__ import annotations

from typing import List

from game.game import Game
from question.question import Question


class User:
    """Spec's User class: id, username; playGame() and viewScore()."""

    def __init__(self, user_id: str = "", username: str = "player") -> None:
        self._id = user_id or "user-1"
        self._username = username
        self.games: List[Game] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    def play_game(self, game: Game) -> None:
        self.games.append(game)
        game.play()

    def view_score(self, game: Game) -> int:
        return game.view_score()

    # Spec naming
    playGame = play_game
    viewScore = view_score


class Admin:
    """Spec's Admin class: id, username; updateQuestions()."""

    def __init__(self, user_id: str = "", username: str = "admin") -> None:
        self._id = user_id or "admin-1"
        self._username = username
        self.questions: List[Question] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    def set_questions(self, questions: List[Question]) -> None:
        self.questions = list(questions)

    def update_questions(self, questions: List[Question]) -> None:
        self.questions = list(questions)

    # Spec naming
    updateQuestions = update_questions
