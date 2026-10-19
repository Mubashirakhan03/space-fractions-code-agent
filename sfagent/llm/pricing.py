"""DeepSeek price table and cost estimation (official pricing page, checked 2026-10-18).

Prices are USD per 1M tokens. Peak hours (Mon–Fri 01:00–04:00 and 06:00–10:00 UTC) cost 2×.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sfagent.llm.provider import Usage

PRICES_PER_M = {
    "deepseek-v4-pro": {"cache_hit": 0.022, "cache_miss": 0.66, "output": 1.98},
}
PEAK_HOURS_UTC = [(1, 4), (6, 10)]


def is_peak(at: datetime | None = None) -> bool:
    """True if `at` (default: now) falls in DeepSeek's weekday peak window."""
    at = (at or datetime.now(UTC)).astimezone(UTC)
    if at.weekday() >= 5:
        return False
    return any(start <= at.hour < end for start, end in PEAK_HOURS_UTC)


def estimate_cost(usage: Usage, model: str = "deepseek-v4-pro", at: datetime | None = None) -> float:
    """Estimated USD cost of `usage`. Unknown models (e.g. the mock) cost 0."""
    price = PRICES_PER_M.get(model)
    if price is None:
        return 0.0
    hit = usage.cache_hit_tokens
    miss = usage.cache_miss_tokens or max(usage.prompt_tokens - hit, 0)
    cost = (hit * price["cache_hit"] + miss * price["cache_miss"] + usage.completion_tokens * price["output"]) / 1e6
    return cost * (2 if is_peak(at) else 1)
