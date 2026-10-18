# Decision Log

Each decision: ID, date, decision, reason, alternatives. Newest at the bottom.

| ID | Date | Decision | Reason | Alternatives considered |
|---|---|---|---|---|
| D-001 | 2026-10-18 | Repo folder `D:\professor project\space-fractions-code-agent\`; original `Task1/` kept untouched | `Task1/` is the pristine backup of the inputs | Work inside `Task1/` |
| D-002 | 2026-10-18 | DeepSeek base URL `https://api.deepseek.com` | Only URL in official docs; `/v1` undocumented | `/v1` |
| D-003 | 2026-10-18 | Model selector: `deepseek-v4-pro` (default) + `deepseek-flash` | Official ids; `deepseek-v4-flash` is a legacy alias | `deepseek-v4-flash` |
| D-004 | 2026-10-18 | Thinking disabled by default via `extra_body.thinking.type=disabled`; when enabled, pass `reasoning_content` back | API default is thinking ON; omitting `reasoning_content` with tools → HTTP 400 | Rely on default |
| D-005 | 2026-10-18 | OpenRouter + Custom providers keep an editable model id; demo provider decided in Phase 5 | No `:free` DeepSeek V4 route exists on OpenRouter | Hard-code a `:free` id |
| D-006 | 2026-10-18 | `.env` copied from `Task1/env`, gitignored before `git init`; `api-keys-backup.txt` never enters the repo | Secret safety | — |
| D-007 | 2026-10-18 | Python 3.12 (installed), GUI customtkinter, PyInstaller onefile | Matches PROMPT §4; 3.12 ≥ 3.11 | Install 3.11 |
| D-008 | 2026-10-18 | **Only `deepseek-v4-pro`** via official API `https://api.deepseek.com`. `deepseek-flash` dropped completely: no GUI option, no flash runs. **Supersedes D-003** | Professor requires deepseek-v4-pro | Keep flash as fallback |
| D-009 | 2026-10-18 | Providers = **DeepSeek official + MockProvider (+ replay mode)** only. OpenRouter / Custom providers and the free plan dropped. **Supersedes D-005** and PROMPT §4.1b items 2–3 | No free DeepSeek V4 route exists; keep scope tight | OpenRouter paid, custom endpoint |
| D-010 | 2026-10-18 | All development and tests run on **MockProvider only** (zero cost) | Limited budget | — |
| D-011 | 2026-10-18 | Before any real API call (Phase 5): STOP, tell the user the exact balance to add on platform.deepseek.com (with safety margin), runs covered and cost per run; wait for the user's confirmation | User pays and tops up personally | — |
