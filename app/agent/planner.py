"""TodoWrite-style task list: the model replaces the whole list each time it updates progress."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

STATUSES = ("pending", "in_progress", "completed")
ICONS = {"pending": "[ ]", "in_progress": "[~]", "completed": "[x]"}


@dataclass
class Todo:
    content: str
    status: str = "pending"


class TodoList:
    def __init__(self, items: list[Todo] | None = None):
        self.items: list[Todo] = items or []

    def update(self, raw: Any) -> None:
        """Validate and replace the list. Raises ValueError with a model-readable message."""
        if not isinstance(raw, list) or not raw:
            raise ValueError("todos must be a non-empty list of {content, status} objects.")
        items = []
        for i, t in enumerate(raw):
            if not isinstance(t, dict) or not str(t.get("content", "")).strip():
                raise ValueError(f"todo #{i + 1} needs a non-empty 'content'.")
            status = t.get("status", "pending")
            if status not in STATUSES:
                raise ValueError(f"todo #{i + 1} has invalid status '{status}'; use one of {', '.join(STATUSES)}.")
            items.append(Todo(str(t["content"]).strip(), status))
        if sum(t.status == "in_progress" for t in items) > 1:
            raise ValueError("Only one todo may be 'in_progress' at a time.")
        self.items = items

    def render(self) -> str:
        if not self.items:
            return "(no todos)"
        done = sum(t.status == "completed" for t in self.items)
        lines = [f"{ICONS[t.status]} {t.content}" for t in self.items]
        return f"Todos ({done}/{len(self.items)} completed):\n" + "\n".join(lines)

    def to_list(self) -> list[dict[str, str]]:
        return [asdict(t) for t in self.items]

    @classmethod
    def from_list(cls, data: list[dict[str, str]]) -> TodoList:
        return cls([Todo(**d) for d in data])
