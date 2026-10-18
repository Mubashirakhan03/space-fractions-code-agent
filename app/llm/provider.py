"""Provider-neutral data types and the LLMProvider interface.

The agent loop only talks to this interface, so the real DeepSeek API and the scripted
MockProvider are interchangeable (same idea as claw-code's mock parity harness).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """One function call requested by the model. `arguments` is the raw JSON string."""

    id: str
    name: str
    arguments: str


@dataclass
class Usage:
    """Token usage of one request. DeepSeek reports cache hit/miss split of the prompt."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_hit_tokens: int = 0
    cache_miss_tokens: int = 0

    def __add__(self, other: Usage) -> Usage:
        return Usage(
            self.prompt_tokens + other.prompt_tokens,
            self.completion_tokens + other.completion_tokens,
            self.cache_hit_tokens + other.cache_hit_tokens,
            self.cache_miss_tokens + other.cache_miss_tokens,
        )

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class LLMResponse:
    """A normalised assistant turn."""

    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: Usage = field(default_factory=Usage)
    reasoning_content: str | None = None

    def to_message(self) -> dict[str, Any]:
        """Convert to an OpenAI-style assistant message for the conversation history.

        `reasoning_content` is kept: DeepSeek thinking mode with tools requires it to be sent
        back in every later request.
        """
        msg: dict[str, Any] = {"role": "assistant", "content": self.content or ""}
        if self.reasoning_content:
            msg["reasoning_content"] = self.reasoning_content
        if self.tool_calls:
            msg["tool_calls"] = [
                {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": tc.arguments}}
                for tc in self.tool_calls
            ]
        return msg


class LLMError(Exception):
    """Provider error with a user-friendly message and whether a retry could help."""

    def __init__(self, message: str, *, status: int | None = None, retryable: bool = False):
        super().__init__(message)
        self.status = status
        self.retryable = retryable


class LLMProvider(ABC):
    """Interface every provider implements."""

    name: str = "base"
    model: str = ""

    @abstractmethod
    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 8192,
    ) -> LLMResponse:
        """Send one chat request and return the normalised response."""

    def test_connection(self) -> str:
        """Cheap check that credentials work. Returns a human-readable status."""
        return f"{self.name}: ok"
