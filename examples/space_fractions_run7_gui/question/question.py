"""Question entity (pure Python, no Tkinter)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import List, Optional


class QuestionKind(str, Enum):
    """Supported question kinds for the game."""

    COMPARE = "compare"
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    SIMPLIFY = "simplify"
    EQUIVALENT = "equivalent"


@dataclass
class Question:
    """A single question: prompt, correct value, and choices.

    For generated math questions the ``operands`` dict stores the raw inputs so tests
    (and the generator validation) can recompute the expected value independently.
    """

    id: str
    prompt: str
    correct: str
    options: List[str] = field(default_factory=list)
    kind: QuestionKind = QuestionKind.COMPARE
    operands: Optional[dict] = None

    # ---- methods required by the class diagram ----
    def getPrompt(self) -> str:
        return self.prompt

    def getOptions(self) -> List[str]:
        return list(self.options)

    def checkAnswer(self, submitted: str) -> bool:
        """Return True if the submitted answer is correct (normalised)."""
        return self.normalise(submitted) == self.normalise(self.correct)

    @staticmethod
    def normalise(value: str) -> str:
        """Normalise a fraction-typed answer so '2/4' == '1/2'."""
        text = (value or "").strip().lower()
        if not text:
            return ""
        try:
            f = Fraction(text)
            return f"{f.numerator}/{f.denominator}"
        except (ValueError, ZeroDivisionError):
            return text

    @classmethod
    def from_kwargs(cls, **kwargs) -> "Question":
        """Build a Question from a dict (used by the seed/repository layers)."""
        kind = kwargs.get("kind", "compare")
        if isinstance(kind, str):
            kind = QuestionKind(kind)
        return cls(
            id=kwargs.get("id", ""),
            prompt=kwargs.get("prompt", ""),
            correct=kwargs.get("correct", ""),
            options=list(kwargs.get("options", [])),
            kind=kind,
            operands=kwargs.get("operands"),
        )

    def to_kwargs(self) -> dict:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "correct": self.correct,
            "options": list(self.options),
            "kind": self.kind.value,
            "operands": self.operands,
        }

    def validate(self) -> List[str]:
        """Return a list of validation errors (empty == valid)."""
        errors: List[str] = []
        if not self.id or not self.id.strip():
            errors.append("ID is required")
        if not self.prompt or not self.prompt.strip():
            errors.append("Prompt is required")
        if not self.correct or not self.correct.strip():
            errors.append("Correct value is required")
        seen = set()
        for opt in self.options:
            norm = self.normalise(opt)
            if norm in seen:
                errors.append(f"Duplicate option: {opt}")
            seen.add(norm)
        if self.kind is QuestionKind.EQUIVALENT and not self.options:
            errors.append("An equivalent-fraction question needs choices")
        return errors


__all__ = ["Question", "QuestionKind"]
