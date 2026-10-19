"""GameService: in-process facade for the sequence Play -> prompt -> answer -> result.

Adapted from the REST /play and gRPC GameService.Play contract (no network).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import List, Optional

from game.game import Game
from game.round import build_round
from game.state import GameState, GameStateMachine
from question.question import Question


@dataclass
class AnswerResult:
    correct: bool
    submitted: str
    expected: str
    prompt: str
    score: int
    total: int


class GameService:
    """Coordinates a game session and exposes state to the UI."""

    def __init__(self, pool: Optional[List[Question]] = None, default_total: int = 10):
        self._pool = list(pool or [])
        self._default_total = default_total
        self._game: Optional[Game] = None
        self._state = GameStateMachine()

    @property
    def state(self) -> GameState:
        return self._state.state

    @property
    def game(self) -> Optional[Game]:
        return self._game

    def play(self, total: Optional[int] = None) -> None:
        """Start a new game (adaptive openapi /play equivalent)."""
        n = total or self._default_total
        questions = build_round(self._pool, total=n)
        self._game = Game(id=str(uuid.uuid4()), questions=questions)
        self._state = GameStateMachine()  # starts Playing

    def pause(self) -> None:
        self._state.pause()

    def resume(self) -> None:
        self._state.resume()

    def current_question(self) -> Optional[Question]:
        if self._game is None:
            return None
        return self._game.current_question

    def submit(self, answer: str) -> Optional[AnswerResult]:
        """Submit an answer for the current question; returns result BEFORE advance."""
        if self._game is None:
            return None
        q = self._game.current_question
        if q is None:
            return None
        correct = q.checkAnswer(answer)
        # Build result using the just-submitted item's values BEFORE mutating state.
        result = AnswerResult(
            correct=correct,
            submitted=answer.strip(),
            expected=q.correct,
            prompt=q.prompt,
            score=self._game.viewScore(),
            total=self._game.total,
        )
        self._game.submitAnswer(answer)
        if self._game.is_finished:
            self._state.gameOver()
        if self._game.is_finished:
            result.score = self._game.viewScore()
        return result

    def view_score(self) -> int:
        return self._game.viewScore() if self._game else 0


__all__ = ["GameService", "AnswerResult"]
