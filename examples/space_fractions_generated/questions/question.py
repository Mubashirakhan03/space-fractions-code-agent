"""Question domain model and answer checking.

Pure Python (no Tkinter). Correctness is judged with fractions.Fraction so that
equivalent forms are accepted (e.g. 2/4 == 1/2).
"""
from __future__ import annotations

import enum
import re
from fractions import Fraction
from typing import List, Optional


class QType(str, enum.Enum):
    EQUIVALENT = "equivalent"
    COMPARE = "compare"
    ADD_SUBTRACT = "add_subtract"
    SIMPLIFY = "simplify"


class Question:
    """A single fraction question.

    Matches the UML class Question:
      id, prompt, options (private); methods getPrompt(), getOptions().
    """

    def __init__(self, id: str, prompt: str, answer: str,
                 qtype: str = QType.EQUIVALENT.value,
                 options: Optional[List[str]] = None):
        self._id = id
        self._prompt = prompt
        self._answer_raw = answer
        self._qtype = QType(qtype)
        self._options = list(options) if options else []
        self._answer = Fraction(answer)

    @property
    def id(self) -> str:
        return self._id

    @property
    def qtype(self) -> QType:
        return self._qtype

    @property
    def answer(self) -> Fraction:
        return self._answer

    def getPrompt(self) -> str:
        return self._prompt

    def getOptions(self) -> List[str]:
        return list(self._options)

    def is_correct(self, user_answer: str) -> bool:
        """Return True if the user's answer equals the correct answer,
        treating equivalent fractions as equal."""
        try:
            return Fraction(self._normalise(user_answer)) == self._answer
        except (ValueError, ZeroDivisionError):
            return False

    def is_multiple_choice(self) -> bool:
        return bool(self._options)

    @staticmethod
    def _normalise(text: str) -> str:
        return text.strip().replace(" ", "")

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "qtype": self._qtype.value,
            "prompt": self._prompt,
            "options": self._options,
            "answer": str(self._answer),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Question":
        return cls(
            id=d["id"],
            prompt=d["prompt"],
            answer=d["answer"],
            qtype=d.get("qtype", QType.EQUIVALENT.value),
            options=d.get("options"),
        )

    def __repr__(self) -> str:
        return f"Question(id={self._id!r}, qtype={self._qtype.value!r}, answer={self._answer!r})"
