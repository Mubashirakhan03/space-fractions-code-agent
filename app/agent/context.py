"""Context engineering (simplified version of Claude Code's multi-level compression).

Level 1 — tool-result cap: long outputs are saved to agent_run/tool-results/ and the model gets
          a head + tail preview with the file path.
Level 2 — microcompact: once the conversation passes half the token budget, old tool results are
          replaced by a short placeholder (the files are still on disk and can be re-read).
Level 3 — auto-compact: near the budget, the middle of the conversation is summarised by the model
          (no tools) and replaced by that summary; system prompt, spec and recent turns are kept and
          the current phase instructions are restated.
The fixed, cached prefix (system prompt + spec) is not counted against the budget — only the part
of the conversation that grows. Token counts are estimated as characters / 4.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.llm.provider import LLMProvider, LLMResponse

CHARS_PER_TOKEN = 4
PLACEHOLDER = "[older tool result cleared to save context — re-run the tool if you need it again]"

COMPACT_PROMPT = """You are summarising the earlier part of a coding-agent session so it can continue with less
context. Write a concise summary with these sections:
1. Task and constraints  2. Design decisions taken  3. Files created/changed (path → purpose)
4. Errors met and how they were fixed  5. Current todo state  6. What to do next.
Do not call tools. Plain text only."""


def estimate_tokens(messages: list[dict[str, Any]]) -> int:
    return len(json.dumps(messages, ensure_ascii=False)) // CHARS_PER_TOKEN


class ContextManager:
    def __init__(self, run_dir: Path, *, max_tool_chars: int = 8000, budget_tokens: int = 120_000,
                 compact_ratio: float = 0.8, keep_recent: int = 8, head_messages: int = 2, min_middle: int = 4):
        self.results_dir = Path(run_dir) / "tool-results"
        self.max_tool_chars = max_tool_chars
        self.budget_tokens = budget_tokens
        self.compact_ratio = compact_ratio
        self.keep_recent = keep_recent
        self.head_messages = head_messages  # system prompt + spec message are never touched (cache prefix)
        self.min_middle = min_middle  # don't spend a request summarising only a couple of messages
        self._seq = 0

    # ---- level 1 ----
    def cap_tool_output(self, name: str, content: str) -> str:
        if len(content) <= self.max_tool_chars:
            return content
        self._seq += 1
        self.results_dir.mkdir(parents=True, exist_ok=True)
        path = self.results_dir / f"{self._seq:03d}_{name}.txt"
        path.write_text(content, encoding="utf-8")
        head, tail = content[: self.max_tool_chars * 2 // 3], content[-self.max_tool_chars // 4:]
        cut = len(content) - len(head) - len(tail)
        return (f"{head}\n\n... [{cut} characters truncated; full output saved to agent_run/tool-results/{path.name} "
                f"— read it with read_file offset/limit if needed] ...\n\n{tail}")

    # ---- level 2 ----
    def microcompact(self, messages: list[dict[str, Any]]) -> int:
        """Clear old tool results in place. Returns how many were cleared."""
        if self.growing_tokens(messages) < self.budget_tokens // 2:
            return 0
        tool_idx = [i for i, m in enumerate(messages) if m.get("role") == "tool"]
        cleared = 0
        for i in tool_idx[: -self.keep_recent]:
            if len(messages[i].get("content", "")) > 300 and messages[i]["content"] != PLACEHOLDER:
                messages[i] = {**messages[i], "content": PLACEHOLDER}
                cleared += 1
        return cleared

    # ---- level 3 ----
    def growing_tokens(self, messages: list[dict[str, Any]]) -> int:
        return estimate_tokens(messages[self.head_messages:])

    def needs_compaction(self, messages: list[dict[str, Any]]) -> bool:
        return self.growing_tokens(messages) > self.budget_tokens * self.compact_ratio

    def split_point(self, messages: list[dict[str, Any]]) -> int | None:
        """Index where the kept tail starts. Never starts on a `tool` message, so every kept
        tool result still has its assistant tool_call in front of it."""
        i = max(len(messages) - self.keep_recent, self.head_messages + 1)
        while i < len(messages) and messages[i].get("role") == "tool":
            i += 1
        return i if i - self.head_messages >= self.min_middle and i < len(messages) else None

    def compact(self, messages: list[dict[str, Any]], provider: LLMProvider,
                restate: str | None = None) -> tuple[list[dict[str, Any]], LLMResponse]:
        cut = self.split_point(messages)
        if cut is None:
            raise ValueError("nothing to compact")
        middle = messages[self.head_messages:cut]
        rendered = "\n\n".join(f"[{m['role']}] {_short(m)}" for m in middle)
        resp = provider.complete([{"role": "system", "content": COMPACT_PROMPT},
                                  {"role": "user", "content": rendered}], tools=None, max_tokens=2000)
        text = "Summary of the earlier part of this session (auto-compacted):\n\n" + (resp.content or "(empty)")
        if restate:
            text += "\n\n---\nCurrent phase instructions (restated):\n" + restate
        summary = {"role": "user", "content": text}
        tail = messages[cut:]
        if tail and tail[0].get("role") == "user":  # keep strict user/assistant alternation readable
            tail = [{"role": "assistant", "content": "Understood, continuing."}, *tail]
        return [*messages[: self.head_messages], summary, *tail], resp


def _short(m: dict[str, Any], limit: int = 1500) -> str:
    text = str(m.get("content") or "")
    if m.get("tool_calls"):
        text += " CALLS: " + ", ".join(f"{c['function']['name']}({c['function']['arguments'][:200]})"
                                      for c in m["tool_calls"])
    return text if len(text) <= limit else text[:limit] + " …"
