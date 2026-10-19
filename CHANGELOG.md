# Changelog

## [1.0.1] — unreleased

### Fixed
- Verify now runs an **import check**: it imports every module and loads `main.py` without running `main()`. A wrong
  import (e.g. `from ui.widgets import centered` when `centered` does not exist) fails verification and goes to a fix
  round, instead of crashing on "Run generated app". The system prompt tells the model about this check.
- "Create a new run folder" no longer nests runs: if the chosen folder is itself a run folder (it holds `agent_run/`
  or has a `run-…` name), the new run is created next to it. The dialog shows the full path.
- Resume shows the phases completed in the previous session as **done**, not pending.
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
