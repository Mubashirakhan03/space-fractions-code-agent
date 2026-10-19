"""Question entity and answer checking for Space Fractions.

Answers are checked with :class:`fractions.Fraction` so that equivalent
forms (e.g. 2/4 == 1/2) are accepted for typed answers.
"""
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import List, Optional, Tuple


class QuestionType(str, Enum):
    """The four fraction question types in the game."""
    EQUIVALENT = "equivalent"
    COMPARE = "compare"
    ADD_SUBTRACT = "add_subtract"
    SIMPLIFY = "simplify"


@dataclass
class Question:
    """A single fraction question.

    Attributes mirror the UML class diagram: ``id``, ``prompt``, ``options``
    plus the additional fields needed to actually check an answer.
    """
    id: str
    prompt: str
    options: List[str] = field(default_factory=list)
    qtype: QuestionType = QuestionType.EQUIVALENT
    answer: str = "1/2"
    #: True -> multiple choice; False -> typed (numeric) answer.
    is_choice: bool = True

    # --- UML methods -------------------------------------------------------
    def getPrompt(self) -> str:
        return self.prompt

    def getOptions(self) -> List[str]:
        return list(self.options)

    # --- answer checking ---------------------------------------------------
    @staticmethod
    def _parse_fraction(value: str) -> Fraction:
        value = (value or "").strip()
        if "/" in value:
            num, den = value.split("/", 1)
            return Fraction(int(num.strip()), int(den.strip()))
        return Fraction(int(value))

    def checkAnswer(self, submitted: Optional[str]) -> Tuple[bool, str]:
        """Return ``(correct, expected_canonical)``.

        For compare questions the expected answer is one of the given options;
        for all other types the answer is reduced to canonical form so that
        e.g. ``2/4`` matches ``1/2``.
        """
        submitted = (submitted or "").strip()
        if not submitted:
            return False, self._canonical_answer()
        if self.qtype is QuestionType.COMPARE:
            return submitted == self.answer, self.answer
        try:
            return (
                self._parse_fraction(submitted) == self._parse_fraction(self.answer),
                self._canonical_answer(),
            )
        except (ValueError, ZeroDivisionError):
            return False, self._canonical_answer()

    def _canonical_answer(self) -> str:
        try:
            f = self._parse_fraction(self.answer)
            return f"{f.numerator}/{f.denominator}"
        except (ValueError, ZeroDivisionError):
            return self.answer
