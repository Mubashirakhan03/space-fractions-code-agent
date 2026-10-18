"""Answer checking using fractions.Fraction so equivalent forms are accepted."""
from __future__ import annotations

from fractions import Fraction


def _to_fraction(value: str) -> Fraction | None:
    """Parse a student answer ('2/4', '1/2', '0.5', '2') into a Fraction, or None."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None


def check_answer(question_answer: str, student_answer: str) -> bool:
    """Return True if the student's answer equals the canonical answer.

    Equivalent fractions are accepted, e.g. 2/4 == 1/2.
    """
    expected = _to_fraction(question_answer)
    actual = _to_fraction(student_answer)
    if expected is None or actual is None:
        # Fall back to case-insensitive exact string comparison for non-numeric answers.
        return (
            str(question_answer).strip().lower()
            == str(student_answer).strip().lower()
        )
    return expected == actual
