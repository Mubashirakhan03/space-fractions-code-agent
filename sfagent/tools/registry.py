"""Tool registry: JSON-schema tool definitions, validation, permissions by mode, batch execution.

Mirrors Claude Code's tool system: every tool declares whether it is read-only; consecutive
read-only calls run in parallel, write calls run serially; failures are returned to the model as
`is_error` results instead of crashing the loop. Tool order is fixed so the prompt prefix (and
DeepSeek's cache) stays stable.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from sfagent.llm.provider import ToolCall
from sfagent.tools.sandbox import SandboxError

MAX_PARALLEL = 8


class ToolError(Exception):
    """A tool failed in a way the model can fix (bad argument, not found, …)."""


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[[Any, dict[str, Any]], str]
    read_only: bool = False
    modes: frozenset[str] | None = None  # None = allowed in every mode
    ends_phase: bool = False

    def schema(self) -> dict[str, Any]:
        return {"type": "function",
                "function": {"name": self.name, "description": self.description, "parameters": self.parameters}}


@dataclass
class ToolResult:
    call_id: str
    name: str
    content: str
    is_error: bool = False
    ends_phase: bool = False
    args: dict[str, Any] | None = None


class ToolRegistry:
    def __init__(self, context: Any = None):
        self.context = context
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"duplicate tool {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schema() for t in self._tools.values()]

    def execute(self, call: ToolCall, mode: str) -> ToolResult:
        tool = self._tools.get(call.name)
        if tool is None:
            return ToolResult(call.id, call.name, f"Unknown tool '{call.name}'. Available: {', '.join(self._tools)}",
                              is_error=True)
        try:
            args = json.loads(call.arguments or "{}")
            if not isinstance(args, dict):
                raise ValueError("arguments must be a JSON object")
        except (json.JSONDecodeError, ValueError) as exc:
            return ToolResult(call.id, call.name, f"Invalid JSON arguments ({exc}). Re-send the call with valid JSON.",
                              is_error=True)
        missing = [k for k in tool.parameters.get("required", []) if k not in args]
        if missing:
            return ToolResult(call.id, call.name, f"Missing required argument(s): {', '.join(missing)}",
                              is_error=True, args=args)
        if tool.modes is not None and mode not in tool.modes:
            return ToolResult(call.id, call.name,
                              f"Permission denied: '{call.name}' is not available in {mode} mode.",
                              is_error=True, args=args)
        try:
            content = tool.handler(self.context, args)
            return ToolResult(call.id, call.name, content, ends_phase=tool.ends_phase, args=args)
        except (ToolError, SandboxError) as exc:
            return ToolResult(call.id, call.name, f"Error: {exc}", is_error=True, args=args)
        except Exception as exc:  # never let a tool crash the agent loop
            return ToolResult(call.id, call.name, f"Error: {type(exc).__name__}: {exc}", is_error=True, args=args)

    def execute_batch(self, calls: list[ToolCall], mode: str) -> list[ToolResult]:
        """Run calls in order; consecutive read-only calls are executed in parallel."""
        results: list[ToolResult] = []
        i = 0
        while i < len(calls):
            j = i
            while j < len(calls) and self._is_read_only(calls[j]):
                j += 1
            if j - i > 1:
                with ThreadPoolExecutor(max_workers=min(MAX_PARALLEL, j - i)) as pool:
                    results.extend(pool.map(lambda c: self.execute(c, mode), calls[i:j]))
                i = j
            else:
                results.append(self.execute(calls[i], mode))
                i += 1
        return results

    def _is_read_only(self, call: ToolCall) -> bool:
        tool = self._tools.get(call.name)
        return bool(tool and tool.read_only)
