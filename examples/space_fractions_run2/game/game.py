"""Game domain logic: score tracking, question flow, result summary.

Pure Python (no Tkinter). Matches UML class Game (id, score private;
play(), viewScore() public). Holds a composition of Question objects.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from questions.question import Question
from .state_machine import GameState, GameStateMachine, StateError

STAR_THRESHOLDS = ((90, 3), (70, 2), (50, 1))


def stars_for_percentage(percentage: float) -> int:
    pct = round(percentage)
    for threshold, stars in STAR_THRESHOLDS:
        if pct >= threshold:
            return stars
    return 0


class Game:
    def __init__(self, questions: List[Question], player_name: str = "",
                 question_count: int = 10):
        self._id = str(uuid.uuid4())
        self._player_name = player_name
        self._all_questions = list(questions)
        self._questions = self._all_questions[:question_count]
        self._score = 0
        self._index = 0
        self._state_machine = GameStateMachine()
        self._last_correct: Optional[bool] = None

    # -- state machine delegation --------------------------------------
    @property
    def state(self) -> GameState:
        return self._state_machine.state

    def pause(self) -> None:
        self._state_machine.pause()

    def resume(self) -> None:
        self._state_machine.resume()

    def game_over(self) -> None:
        self._state_machine.game_over()

    # -- UML attributes ------------------------------------------------
    @property
    def id(self) -> str:
        return self._id

    @property
    def score(self) -> int:
        return self._score

    @property
    def player_name(self) -> str:
        return self._player_name

    @property
    def index(self) -> int:
        return self._index

    @property
    def total(self) -> int:
        return len(self._questions)

    @property
    def questions(self) -> List[Question]:
        return list(self._questions)

    def current_question(self) -> Optional[Question]:
        if self.is_finished():
            return None
        return self._questions[self._index]

    def is_finished(self) -> bool:
        return self._index >= len(self._questions)

    @property
    def last_correct(self) -> Optional[bool]:
        return self._last_correct

    # -- UML methods ---------------------------------------------------
    def play(self) -> None:
        """Begin / (re)enter the playing state if not already over."""
        self._state_machine = GameStateMachine()

    def viewScore(self) -> int:
        return self._score

    # -- question flow -------------------------------------------------
    def submit_answer(self, user_answer: str) -> bool:
        """Check the current answer, advance, and return correctness.
        Raises StopIteration if called after the round is finished."""
        if self.is_finished():
            raise StopIteration("No questions remaining")
        if self.state is GameState.GAME_OVER:
            raise StateError("Game is over")
        q = self._questions[self._index]
        correct = q.is_correct(user_answer)
        self._last_correct = correct
        if correct:
            self._score += 1
        self._index += 1
        if self.is_finished():
            self._state_machine.game_over()
        return correct

    def percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return 100.0 * self._score / self.total

    def stars(self) -> int:
        return stars_for_percentage(self.percentage())

    def result(self) -> dict:
        return {
            "player_name": self._player_name,
            "score": self._score,
            "total": self.total,
            "percentage": round(self.percentage(), 1),
            "stars": self.stars(),
        }

    def snapshot(self) -> dict:
        return {
            "id": self._id,
            "player_name": self._player_name,
            "score": self._score,
            "index": self._index,
            "state": self.state.name,
            "question_ids": [q.id for q in self._questions],
        }
