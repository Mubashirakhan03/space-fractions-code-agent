"""GameService: coordinates a round, adapting the /play API + proto service."""
from typing import List, Optional
from random import Random

from game.game import Game
from game.generator import FractionGenerator
from question.question import Question


class GameService:
    """In-process replacement for the REST /play endpoint and GameService rpc."""

    def __init__(self, seed_pool: List[Question], generator: FractionGenerator = None):
        self.seed_pool: List[Question] = list(seed_pool)
        self.generator = generator or FractionGenerator()
        self._rng = Random()

    def build_round(self, count: int = 10, seed=None) -> Game:
        """Draw randomly from the pool AND generate new items, then shuffle.

        Two rounds therefore differ (seeded random). Admin-added questions in the
        pool can appear.
        """
        rng = Random(seed) if seed is not None else self._rng
        n_generated = max(0, count // 2)
        questions = list(self.seed_pool)
        questions.extend(self.generator.generate(n_generated, seed=rng.random()))
        rng.shuffle(questions)
        questions = questions[:count]
        if not questions:
            questions = self.generator.generate(count, seed=rng.random())
        return Game(questions)

    def play(self, game_id: int = 0) -> dict:
        # Keeps the proto 'Play' shape (gameId in/out) in a local form.
        game = self.build_round()
        return {"gameId": game.id, "game": game}
