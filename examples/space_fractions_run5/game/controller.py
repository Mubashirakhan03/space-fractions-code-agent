"""GameController: orchestrates a round of fraction questions and scoring."""
from __future__ import annotations

import random
from typing import Iterable, Optional, Tuple

from game.models import Game
from game.state_machine import GameStateMachine, InvalidTransitionError
from questions.checker import QuestionChecker
from questions.model import Question


class GameController:
    """Drives one play session against a pool of questions.

    Pure and testable: no tkinter imports. The UI calls these methods and
    renders the results.
    """

    def __init__(
        self,
        questions: Iterable[Question],
        round_size: int = 10,
        rng: Optional[random.Random] = None,
    ) -> None:
        pool = list(questions)
        self.rng = rng or random.Random()
        if len(pool) < round_size:
            # allow a smaller round when the pool is smaller than requested
            round_size = max(1, len(pool))
        self._round_size = round_size
        chosen = self.rng.sample(pool, round_size)
        self.game = Game(questions=chosen)
        self.state_machine = GameStateMachine()
        self.last_answer_correct = False
        self.last_expected = ""

    # -- state machine delegation -------------------------------------------
    def pause(self) -> None:
        self.state_machine.pause()

    def resume(self) -> None:
        self.state_machine.resume()

    def game_over(self) -> None:
        self.state_machine.game_over()

    # -- question flow -------------------------------------------------------
    @property
    def current_question(self) -> Optional[Question]:
        return self.game.current_question

    def submit_answer(self, given: str) -> Tuple[bool, str]:
        """Check the answer against the current question and advance.

        Returns (correct, expected_display). The expected value is computed
        BEFORE advancing so wrong-answer feedback names the right answer.
        Raises InvalidTransitionError if the game is over.
        """
        question = self.current_question
        if question is None:
            self.game_over()
            raise InvalidTransitionError(
                "Cannot submit an answer after the game is over."
            )
        correct, expected = QuestionChecker.check(question, given)
        self.last_answer_correct = correct
        self.last_expected = expected
        self.game.answered_count += 1
        if correct:
            self.game.correct_count += 1
            self.game.score += 1
        return correct, expected

    def advance(self) -> None:
        """Move to the next question (or finish the game)."""
        self.game.current_index += 1
        if self.game.is_finished():
            self.game_over()

    @property
    def is_finished(self) -> bool:
        return self.game.is_finished()
