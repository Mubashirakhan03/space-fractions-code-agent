"""The Question domain object and answer checking via fractions.Fraction."""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import List


@dataclass
class Question:
    """Design class Question (id, prompt, options; getPrompt, getOptions)."""

    id: str
    prompt: str
    options: List[str] = field(default_factory=list)
    answer: str = ""
    qtype: str = "equivalent"
    explanation: str = ""

    def get_prompt(self) -> str:
        return self.prompt

    def get_options(self) -> List[str]:
        return list(self.options)

    # -- answer checking --------------------------------------------------
    def check_answer(self, given: str) -> bool:
        """Check a submitted answer; accepts equivalent fraction forms.

        Numeric fraction inputs compare by value (2/4 == 1/2).
        Word answers (e.g. 'greater', 'less', 'equal') compare case-insensitively.
        """
        given = (given or "").strip()
        if not given:
            return False
        # Word-type comparison questions.
        expected_text = self.answer.strip()
        if _is_word_value(expected_text):
            return given.lower() == expected_text.lower()
        # Multiple choice: accept the chosen option text too.
        if given in self.options:
            return given == self.answer
        # Fraction comparison (equivalent forms accepted).
        try:
            return Fraction(given) == Fraction(self.answer)
        except (ValueError, ZeroDivisionError):
            return given == self.answer


_WORD_VALUES = {"greater", "less", "equal", "more", "fewer", "true", "false"}


def _is_word_value(value: str) -> bool:
    return value.strip().lower() in _WORD_VALUES


def is_fraction_input(text: str) -> bool:
    """True if the text can be parsed as a fraction (e.g. '3/4', '0.5', '2')."""
    try:
        Fraction(text.strip())
        return True
    except (ValueError, ZeroDivisionError):
        return False
