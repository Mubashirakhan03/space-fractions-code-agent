"""Replay a recorded run with zero API cost.

ReplayProvider feeds the model responses stored in a transcript back into the real agent loop, so
the tools really execute again and the project is regenerated on disk — useful for demos when the
internet/API is unavailable. Always labelled "REPLAY of recorded run"; it never pretends to be live.
"""

from __future__ import annotations

from pathlib import Path

from app.agent.transcript import read_events
from app.llm.provider import LLMError, LLMProvider, LLMResponse, ToolCall, Usage

REPLAY_LABEL = "REPLAY of recorded run"


class ReplayProvider(LLMProvider):
    name = REPLAY_LABEL

    def __init__(self, transcript_path: Path | str):
        events = read_events(Path(transcript_path))
        start = next((e for e in events if e["event"] == "run_start"), {})
        self.recorded_model = start.get("model", "unknown")
        self.recorded_provider = start.get("provider", "unknown")
        self.model = f"replay:{self.recorded_model}"
        self._responses = [
            LLMResponse(content=e.get("content"), finish_reason=e.get("finish_reason", "stop"),
                        reasoning_content=e.get("reasoning_content"),
                        tool_calls=[ToolCall(**t) for t in e.get("tool_calls", [])],
                        usage=Usage(**e.get("usage", {})))
            for e in events if e["event"] == "llm_response"
        ]
        if not self._responses:
            raise LLMError(f"No recorded model responses in {transcript_path}")

    @property
    def remaining(self) -> int:
        return len(self._responses)

    def complete(self, messages, tools=None, max_tokens=8192) -> LLMResponse:
        if not self._responses:
            raise LLMError("Replay finished: no more recorded responses.")
        return self._responses.pop(0)

    def test_connection(self) -> str:
        return f"{REPLAY_LABEL}: {len(self._responses)} responses from {self.recorded_provider} / {self.recorded_model}"
