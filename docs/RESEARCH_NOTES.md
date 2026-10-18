# Research Notes — Claude Code mechanisms → Space Fractions Code Agent

Date of research: 2026-10-18. Sources were read online; facts not found in a source are marked *(unverified)*.

## 1. Windy3f3f3f3f/how-claude-code-works
A Chinese source-level deep-dive of Claude Code (v2.1.6x snapshot, ~512K lines TS, ~55 tools).
Docs: https://github.com/Windy3f3f3f3f/how-claude-code-works/tree/main/docs

- **Agent loop** (`02-agent-loop.md`): two layers. Outer `QueryEngine.submitMessage()` owns the session
  (messages, usage, cost). Inner `query()` async generator runs compact → API call → tools → recovery.
  Stops on: no tool calls, `maxTurns`, `maxBudgetUsd`, user abort, unrecoverable error.
  Recovery: output too long → raise max tokens then inject "resume" up to 3×; prompt too long → reactive compact.
- **Context engineering** (`03-context-engineering.md`): 5 levels — (1) per tool-result budget (50K chars,
  overflow saved to disk + 2KB preview), (2) history snip, (3) microcompact (old tool results → placeholder),
  (4) context collapse, (5) autocompact (~83.5% of window; disabled after 3 failures; 9-section summary;
  restores up to 5 recent files). Prompt caching: static system prompt before a dynamic boundary; CLAUDE.md
  injected as a user message, not in the system prompt. Token estimate ≈ chars/4.
- **Tool system** (`04-tool-system.md`): each tool declares `isReadOnly`, `isConcurrencySafe`,
  `validateInput`, `checkPermissions` (fail-closed defaults). Consecutive safe calls run in parallel (cap 10),
  others serially. Large output → file on disk + path + preview. Tool errors returned as `is_error`, not thrown.
  Fixed tool order keeps the prompt cache stable.
- **Code editing** (`05-code-editing-strategy.md`): `old_string` → `new_string`; fails if 0 or >1 matches
  (unless `replace_all`); file must have been fully read first and not modified since (mtime check).
  Write only for new files / full rewrites.
- **Plan mode** (`10-plan-mode.md`): read-only tools only; plan written to a file; `ExitPlanMode` asks the user.
- **Permissions** (`11-permission-security.md`): 7 defence layers; modes default/acceptEdits/plan/bypass;
  rules resolved deny > ask > allow; sensitive paths always ask; shell commands statically checked.
- **Tasks / todos** (`15-task-system.md`): TodoWrite (pending / in_progress / completed); reminder if stale.
- **System prompt** (`14-system-prompt-design.md`): static sections (intro, system, doing tasks, actions,
  using tools, tone, output efficiency) then dynamic (env, memory).
- **Observability** (`16-observability.md`): cost per model over input/output/cache-read/cache-write tokens,
  `/cost`, JSONL transcripts.
- **Minimal components** (`13-minimal-components.md`): ~500-line first version = loop + read/write/shell;
  reference build adds registry, truncation, unique edit, compaction at ~85%, retry/backoff, resume.

## 2. ultraworkers/claw-code
https://github.com/ultraworkers/claw-code — open-source Rust re-implementation of a Claude-Code-style harness (`claw`).

- Rust crates: `api` (providers, SSE), `runtime` (conversation runtime, sessions, permissions, prompts),
  `tools`, `commands`, `plugins`, `telemetry`, CLI, `compat-harness`, `mock-anthropic-service`.
- `src/` holds a Python reference (`query_engine.py`, `Tool.py`, `tool_pool.py`, `permissions.py`,
  `session_store.py`, `transcript.py`, `cost_tracker.py`, …).
- Providers: Anthropic, xAI, DashScope and any OpenAI-compatible endpoint (Ollama, vLLM, …).
- Sessions saved as `.jsonl`, resumable with `--resume`.
- `claw doctor`: checks key, model access, tools, config.
- **Mock parity harness** (`rust/MOCK_PARITY_HARNESS.md`): a local mock server replays scripted model
  responses; each scenario runs in a fresh workspace → deterministic tests (read roundtrip, write allowed/denied,
  multi-tool turn, permission prompt, auto-compact triggered, token cost reporting).

## 3. anthropics/claude-code
https://github.com/anthropics/claude-code — official repo; contains docs, changelog, **plugins** and examples
(no product source).
- Plugin layout: `.claude-plugin/plugin.json`, `commands/`, `agents/`, `skills/`, `hooks/`, `.mcp.json`.
- Hooks: PreToolUse / PostToolUse / Stop / SessionStart (e.g. security-guidance blocks risky patterns).
- `CLAUDE.md`: short, rule-style project memory file read at session start.

## 4. DeepSeek API (official docs, https://api-docs.deepseek.com)
- Base URL `https://api.deepseek.com` (OpenAI-compatible; `/beta` for strict tools). `/v1` not documented.
- Models: `deepseek-v4-pro`, `deepseek-flash` (`deepseek-v4-flash` = legacy alias). `deepseek-chat`/`deepseek-reasoner` retired 2026-07-24.
- Tools: OpenAI format, `role:"tool"` + `tool_call_id`. `tool_choice` none/auto/required/named (required/named → 400 in thinking mode).
- Thinking mode **on by default**; disable with `extra_body={"thinking":{"type":"disabled"}}`.
  With tools + thinking, `reasoning_content` must be sent back in every later request.
- Pricing per 1M tokens (off-peak; peak = 2×): v4-pro $0.022 hit / $0.66 miss / $1.98 out; flash $0.003 / $0.15 / $0.60.
  Context 1M; default max output 8K (non-thinking).
- Errors: 400, 401, 402 (insufficient balance), 422, 429 (concurrency limit), 500, 503.
- Context caching automatic; usage reports `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens`.
- **OpenRouter:** `deepseek/deepseek-v4-pro:free` and `deepseek/deepseek-v4-flash:free` do **not** exist (404).
  Free models in general: 20 req/min, 50 req/day (<10 credits bought).

## 5. Mechanism mapping (heart of the evaluation)

| # | Claude Code mechanism (source) | How the simplified agent implements it |
|---|---|---|
| 1 | Two-layer agent loop (HCC 02) | `Session` keeps history/usage/cost; `run_loop()` sends messages + tool schemas, executes tool_calls, appends `role:"tool"` results, stops on `finish`, no tool calls, max steps, max requests or budget |
| 2 | Error recovery (HCC 02) | retry + exponential backoff on 429/500/503/network; malformed tool-call JSON returned to the model as an error; `finish_reason=length` → "continue" (≤3) |
| 3 | Context engineering (HCC 03) | tool output cap with full output saved to `agent_run/tool-results/` + head/tail preview; microcompact of old tool results; auto-compact summary turn near the token budget |
| 4 | Prompt caching (HCC 03/14) | stable prefix: static system prompt + spec.json first, no timestamps, fixed tool order → DeepSeek automatic cache hits |
| 5 | Tool registry (HCC 04) | JSON-schema registry; `read_only` tools run in parallel, writes serially; errors returned as `is_error` |
| 6 | Search-and-replace editing (HCC 05) | `edit_file`: exact unique match, read-before-edit, mtime check; `write_files` batch for new files |
| 7 | Plan mode (HCC 10) | Plan phase allows only read-only tools + `update_todos`, outputs todo list + file tree |
| 8 | Permissions & sandbox (HCC 11) | all paths confined to output dir (traversal/symlink blocked), no shell, `run_python` only through the bundled interpreter with timeout, optional ask-before-write |
| 9 | TodoWrite (HCC 15) | `update_todos` with pending/in_progress/completed, live in GUI |
| 10 | System prompt design (HCC 14) | layered prompt: role → rules → tool usage → output contract → spec.json |
| 11 | CLAUDE.md memory | `AGENT_NOTES.md` written/read by the agent inside the generated project |
| 12 | Observability & cost (HCC 16) | live GUI log, `agent_run/transcript.jsonl`, tokens + cost per run, `RUN_REPORT.md` |
| 13 | Sessions / resume (claw-code) | `agent_run/state.json`, resume an interrupted run |
| 14 | `doctor` (claw-code) | "Test connection" button + `--doctor` sub-command |
| 15 | Mock parity harness (claw-code) | `MockProvider` scripted scenarios → deterministic pytest, zero API cost |
| 16 | Self-verification | `py_compile` + run generated pytest via bundled interpreter, failures fed back (bounded rounds) |
