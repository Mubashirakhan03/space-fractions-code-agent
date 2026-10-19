# Changelog

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
- 128 tests (MockProvider only), ruff, CI on windows-latest that builds and verifies the exe.
- Four real runs with transcripts in `examples/` (final: `space_fractions_run4`), documented in `docs/REAL_RUNS.md`.
