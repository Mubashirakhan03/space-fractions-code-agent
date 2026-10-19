"""Application controller: wires game, repository and session."""
from __future__ import annotations

import random
from typing import List, Optional

from game.game import Game
from game.question_generator import generate_questions
from questions.question import Question
from questions.repository import QuestionRepository
from users.admin import Admin
from users.user import User


class Controller:
    """In-process façade for the Game/Question/User/Admin components."""

    QUESTIONS_PER_ROUND = 8

    def __init__(self, repo: QuestionRepository, rng: Optional[random.Random] = None) -> None:
        self.repo = repo
        self._rng = rng or random.Random()
        self.current_user: Optional[object] = None
        self._game: Optional[Game] = None
        self._pool: List[Question] = []

    # -- user session ------------------------------------------------------
    def login(self, username: str, role: str) -> object:
        if role == "admin":
            self.current_user = Admin(id=f"admin-{username}", username=username)
        else:
            self.current_user = User(id=f"user-{username}", username=username)
        return self.current_user

    @property
    def is_admin(self) -> bool:
        return isinstance(self.current_user, Admin)

    # -- game --------------------------------------------------------------
    def new_game(self) -> Game:
        """Build a round: random draw from seed + admin pool, shuffled, plus
        fresh generated (computable) questions."""
        pool = list(self.repo.list_all())
        generated = generate_questions(4, self._rng)
        combined = pool + generated
        self._rng.shuffle(combined)
        if len(combined) > self.QUESTIONS_PER_ROUND:
            combined = combined[: self.QUESTIONS_PER_ROUND]
        self._game = Game(id=str(random_round_id(self._rng)), questions=combined, rng=self._rng)
        return self._game

    @property
    def game(self) -> Optional[Game]:
        return self._game

    # -- admin -------------------------------------------------------------
    def add_question(self, question: Question) -> None:
        self.repo.insert(question)

    def delete_question(self, question_id: str) -> None:
        self.repo.delete(question_id)

    def all_questions(self) -> List[Question]:
        return self.repo.list_all()

    def save_score(self) -> None:
        """Persist a finished round to the games table (data durability)."""
        if self._game is None or self._game.state.value != "GameOver":
            return
        from datetime import datetime
        import sqlite3
        conn = sqlite3.connect(self.repo._db_path)
        try:
            conn.execute(
                "INSERT OR REPLACE INTO games (id, game_state, score, played_at) VALUES (?, ?, ?, ?)",
                (self._game._id, "GameOver", self._game.view_score(),
                 datetime.now().isoformat()),
            )
            conn.commit()
        finally:
            conn.close()


def random_round_id(rng: random.Random) -> str:
    return "round-%d" % rng.randrange(1_000_000_000)
