"""Question model and multi-type answer checking (pure Python)."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List


@dataclass
class Question:
    """A single fraction question.

    Matches the UML `Question` class (id, prompt, options; getPrompt,
    getOptions) plus the fields needed for four question types.
    """

    prompt: str
    answer: str
    options: List[str] = field(default_factory=list)
    qtype: str = "choice"  # equivalent | compare | addsub | simplify
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def getPrompt(self) -> str:
        return self.prompt

    def getOptions(self) -> List[str]:
        return list(self.options)

    @property
    def is_multiple_choice(self) -> bool:
        return bool(self.options)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "answer": self.answer,
            "options": list(self.options),
            "qtype": self.qtype,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Question":
        return cls(
            prompt=d["prompt"],
            answer=d["answer"],
            options=list(d.get("options", [])),
            qtype=d.get("qtype", "choice"),
            id=str(d.get("id", uuid.uuid4().hex)),
        )
