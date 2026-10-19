"""GameService — in-process equivalent of the gRPC GameService.play() RPC.

Implements SequenceDiagram1: User.play() -> Question.getPrompt() -> display
prompt -> submit answer -> check answer -> display result -> calculate score.
"""
from __future__ import annotations

from typing import List, Optional

from game.game import Game


class GameService:
    """Coordinates a game round given a list of questions."""

    def __init__(self, game_id: str, questions: List[object]) -> None:
        self.game_id = game_id
        self.game = Game(id=game_id, questions=list(questions))

    def play(self) -> Game:
        """Mirror gRPC Play(PlayRequest) -> PlayResponse (gameId)."""
        self.game.play()
        return self.game

    def current_prompt(self) -> Optional[str]:
        q = self.game.current_question
        return q.get_prompt() if q else None

    def current_options(self) -> List[str]:
        q = self.game.current_question
        return q.get_options() if q else []

    def submit(self, answer: str) -> bool:
        return self.game.submit_answer(answer)

    def view_score(self) -> int:
        return self.game.view_score()
