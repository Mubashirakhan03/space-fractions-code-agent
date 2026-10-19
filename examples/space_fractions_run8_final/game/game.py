"""Game domain model: a series of fraction questions with a score."""
from typing import List, Optional
import uuid

from question.question import Question
from game.state import GameState, GameStateMachine


class Game:
    """A game is a composition of Questions (Game --* Question)."""

    def __init__(self, questions: List[Question], qid: str = ""):
        self.id: str = qid or uuid.uuid4().hex[:12]
        self.questions: List[Question] = list(questions)
        self._score: int = 0
        self._index: int = 0
        self._answers: List[bool] = []
        self.state_machine: GameStateMachine = GameStateMachine()

    # -- class diagram methods --
    def play(self) -> None:
        """Begin/resume the round loop; no-op here (UI drives it) but keeps the API."""
        self.state_machine.state = GameState.PLAYING

    def viewScore(self) -> int:
        return self._score

    @property
    def score(self) -> int:
        return self._score

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def current_index(self) -> int:
        return self._index

    @property
    def current_question(self) -> Optional[Question]:
        if 0 <= self._index < len(self.questions):
            return self.questions[self._index]
        return None

    def submit(self, answer_text: str) -> bool:
        q = self.current_question
        if q is None:
            raise IndexError("No current question")
        correct = q.checkAnswer(answer_text)
        self._answers.append(correct)
        if correct:
            self._score += 1
        self._index += 1
        if self._index >= len(self.questions):
            self.state_machine.game_over()
        return correct

    def pause(self) -> None:
        self.state_machine.pause()

    def resume(self) -> None:
        self.state_machine.resume()

    @property
    def is_over(self) -> bool:
        return self.state_machine.state == GameState.GAMEOVER

    @property
    def answers(self) -> List[bool]:
        return list(self._answers)

    def reviewed_questions(self) -> List[tuple]:
        """Return (question, correct?, user_was_correct) for answered items."""
        out = []
        for i, q in enumerate(self.questions):
            if i < len(self._answers):
                out.append((q, self._answers[i]))
        return out

    def rating(self) -> str:
        """Rating text driven strictly by the real result (no praise for zero)."""
        if self.total == 0:
            return "No questions"
        pct = self._score / self.total
        if pct >= 0.9:
            return "Excellent! You are a fractions star!"
        if pct >= 0.7:
            return "Great job — keep it up!"
        if pct >= 0.5:
            return "Good effort — practise a little more."
        if pct > 0:
            return "Keep practising — you'll get there!"
        return "No correct answers yet — try again!"
