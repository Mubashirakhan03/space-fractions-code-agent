"""Append-only JSONL transcript of a run (agent_run/transcript.jsonl): observability + replay source."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.llm.provider import LLMResponse


class Transcript:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._seq = sum(1 for _ in self.path.open(encoding="utf-8")) if self.path.exists() else 0

    def append(self, event: str, **data: Any) -> None:
        with self._lock:
            self._seq += 1
            rec = {"seq": self._seq, "ts": round(time.time(), 3), "event": event, **data}
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")

    def log_response(self, phase: str, resp: LLMResponse, purpose: str = "agent") -> None:
        self.append("llm_response", phase=phase, purpose=purpose, content=resp.content,
                    reasoning_content=resp.reasoning_content, finish_reason=resp.finish_reason,
                    tool_calls=[asdict(t) for t in resp.tool_calls], usage=asdict(resp.usage))


def read_events(path: Path) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
