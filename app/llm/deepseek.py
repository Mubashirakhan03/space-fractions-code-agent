"""DeepSeek official API provider (OpenAI-compatible), model `deepseek-v4-pro`.

Facts verified against https://api-docs.deepseek.com (2026-10-18):
- base URL `https://api.deepseek.com`
- thinking mode is ON by default; we disable it unless asked (cheaper). When enabled,
  `reasoning_content` must be sent back in later requests (kept by LLMResponse.to_message).
- errors: 401 bad key, 402 insufficient balance, 429 rate/concurrency limit, 500/503 server.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from app.llm.provider import LLMError, LLMProvider, LLMResponse, ToolCall, Usage

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"

RETRYABLE_STATUS = {429, 500, 502, 503}
FRIENDLY = {
    400: "Bad request format (400).",
    401: "Authentication failed (401): check your DeepSeek API key.",
    402: "Insufficient balance (402): add balance on platform.deepseek.com.",
    422: "Invalid parameters (422).",
    429: "Rate limit reached (429): waiting and retrying.",
    500: "DeepSeek server error (500).",
    503: "DeepSeek server overloaded (503).",
}


class DeepSeekProvider(LLMProvider):
    name = "DeepSeek (official)"

    def __init__(
        self,
        api_key: str,
        *,
        thinking: bool = False,
        max_retries: int = 4,
        timeout: float = 600.0,
        client: Any = None,
        sleep: Callable[[float], None] = time.sleep,
    ):
        if not api_key and client is None:
            raise LLMError("DeepSeek API key is empty.")
        self.model = DEEPSEEK_MODEL
        self.thinking = thinking
        self.max_retries = max_retries
        self._sleep = sleep
        if client is None:
            from openai import OpenAI

            # The SDK's own retries are disabled so our loop controls backoff and logging.
            client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL, timeout=timeout, max_retries=0)
        self._client = client

    def _request_kwargs(self, messages, tools, max_tokens) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "extra_body": {"thinking": {"type": "enabled" if self.thinking else "disabled"}},
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        return kwargs

    def complete(self, messages, tools=None, max_tokens=8192) -> LLMResponse:
        kwargs = self._request_kwargs(messages, tools, max_tokens)
        attempt = 0
        while True:
            try:
                raw = self._client.chat.completions.create(**kwargs)
                return self._parse(raw)
            except LLMError:
                raise
            except Exception as exc:  # map SDK / network errors to LLMError
                err = _to_llm_error(exc)
                if not err.retryable or attempt >= self.max_retries:
                    raise err from exc
                self._sleep(min(2**attempt * 2, 60))
                attempt += 1

    @staticmethod
    def _parse(raw: Any) -> LLMResponse:
        choice = raw.choices[0]
        msg = choice.message
        calls = [
            ToolCall(id=tc.id, name=tc.function.name, arguments=tc.function.arguments or "{}")
            for tc in (msg.tool_calls or [])
        ]
        u = raw.usage
        usage = Usage(
            prompt_tokens=getattr(u, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(u, "completion_tokens", 0) or 0,
            cache_hit_tokens=getattr(u, "prompt_cache_hit_tokens", 0) or 0,
            cache_miss_tokens=getattr(u, "prompt_cache_miss_tokens", 0) or 0,
        )
        return LLMResponse(
            content=msg.content,
            tool_calls=calls,
            finish_reason=choice.finish_reason or "stop",
            usage=usage,
            reasoning_content=getattr(msg, "reasoning_content", None),
        )

    def test_connection(self) -> str:
        """One tiny request (a few tokens) to validate the key and model."""
        resp = self.complete([{"role": "user", "content": "Reply with: ok"}], max_tokens=5)
        return f"Connected to {self.model} (reply: {(resp.content or '').strip()[:20]!r})"


def _to_llm_error(exc: Exception) -> LLMError:
    status = getattr(exc, "status_code", None)
    if status is not None:
        msg = FRIENDLY.get(status, f"DeepSeek API error ({status}).")
        return LLMError(msg, status=status, retryable=status in RETRYABLE_STATUS)
    name = type(exc).__name__
    if name in {"APIConnectionError", "APITimeoutError", "ConnectionError", "TimeoutError"}:
        return LLMError(f"Network problem talking to DeepSeek ({name}).", retryable=True)
    return LLMError(f"Unexpected error: {name}: {exc}")
