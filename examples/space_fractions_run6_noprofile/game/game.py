"""Game entity and lifecycle (domain model, tkinter-free)."""
from __future__ import annotations

import random
from typing import List, Optional

from game.game_state import GameState
from questions.question import Question


class Game:
    """A round of fraction questions.

    Follows the UML class diagram (id, score, play(), viewScore()) plus the
    Playing/Paused/GameOver state machine with the transitions:
      [*]->Playing, Playing->Paused (pause), Paused->Playing (resume),
      Playing->GameOver (gameOver).
    """

    def __init__(self, id: str, questions: List[Question], rng: Optional[random.Random] = None) -> None:
        if not questions:
            raise ValueError("Game requires at least one question")
        self._id: str = id
        self._score: int = 0
        self._questions: List[Question] = list(questions)
        self._rng = rng or random.Random()
        self._index: int = 0
        self._state: GameState = GameState.PLAYING
        self._answered_current: bool = False

    # -- state machine -----------------------------------------------------
    @property
    def state(self) -> GameState:
        return self._state

    def pause(self) -> None:
        if self._state is not GameState.PLAYING:
            raise InvalidTransition(self._state, "pause()")
        self._state = GameState.PAUSED

    def resume(self) -> None:
        if self._state is not GameState.PAUSED:
            raise InvalidTransition(self._state, "resume()")
        self._state = GameState.PLAYING

    def game_over(self) -> None:
        if self._state is not GameState.PLAYING:
            raise InvalidTransition(self._state, "gameOver()")
        self._state = GameState.GAMEOVER

    # -- game flow ---------------------------------------------------------
    def play(self) -> str:
        """Return the prompt of the current question (SequenceDiagram1: Game->Question getPrompt)."""
        self._require_playing()
        return self.current_question.get_prompt()

    def submit_answer(self, answer: str) -> bool:
        """Score the current question and advance. Returns whether it was correct."""
        self._require_playing()
        if self._answered_current:
            raise AlreadyAnswered()
        question = self.current_question
        correct = question.check_answer(answer)
        if correct:
            self._score += 1
        self._answered_current = True
        self._index += 1
        if self._index >= len(self._questions):
            self._state = GameState.GAMEOVER
        return correct

    def view_score(self) -> int:
        return self._score

    # -- inspection --------------------------------------------------------
    @property
    def current_question(self) -> Question:
        if self._index >= len(self._questions):
            raise GameOverError("No current question: round is over")
        return self._questions[self._index]

    @property
    def answered_current(self) -> bool:
        return self._answered_current

    @property
    def total(self) -> int:
        return len(self._questions)

    @property
    def index(self) -> int:
        return self._index

    def _require_playing(self) -> None:
        if self._state is not GameState.PLAYING:
            raise InvalidTransition(self._state, "play()/submit_answer()")


class InvalidTransition(Exception):
    """Raised when an invalid state transition is attempted."""


class AlreadyAnswered(Exception):
    """Raised when the same question is answered twice."""


class GameOverError(Exception):
    """Raised when interacting with a finished round."""
