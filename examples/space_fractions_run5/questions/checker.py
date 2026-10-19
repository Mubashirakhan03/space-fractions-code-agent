"""Answer checking using fractions.Fraction so equivalent forms are accepted."""
from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from questions.model import Question


def _to_fraction(text: str) -> Fraction:
    """Parse an answer into a Fraction, tolerant of common kid input.

    Accepts forms like ``3/4``, ``2 1/2``, ``1.5``, ``3``, ``0.75`` and
    whitespace. Raises ValueError when it cannot be parsed.
    """
    s = text.strip().replace(",", ".")
    s = s.replace(" ", "")
    if "/" in s and s.count("/") == 1:
        num, den = s.split("/")
        return Fraction(int(num), int(den))
    if "." in s:
        return Fraction(float(s))
    return Fraction(int(s))


class QuestionChecker:
    """Check a user's answer against a question's answer, by value."""

    @staticmethod
    def check(question: Question, given: str) -> Tuple[bool, str]:
        """Return (correct, expected_display) for a submitted answer.

        The expected display is normalised so wrong-answer feedback can say
        "the answer is 3/4". Both the given and expected answers are reduced to
        a common `Fraction` for comparison, which is what makes 2/4 == 1/2.
        """
        expected_display = QuestionChecker.normalise(question.answer)
        if given is None:
            return False, expected_display
        given = given.strip()
        if not given:
            return False, expected_display
        try:
            expected_val = QuestionChecker._value(question.answer)
            given_val = QuestionChecker._value(given)
        except (ValueError, ZeroDivisionError):
            return False, expected_display
        return given_val == expected_val, expected_display

    @staticmethod
    def _value(text: str) -> Fraction:
        if "/" in text and text.count("/") == 1:
            num, den = text.split("/")
            return Fraction(int(num), int(den))
        if "." in text:
            return Fraction(float(text))
        return Fraction(int(text))

    @staticmethod
    def normalise(text: str) -> str:
        """Return a tidy display form of an answer, e.g. ``3/4``."""
        try:
            f = QuestionChecker._value(text)
        except (ValueError, ZeroDivisionError):
            return text.strip()
        if f.denominator == 1:
            return str(f.numerator)
        return f"{f.numerator}/{f.denominator}"
