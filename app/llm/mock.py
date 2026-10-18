"""Scripted MockProvider — runs the whole agent with zero API cost and deterministic results.

Each script step is either an LLMResponse or a callable `(messages, tools) -> LLMResponse`, so a
test can react to what the agent sent (e.g. check a tool result before answering).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from typing import Any

from app.llm.provider import LLMError, LLMProvider, LLMResponse, ToolCall, Usage

Step = LLMResponse | Callable[[list[dict[str, Any]], list[dict[str, Any]] | None], LLMResponse]


class MockProvider(LLMProvider):
    name = "Mock (scripted, no cost)"

    def __init__(self, script: Iterable[Step] = (), model: str = "mock"):
        self.model = model
        self._script: list[Step] = list(script)
        self.requests: list[dict[str, Any]] = []  # what the agent sent, for assertions

    def add(self, *steps: Step) -> MockProvider:
        self._script.extend(steps)
        return self

    def complete(self, messages, tools=None, max_tokens=8192) -> LLMResponse:
        self.requests.append({"messages": [dict(m) for m in messages], "tools": tools})
        if not self._script:
            raise LLMError("MockProvider script exhausted.")
        step = self._script.pop(0)
        resp = step(messages, tools) if callable(step) else step
        if resp.usage.total_tokens == 0:  # fake but plausible usage for cost/budget code paths
            prompt = sum(len(str(m.get("content", ""))) for m in messages) // 4
            resp.usage = Usage(prompt_tokens=prompt, completion_tokens=50, cache_miss_tokens=prompt)
        return resp

    def test_connection(self) -> str:
        return "Mock provider ready (no network, no cost)."


def tool_call(name: str, call_id: str | None = None, **arguments: Any) -> ToolCall:
    """Helper to build a ToolCall in test scripts."""
    return ToolCall(id=call_id or f"call_{name}", name=name, arguments=json.dumps(arguments))


def reply(*calls: ToolCall, content: str | None = None) -> LLMResponse:
    """Helper: an assistant turn with the given tool calls (finish_reason=tool_calls if any)."""
    return LLMResponse(content=content, tool_calls=list(calls), finish_reason="tool_calls" if calls else "stop")
