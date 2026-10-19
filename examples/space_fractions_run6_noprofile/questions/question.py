"""Question entity (domain model, tkinter-free)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from fractions import Fraction


@dataclass
class Question:
    """A fraction question.

    Attributes follow the UML class diagram: id, prompt, options.
    A question has one of two kinds:
      * 'choice' - the player picks the correct option from ``options``
                   (``correct`` must be present in ``options``).
      * 'typed'  - the player types the fraction; ``correct`` is the expected
                   value and ``options`` is empty.
    """

    id: str
    prompt: str
    correct: str
    kind: str = "choice"
    options: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.kind not in ("choice", "typed"):
            raise ValueError(f"Unknown question kind: {self.kind!r}")
        if self.kind == "choice":
            if not self.options:
                raise ValueError("choice question must provide options")
            if self.correct not in self.options:
                raise ValueError(
                    f"correct value {self.correct!r} not among options {self.options!r}"
                )
        else:
            self.options = []

    def get_prompt(self) -> str:
        """Return the question prompt."""
        return self.prompt

    def get_options(self) -> List[str]:
        """Return the answer options (empty for typed questions)."""
        return list(self.options)

    def check_answer(self, answer: str) -> bool:
        """Return True iff ``answer`` equals the correct value.

        Fraction answers are compared by numeric value, so equivalent textual
        forms ("1/2" vs "2/4") are treated as correct for typed questions.
        For choice questions the raw string must match an option exactly.
        """
        if answer is None:
            return False
        answer = str(answer).strip()
        if self.kind == "choice":
            return answer == self.correct
        return _fraction_equal(answer, self.correct)


def _fraction_equal(a: str, b: str) -> bool:
    """Compare two fraction strings by numeric value; tolerate invalid input."""
    try:
        return Fraction(a) == Fraction(b)
    except (ValueError, ZeroDivisionError):
        return False
