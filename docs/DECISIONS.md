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
| D-012 | 2026-10-19 | Agent is **generic**: system prompt/output contract contain no app-specific content; task hints live in optional **task profiles** (`profiles/*.md`, YAML front matter `name`, `required_files`) chosen in the GUI and appended to the spec message | Evaluation of a code agent, not a hard-coded generator; keeps cached prefix stable | Hard-coded Space Fractions contract |
| D-013 | 2026-10-19 | Second sample `samples/library_tracker/` tested in mock mode and unit tests only (no paid run) | Shows generality at zero cost | Real run on it |
| D-014 | 2026-10-19 | Frozen exe copies bundled `samples/` and `profiles/` once to `Documents\SpaceFractionsAgent\` and pre-fills from there | `_MEI…` temp folder disappears when the exe exits | Point at `_MEI` |
| D-015 | 2026-10-19 | GUI: light theme, one accent colour (#2563EB), cards, phase states pending/running/done/failed/stopped/skipped, colour-coded log, window sized to fit the screen (max 1400×850) | Readable in a YouTube video; works with 125–150 % display scaling | Dark/system theme, fixed size |
| D-016 | 2026-10-19 | Never hand-edit generated code; when a real run shows a problem, improve the agent (prompt rules, tools, verification) and re-run | PROMPT §1 critical rule; makes the agent better for any input | Patch the generated game |
| D-017 | 2026-10-19 | Final example = real run 4 (`examples/space_fractions_run4`); runs 1–3 kept as evidence; remaining issues documented as known limitations | Run 4 is the most robust (no freeze, correct feedback); honesty over cherry-picking | Keep re-running until perfect |
| D-018 | 2026-10-19 | Default token cap 6M (cumulative, mostly cache hits); the cost cap ($1) is the real spending guard | Run 4 hit the 2M cap at only $0.136 | Keep 2M |
| D-019 | 2026-10-19 | Final example = **real run 5** (`examples/space_fractions_run5`), replacing run 4: it fits 1100×750, has a Check button for typed answers, a full pause overlay and 41 tests; its in-run FAILED verdict was a probe false positive (scrollable list), re-verified OK with the fixed probe | User rule: "if run 5 is better than run 4, make it final"; honesty: the original RUN_REPORT is kept unchanged and the re-verification is a separate file | Keep run 4 |
