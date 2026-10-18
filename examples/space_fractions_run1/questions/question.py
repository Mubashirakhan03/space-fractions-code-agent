"""Question domain class (QuestionComponent)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


VALID_TYPES = {"equivalent", "compare", "add_subtract", "simplify"}


@dataclass
class Question:
    """A single fraction question."""

    id: str
    prompt: str
    type: str
    options: List[str] = field(default_factory=list)
    answer: str = ""

    def __post_init__(self) -> None:
        if self.type not in VALID_TYPES:
            raise ValueError(f"Invalid question type: {self.type!r}")

    def get_prompt(self) -> str:
        return self.prompt

    def get_options(self) -> List[str]:
        return list(self.options)

    def is_multiple_choice(self) -> bool:
        return bool(self.options)
