# Changelog

## [1.0.1] — unreleased

### Changed
- `write_files` takes `files` as an object keyed by path (`{"pkg/a.py": "<full content>"}`), so a path can no
  longer be lost. In run 7, 6 of 12 calls in the old list form dropped `"path"` and the files had to be re-sent.
  The list form still works; a missing path now points the model to the object form.
- Generic rules: every screen/scene the spec names is implemented; a movie/animation in the spec becomes a 5–10 s
  Canvas animation with moving objects, Skip and auto-advance; administrator-type roles get an in-window PIN screen;
  every choice item has exactly one option that satisfies the prompt. The first message lists the spec's own names
  ("Harness checklist"), and the UI probe fails a missing animation, Skip button or masked PIN input.
- Generic rule: a role that updates / manages / maintains records gets a list of all records (seed data
  included) with Add, Edit and Delete, each tested; the UI probe fails an empty list while seed data exists, or a
  missing Add / Edit / Delete button.
- Mock demo: animated intro with Skip, an admin PIN screen and an admin list with Add / Edit / Delete.
- Final example is real run 9 (`examples/space_fractions_run9_final/`, profile none), with re-verification evidence
  `docs/run9_reverification.txt` and screenshots `docs/screenshots/run9/`. Runs 7 and 8 are kept.

### Fixed
- Verify now runs an **import check**: it imports every module and loads `main.py` without running `main()`. A wrong
  import (e.g. `from ui.widgets import centered` when `centered` does not exist) fails verification and goes to a fix
  round, instead of crashing on "Run generated app". The system prompt tells the model about this check.
- "Create a new run folder" no longer nests runs: if the chosen folder is itself a run folder (it holds `agent_run/`
  or has a `run-…` name), the new run is created next to it. The dialog shows the full path.
- Resume shows the phases completed in the previous session as **done**, not pending.
- Mock demo end screen: 0–3 stars (0 correct → 0 stars) and a score-dependent message ("Good try! Keep
  practising" / "Well done!" / "Congratulations!"); confetti only for a full score.
- Space Fractions profile and the generic prompt: result screens must match the outcome (no praise or positive
  rating for a zero score).
- Generic rules: add/edit forms must include every field the entity needs (e.g. answer and choices) with no
  silent hard-coded defaults; apps must ship with seed data loaded on first start (≥ 20 items for quiz-style
  apps); `create_app` sets a real window title. The UI probe now fails a default "tk" title (a title set in
  `main.py` is accepted).
- Generic rule for quiz/practice apps (any profile): every round draws items at random from the whole pool
  (seed + admin-added) and shuffles them; computable content (math, arithmetic, number patterns…) is also
  generated in code each round with computed answers and distinct wrong choices; tests for all of this.
- UI probe: re-checks once after bringing the window to the front if nothing is mapped (removes a flaky false alarm).
- Space Fractions profile: ≥ 20 seed questions plus fraction questions generated in code for every round
  (equivalent, compare, add/subtract, simplify; answers via `fractions.Fraction`); full admin form.
- The agent's own package is renamed `app` → `sfagent`, so generated projects can have their own `app/` package
  (before, every script/test failed when they did).
- Default max agent steps 100 (was 60; migrated). Generator tests must recompute expected values independently and
  reject ambiguous items; text inputs must be visibly distinct (and the UI probe checks it).
- Default max LLM requests per run is now 80 (and the token cap 6M); older saved settings with the old defaults are
  migrated automatically.

## [1.0.0] — 2026-10-19

First public release for the Task 1 evaluation.

### Added
- Windows desktop app `SpaceFractionsAgent.exe` (one file, no Python needed) with a customtkinter GUI: DeepSeek key +
  test connection, input pickers, optional task profile, output folder, hard limits (cost, requests), live phases,
  log, todos, cost, a result dialog, Resume, Replay and Run generated app.
- Simplified Claude-Code-style agent: two-layer loop; plan mode; sandboxed tool registry (`list_dir`, `read_file`,
  `glob`, `search_text`, `write_file(s)`, `edit_file`, `delete_file`, `run_python`, `update_todos`, `submit_plan`,
  `finish`); context management; prompt caching; resume/replay; transcript; cost accounting.
- Deterministic Markdown + PlantUML parsers → `spec.json` with JSON Schema and automatic input-issue detection.
- Harness verification: deliverables, compile, pytest via the bundled interpreter, and a UI layout probe that
  opens the real window.
- Generic system prompt with a UI design brief; optional task profiles (`profiles/space_fractions.md`).
- DeepSeek `deepseek-v4-pro` provider (official API, thinking off, retry/backoff), MockProvider, ReplayProvider.
- 134 tests (MockProvider only), ruff, CI on windows-latest that builds and verifies the exe.
- Five real runs with transcripts in `examples/` (final: `space_fractions_run5`), documented in `docs/REAL_RUNS.md`.
