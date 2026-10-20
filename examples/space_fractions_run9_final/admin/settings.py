"""Settings management (PIN storage) for the protected Admin area."""
from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_PIN = "4321"
DEFAULT_SETTINGS = {"admin_pin": DEFAULT_PIN}


class Settings:
    """Reads/writes a small local settings file holding the admin PIN."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._data: dict = {}

    def load(self) -> None:
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                self._data = {}
        if "admin_pin" not in self._data:
            self._data["admin_pin"] = DEFAULT_PIN
            self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._data, indent=2), encoding="utf-8"
        )

    @property
    def admin_pin(self) -> str:
        return str(self._data.get("admin_pin", DEFAULT_PIN))

    def check_pin(self, candidate: str) -> bool:
        return candidate == self.admin_pin
