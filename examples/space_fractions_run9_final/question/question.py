"""Question domain entity.

A Question is the spec's Question class (id, prompt, options) extended so that
grading follows the prompt's own criterion. `kind` determines how an answer is
checked; `choices` are the displayed options (empty = typed answer);
`correct_value` is the accepted answer text.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional


KNOWN_KINDS = ("identify", "compare", "add", "subtract", "reduce", "equivalent")


def _normalise(value: str) -> str:
    try:
        return str(Fraction(value.replace(" ", "")))
    except (ValueError, ZeroDivisionError):
        return value.strip().lower()


@dataclass
class Question:
    id: str
    prompt: str
    options: List[str] = field(default_factory=list)
    correct_value: str = ""
    kind: str = "identify"
    choices: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.choices:
            self.choices = list(self.options)
        if not self.correct_value:
            self.correct_value = self.choices[0] if self.choices else ""

    def get_prompt(self) -> str:
        return self.prompt

    def get_options(self) -> List[str]:
        return list(self.choices)

    def has_choices(self) -> bool:
        return bool(self.choices)

    def check_answer(self, submitted: str) -> bool:
        """Grade a submitted answer against this question's criterion."""
        submitted = (submitted or "").strip()
        if not submitted:
            return False
        if self.choices:
            return submitted == self.correct_value
        if self.kind == "reduce":
            # "lowest terms" accepts ONLY the reduced form, not every equal value
            return submitted == self.correct_value
        return _normalise(submitted) == _normalise(self.correct_value)


@dataclass
class GeneratedQuestion(Question):
    """A generator-produced question; carries operands so tests can recompute
    the expected value independently."""

    operands: Optional[dict] = None
