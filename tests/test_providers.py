from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app.llm.deepseek import DEEPSEEK_MODEL, DeepSeekProvider
from app.llm.mock import MockProvider, reply, tool_call
from app.llm.pricing import estimate_cost, is_peak
from app.llm.provider import LLMError, LLMResponse, Usage


def _raw(content="hi", tool_calls=None, reasoning=None, finish="stop"):
    msg = SimpleNamespace(content=content, tool_calls=tool_calls, reasoning_content=reasoning)
    usage = SimpleNamespace(prompt_tokens=100, completion_tokens=20,
                            prompt_cache_hit_tokens=60, prompt_cache_miss_tokens=40)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg, finish_reason=finish)], usage=usage)


class FakeClient:
    """Stands in for openai.OpenAI; records kwargs and returns queued results/exceptions."""

    def __init__(self, *results):
        self.results = list(results)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        r = self.results.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


class StatusError(Exception):
    def __init__(self, status):
        super().__init__(f"status {status}")
        self.status_code = status


def test_deepseek_request_uses_v4_pro_and_disables_thinking():
    client = FakeClient(_raw())
    p = DeepSeekProvider("", client=client)
    p.complete([{"role": "user", "content": "x"}], tools=[{"type": "function"}])
    kw = client.calls[0]
    assert kw["model"] == DEEPSEEK_MODEL == "deepseek-v4-pro"
    assert kw["extra_body"] == {"thinking": {"type": "disabled"}}
    assert kw["tool_choice"] == "auto"


def test_deepseek_parses_tool_calls_usage_and_reasoning():
    tc = SimpleNamespace(id="c1", function=SimpleNamespace(name="read_file", arguments='{"path":"a"}'))
    p = DeepSeekProvider("", client=FakeClient(_raw(None, [tc], reasoning="think", finish="tool_calls")),
                         thinking=True)
    r = p.complete([])
    assert r.tool_calls[0].name == "read_file"
    assert r.usage.cache_hit_tokens == 60 and r.usage.cache_miss_tokens == 40
    msg = r.to_message()
    assert msg["reasoning_content"] == "think"  # must be passed back in thinking mode
    assert msg["tool_calls"][0]["function"]["arguments"] == '{"path":"a"}'


def test_deepseek_retries_429_then_succeeds():
    sleeps = []
    client = FakeClient(StatusError(429), StatusError(503), _raw("ok"))
    r = DeepSeekProvider("", client=client, sleep=sleeps.append).complete([])
    assert r.content == "ok"
    assert len(sleeps) == 2


@pytest.mark.parametrize("status,text", [(401, "API key"), (402, "balance")])
def test_deepseek_non_retryable_errors_are_friendly(status, text):
    client = FakeClient(StatusError(status))
    with pytest.raises(LLMError) as ei:
        DeepSeekProvider("", client=client, sleep=lambda s: None).complete([])
    assert text in str(ei.value)
    assert len(client.calls) == 1


def test_deepseek_requires_key():
    with pytest.raises(LLMError):
        DeepSeekProvider("")


def test_mock_provider_scripted_and_callable_steps():
    mock = MockProvider([reply(tool_call("list_dir", path=".")),
                         lambda msgs, tools: LLMResponse(content=f"saw {len(msgs)} msgs")])
    r1 = mock.complete([{"role": "user", "content": "go"}])
    assert r1.tool_calls[0].name == "list_dir" and r1.finish_reason == "tool_calls"
    r2 = mock.complete([{"role": "user", "content": "go"}, {"role": "tool", "content": "x"}])
    assert r2.content == "saw 2 msgs"
    assert r2.usage.total_tokens > 0
    with pytest.raises(LLMError):
        mock.complete([])


def test_cost_estimate_off_peak_and_peak():
    usage = Usage(prompt_tokens=1_000_000, completion_tokens=1_000_000,
                  cache_hit_tokens=0, cache_miss_tokens=1_000_000)
    saturday = datetime(2026, 10, 17, 12, tzinfo=UTC)
    tuesday_peak = datetime(2026, 10, 20, 7, tzinfo=UTC)
    assert not is_peak(saturday) and is_peak(tuesday_peak)
    assert estimate_cost(usage, at=saturday) == pytest.approx(0.66 + 1.98)
    assert estimate_cost(usage, at=tuesday_peak) == pytest.approx(2 * (0.66 + 1.98))
    assert estimate_cost(usage, model="mock") == 0.0
