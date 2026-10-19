"""Persistent run state (agent_run/state.json) so an interrupted run can be resumed later."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from sfagent.llm.provider import Usage

PHASES = ("plan", "implement", "verify", "report", "done")


@dataclass
class RunState:
    phase: str = "plan"
    phase_started: bool = False
    messages: list[dict[str, Any]] = field(default_factory=list)
    todos: list[dict[str, str]] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=lambda: asdict(Usage()))
    cost_usd: float = 0.0
    requests: int = 0
    steps: int = 0
    fix_round: int = 0
    compactions: int = 0
    plan: dict[str, Any] | None = None
    verify_ok: bool | None = None
    verify_report: str = ""
    status: str = "running"
    stop_reason: str = ""
    provider: str = ""
    model: str = ""
    elapsed_s: float = 0.0
    written: list[str] = field(default_factory=list)

    @property
    def usage_obj(self) -> Usage:
        return Usage(**self.usage)

    def add_usage(self, u: Usage) -> None:
        self.usage = asdict(self.usage_obj + u)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(self), indent=1, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)  # atomic: a crash never leaves a half-written state file

    @classmethod
    def load(cls, path: Path) -> RunState:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        known = cls.__dataclass_fields__.keys()
        return cls(**{k: v for k, v in data.items() if k in known})
