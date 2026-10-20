"""Game domain entity and GameService (the in-process RPC-equivalent)."""
from __future__ import annotations

import random
from typing import List, Optional

from question.question import Question
from game.state_machine import GameStateMachine, State
from game.question_generator import generate_questions


class Game:
    """Spec's Game class: id, score; play() and viewScore()."""

    def __init__(self, game_id: str = "") -> None:
        self._id = game_id or "game-1"
        self._score = 0

    @property
    def id(self) -> str:
        return self._id

    @property
    def score(self) -> int:
        return self._score

    def play(self) -> None:
        """Kick off a round (mostly a no-op here; state lives in GameService)."""

    def view_score(self) -> int:
        return self._score


class Round:
    """A single round: a shuffled series of fraction questions with scoring."""

    def __init__(self, questions: List[Question], rng: Optional[random.Random] = None) -> None:
        self.questions = list(questions)
        self._rng = rng or random.Random()
        self._rng.shuffle(self.questions)
        self.index = 0
        self.correct = 0
        self.wrong = 0
        self.state_machine = GameStateMachine(State.PLAYING)
        self.finished = False

    @property
    def current(self) -> Optional[Question]:
        if self.index < len(self.questions):
            return self.questions[self.index]
        return None

    @property
    def remaining(self) -> int:
        return max(0, len(self.questions) - self.index)

    @property
    def total(self) -> int:
        return len(self.questions)

    def submit(self, answer: str) -> bool:
        """Grade the current question; returns whether the round just ended.

        The correct answer is computed BEFORE advancing state so callers can
        report the right item.
        """
        if self.state_machine.state is State.GAME_OVER or self.finished:
            return True
        q = self.current
        if q is None:
            self._finish()
            return True
        self.last_question = q
        self.last_correct_answer = q.correct_value
        correct = q.check_answer(answer)
        self.last_was_correct = correct
        if correct:
            self.correct += 1
        else:
            self.wrong += 1
        self.index += 1
        if self.index >= len(self.questions):
            self._finish()
            return True
        return False

    def _finish(self) -> None:
        self.finished = True
        if self.state_machine.state is State.PLAYING:
            self.state_machine.game_over()

    @property
    def score(self) -> int:
        return self.correct


class GameService:
    """In-process equivalent of the REST/gRPC GameService.

    `play()` returns a started round (the 'PlayResponse'); rounds draw at random
    from the whole pool (stored + generated) and shuffle their order.
    """

    def __init__(self, pool_questions: Optional[List[Question]] = None,
                 rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()
        self.pool = pool_questions or []
        self.current_round: Optional[Round] = None
        self.high_score = 0

    def play(self, question_count: int = 10) -> Round:
        stored = [q for q in self.pool]
        generated = generate_questions(self._rng, count=question_count)
        combined = self._rng.sample(stored, min(len(stored), question_count)) + generated
        if len(combined) > question_count:
            combined = combined[:question_count]
        elif len(combined) < question_count:
            combined = combined + generate_questions(
                self._rng, count=question_count - len(combined)
            )
        self.current_round = Round(combined, self._rng)
        return self.current_round

    def view_score(self) -> int:
        return self.current_round.correct if self.current_round else 0

    def finish_round(self) -> None:
        if self.current_round:
            self.high_score = max(self.high_score, self.current_round.correct)
