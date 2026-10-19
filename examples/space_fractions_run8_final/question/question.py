"""Question domain model: a single fraction question.

Tkinter-free and headless-testable.
"""
from fractions import Fraction
from enum import Enum
from typing import List
import uuid


class QuestionKind(str, Enum):
    EQUIVALENT = "equivalent"      # given a/b, pick p/q with same value
    SIMPLIFY = "simplify"          # reduce a/b to lowest terms
    DECIMAL = "decimal"            # convert a/b to a decimal string
    LARGER = "larger"              # which of two fractions is larger


def _frac_str(f: Fraction) -> str:
    """Format a fraction like '3/4' or '2' for whole numbers."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _parse_frac(s: str) -> Fraction:
    s = s.strip()
    if "/" in s:
        n, d = s.split("/", 1)
        return Fraction(int(n), int(d))
    return Fraction(int(s))


class Question:
    _OPTION_COUNT = 4

    def __init__(
        self,
        prompt: str,
        options: List[str],
        correct_index: int = 0,
        kind: QuestionKind = QuestionKind.EQUIVALENT,
        explanation: str = "",
        qid: str = "",
    ):
        """A question where options[correct_index] is the correct answer.

        The correct answer is stored as Text (its position among options), so the
        actual value must always equal options[correct_index].
        """
        self.id: str = qid or uuid.uuid4().hex[:12]
        self.prompt: str = prompt
        self.kind: QuestionKind = kind
        self.explanation: str = explanation
        self._options: List[str] = list(options)
        if not 0 <= correct_index < len(options):
            raise ValueError("correct_index out of range")
        self.correct_index: int = correct_index

    # -- public accessors named after the class diagram --
    def getPrompt(self) -> str:
        return self.prompt

    def getOptions(self) -> List[str]:
        return list(self._options)

    @property
    def correct_answer(self) -> str:
        return self._options[self.correct_index]

    def checkAnswer(self, submitted: str) -> bool:
        """Check a submitted option text against the correct one.

        For DECIMAL questions we also accept exact-value decimal input, and for
        typed fraction input we compare reduced values to avoid accepting an
        equivalent-but-differently-written option as 'wrong'.
        """
        submitted = submitted.strip()
        if submitted == self.correct_answer:
            return True
        # value-equivalence for fraction kinds
        if self.kind in (QuestionKind.SIMPLIFY, QuestionKind.LARGER):
            try:
                if _parse_frac(submitted) == _parse_frac(self.correct_answer):
                    return True
            except (ValueError, ZeroDivisionError):
                return False
        if self.kind == QuestionKind.DECIMAL:
            try:
                if float(submitted) == float(self.correct_answer):
                    return True
            except ValueError:
                return False
        if self.kind == QuestionKind.EQUIVALENT:
            try:
                if _parse_frac(submitted) == _parse_frac(self.correct_answer):
                    return True
            except (ValueError, ZeroDivisionError):
                return False
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "kind": self.kind.value,
            "options": list(self._options),
            "correct_index": self.correct_index,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Question":
        return cls(
            prompt=d["prompt"],
            options=d["options"],
            correct_index=d.get("correct_index", 0),
            kind=QuestionKind(d.get("kind", "equivalent")),
            explanation=d.get("explanation", ""),
            qid=d.get("id", ""),
        )


# Backwards-friendly module helper (used by generator and tests).
def check_fraction_answer(question: Question, submitted: str) -> bool:
    return question.checkAnswer(submitted)
