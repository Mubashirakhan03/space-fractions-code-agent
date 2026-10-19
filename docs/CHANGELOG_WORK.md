# Work Change Log (backup & rollback guide)

Every change is recorded here: what changed, why, which files, the commit, and **how to undo it**.

## How to roll back
| I want to… | Command |
|---|---|
| See all restore points | `git tag` and `git log --oneline` |
| Undo one commit (safe, keeps history) | `git revert <commit-hash>` then `git push` |
| Look at the project as it was at a phase | `git checkout phase-N` (go back: `git checkout main`) |
| Restore one file from a phase | `git checkout phase-N -- path/to/file` |
| Throw away uncommitted local edits to a file | `git restore path/to/file` |

Original inputs are also kept untouched in `D:\professor project\Task1\`.

---

## Entries

### 2026-10-18 — Phase 0 (research & setup)
- **Created** folder `space-fractions-code-agent/` with `docs/` and `samples/`.
- **Copied** `PROMPT (1).md` → `docs/PROMPT.md`; `Task1-EN.docx`, `Architecture_Documentation.md`,
  `Architecture_View.md` → `docs/`; the two `.md` inputs → `samples/`.
- **Copied** `Task1/env` → `.env` (secret, gitignored).
- **Added** `.gitignore` (secrets, Python, build outputs).
- **Added** docs: `RESEARCH_NOTES.md`, `DECISIONS.md`, `CHANGELOG_WORK.md`, `PROGRESS.md`, `LEARNING_NOTES_UR.md`.
- Commit: `d37cc8f` — tag `phase-0`
- Rollback: delete the `space-fractions-code-agent/` folder; `Task1/` is unchanged.

### 2026-10-18 — Phase 1 start (git + GitHub)
- Installed GitHub CLI 2.102.0 (`winget install GitHub.cli`); user logged in as `Mubashirakhan03`.
- `git init -b main`, identity `Mubashira <mubashirakhan1001@gmail.com>`; verified `.env` ignored (`git check-ignore`).
- Added `.env.example`, `LICENSE` (MIT), starter `README.md`.
- Created public repo https://github.com/Mubashirakhan03/space-fractions-code-agent and pushed `main` + tag `phase-0`.
- Recorded scope decisions D-008…D-011 (only deepseek-v4-pro, DeepSeek + Mock only, mock-only dev, stop before paid runs).
- Commit: `d37cc8f` (same first commit)
- Rollback: `gh repo delete Mubashirakhan03/space-fractions-code-agent` (irreversible, ask first) / `rm -rf .git`.

### 2026-10-18 — Phase 1 (skeleton, config, providers, parsers)
- `.venv` (Python 3.12) with openai 3.35, customtkinter 6.0, PyYAML, python-dotenv, jsonschema, pytest, ruff, pyinstaller.
- Added `pyproject.toml` (ruff + pytest config), `requirements.txt`, `requirements-dev.txt`, `.gitattributes`.
- `b04d26d` feat(llm): `app/llm/provider.py` (interface + types), `deepseek.py` (v4-pro only, thinking off, retry/backoff,
  friendly 401/402 errors), `mock.py` (scripted, zero cost), `pricing.py` (off-peak/peak), `app/config.py`
  (%APPDATA% config, env/.env key, `mask_key`). Tests: `test_config.py`, `test_providers.py`.
- `b84f0b0` feat(parser): `app/parsers/doc_parser.py`, `uml_parser.py`, `spec.py` + `schemas/spec.schema.json`.
  Tests: `test_doc_parser.py`, `test_uml_parser.py`, `test_spec.py` (35 tests total, all passing, ruff clean).
- (this commit) `scripts/check_secrets.py` + `scripts/install_hooks.py` — pre-commit hook blocks keys (verified with a fake key).
- Rollback: `git revert <hash>` for one commit, or `git checkout phase-0 -- <file>`; whole phase: `git reset --hard phase-0` (destructive, ask first).

### 2026-10-18 — Phase 2 (tools, sandbox, agent loop, context, prompts)
- `abc710f` feat(tools): `app/tools/sandbox.py` (path guard, harness dir read-only, blocked script types, ReadState
  read-before-edit + mtime), `registry.py` (JSON-schema tools, mode permissions, parallel read-only batches,
  errors as results), `builtin.py` (list_dir, read_file, glob, search_text, write_file, write_files, edit_file,
  run_python, update_todos, submit_plan, finish), `runner.py` (bundled interpreter via `app.main --run-pytest/
  --run-script`, timeout + process-tree kill, secrets stripped from env), `app/main.py` (hidden sub-commands),
  `app/agent/planner.py` (TodoList). Tests: `tests/test_tools.py`.
- `087b40e` feat(agent): `app/agent/loop.py` (two-layer loop + pipeline plan → implement → verify ⇄ fix → report,
  limits, resume), `context.py` (tool-output cap → disk, microcompact, auto-compact with restated instructions;
  cached prefix not counted), `prompts.py` (layered system prompt + output contract + compact spec), `state.py`,
  `transcript.py`, `replay.py` (ReplayProvider), `report.py` (RUN_REPORT.md, required deliverables).
  Tests: `tests/test_agent_loop.py` (15 mock end-to-end scenarios). Total 74 passed, 1 skipped (symlink test on Windows).
- Measured fixed prompt prefix ≈ 5.2K tokens (system 1.4K + compact spec 2.9K + tool schemas 1K).
- Rollback: `git revert 087b40e` / `git revert abc710f`, or `git checkout phase-1 -- app/` to restore Phase 1 code.

### 2026-10-18 — Phase 3 (GUI)
- `04c72c5` feat(gui): `app/gui/app.py` (customtkinter window: provider/key, inputs, output, limits, fixed action bar,
  phase strip, MOCK/REPLAY banner, tabs Log/Todos/Spec preview/Report, usage+cost line), `app/gui/controller.py`
  (worker thread + queue, provider factory, ask-before-write bridge, input pre-fill, launch generated game),
  `app/llm/demo_script.py` (scripted MOCK DEMO project, clearly labelled as not LLM-generated).
  Tests: `tests/test_gui.py` (controller + real-window smoke run). Total 81 passed, 1 skipped.
- New runs require an empty output folder (prevents mixing two runs; nothing is ever deleted).
- Paid run asks for confirmation with prices and the run's hard limits.
- Screenshot: `docs/screenshots/gui_mock_run.png`. Pillow installed in `.venv` only for screenshots (not a dependency).
- Verified manually: "Run generated game" opens the generated Tk window via the bundled interpreter.
- Rollback: `git revert 04c72c5` or `git checkout phase-2 -- app/` (GUI files are new, so revert removes them).

### 2026-10-18 — Phase 4 (exe build, verification, CI)
- `a193ed2` build: `SpaceFractionsAgent.spec` (one-file, windowed, icon; bundles customtkinter assets, openai SDK,
  pytest via `pytest.freeze_includes()`, samples, schema, and the stdlib list in `app/bundled.py`), `run_agent.py`
  entry, `scripts/build_exe.bat`, `scripts/make_icon.py` → `assets/icon.ico/.png`, `app/selftest.py`
  (`--doctor`, `--self-test`), `scripts/verify_exe.py`, `.github/workflows/build-windows.yml`.
- System prompt now lists exactly the bundled stdlib modules (generated code can only use what the exe contains).
- Local build: `dist/SpaceFractionsAgent.exe` 26.1 MB in ~1 min. `verify_exe.py` with PATH = Windows dirs only:
  6/6 PASS (--version, --doctor, --self-test incl. child-exe pytest "2 passed", --run-script frozen=True,
  GUI window, generated game window).
- Note: "no Python" is simulated by stripping PATH/PYTHON* env vars; a clean-PC test (e.g. Windows Sandbox or
  another laptop) is still recommended before submission.
- Rollback: `git revert a193ed2`; build outputs (`build/`, `dist/`) are gitignored and can simply be deleted.
- CI run 39153253009 on windows-latest: lint, 81 tests, build and verify_exe 6/6 PASS on a clean GitHub runner;
  artifact `SpaceFractionsAgent-windows` uploaded.
- Bumped actions to checkout@v7, setup-python@v7, upload-artifact@v7, action-gh-release@v3 (Node 20 deprecation).
- CI run 39153490927 green with Node 24 actions (no warnings).
- `max_output_tokens` default 8192 → 32768 and implement prompt asks for 4-6 files per `write_files` call
  (a full module batch does not fit in 8K output tokens; a cut-off reply would break the tool-call JSON).

### 2026-10-19 — Pre-Phase-5 improvements (user request: generic agent + GUI polish)
- `e8bf914` feat(agent): generic system prompt + output contract; `app/agent/profile.py`; `profiles/space_fractions.md`;
  generic required deliverables (+ profile `required_files`); `samples/library_tracker/`; samples/profiles copied
  to `Documents\SpaceFractionsAgent` in the exe; parser testing-matrix lookup made generic. Tests: `tests/test_generic.py`.
- (this commit) feat(gui): redesigned window (`app/gui/app.py`, new `app/gui/theme.py`): header + subtitle +
  provider/model badge, cards with labels, phase bar with states incl. "skipped (not needed)", colour-coded log,
  status bar (requests / tokens / cache-hit % / cost / elapsed), fit-to-screen sizing, friendly key/balance errors
  (`friendly_key_problem`, DeepSeek 401/402 messages). README: "The agent is generic" + "How to use with your own
  architecture docs". Screenshots: `docs/screenshots/gui_idle.png`, `gui_mock_run.png`.
- `scripts/verify_exe.py`: only counts NEW windows (ignores windows the user already has open) and kills both
  bootloader and child processes.
- Tests: 94 passed, 1 skipped. New exe built to `build/dist_new/` (old one was locked by open windows), verified
  6/6 PASS without Python, then copied to `dist/`.
- Rollback: `git revert <this hash>` (GUI) and/or `git revert e8bf914` (generic agent); `git checkout phase-4 -- app/`.

### 2026-10-19 — UI/UX round 2 (user request: 4 items + maximized apps)
- GUI: success dialog "Project generated successfully! … Tests: PASSED" with Run generated app / Open folder /
  Close, green banner; failure/stop → red banner + dialog with the reason and "View report".
- "Run generated app" enabled only when the selected folder holds a completed, verified run (`run_succeeded`);
  then bold green with a pulsing border; disabled/grey otherwise (re-checked when the folder changes).
- Non-empty output folder → dialog: Create new subfolder `run-YYYY-MM-DD_HHMM` (recommended) / Overwrite
  (deletes ONLY files recorded in the previous run's state + `agent_run/`; user files kept) / Resume / Cancel.
- API key button toggles "👁 Show" ⇄ "🙈 Hide".
- Agent: generic **UI quality rules** in the system prompt (≥1100×750, maximized, F11/Esc, big fonts, hover
  buttons, Enter submits, auto-clear input, coloured feedback, screens as Frames + `create_app(root)`);
  `tests/test_ui_smoke.py` is now a required deliverable and verify checks it asserts `minsize`.
  Kid-friendly rules added to `profiles/space_fractions.md` (space theme, 36/30/20 pt fonts, progress, pause,
  feedback then auto-next, end screen with stars + confetti).
- Mock demo (clearly labelled MOCK): maximized space-themed window, 3 questions, auto-clear, coloured feedback,
  Congratulations screen with stars + confetti, its own headless UI smoke test.
- Robustness found while testing: re-creating `tk.Tk()` after `destroy()` can crash the frozen exe on Windows
  (fatal 0x80000003) and Tk init can fail transiently ("Can't find a usable init.tcl"). Fixes: ONE session Tk
  root in UI tests (rule also added to the system prompt), retries for Tk creation, `create_window()` retry in
  the GUI launcher, test teardown cancels pending `after()` callbacks.
- Tests: 98 passed, 1 skipped. Frozen exe: demo UI tests 8/8 runs green; verify_exe 2/2 ALL PASSED.
- Screenshots: `docs/screenshots/gui_success.png`, `mock_demo_feedback.png`, `mock_demo_end.png`.
- Rollback: `git revert <this hash>`.

### 2026-10-19 — Phase 5, real run 1 + agent improvements
- `scripts/run_agent_cli.py`: headless run (same Agent as the GUI) printing one line per event.
- Balance check via `GET /user/balance` (no tokens): $2.00 topped up.
- Real run 1 (deepseek-v4-pro, profile space_fractions): 40 requests → stopped at cap → Resume +4 → completed,
  VERIFY PASSED, $0.103 total. Saved as `examples/space_fractions_run1/` (+ CLI logs). Details: `docs/REAL_RUNS.md`.
- Visual check found canvas drawn with `winfo_width()==1` (stars collapsed, title/question text invisible).
  NOT fixed by hand. Instead: `app/agent/ui_probe.py` (harness UI layout probe in Verify), new UI rules in the system
  prompt (<Configure> drawing, create_app/screens/show contract), batch-edit rule; mock demo follows the contract.
  Tests: `tests/test_ui_probe.py` (bad layout flagged, good passes, crashing screen flagged, no-UI skipped).
- Tests: 102 passed, 1 skipped.
- Rollback: `git revert <this hash>`; run-1 folder can be deleted without affecting the agent.

### 2026-10-19 — Generic UI style: "UI design brief"
- System prompt: removed all app-specific style words (stars/planets, "question/game" examples, children);
  style now comes from a **UI design brief** the agent derives from the spec in the Plan phase and writes as
  DESIGN_DECISIONS.md section 5 (users, mood, hex palette with roles, fonts, layout, key screens). Examples:
  Tic-Tac-Toe → playful big 3x3 board; library tracker → calm, table based; learning app → bright, encouraging.
  Implement phase must follow it (palette/fonts in ui/theme.py). Generic quality rules kept.
- `submit_plan` rejects design_decisions without a "UI design brief" section.
- Tests: generic prompt contains none of 21 Space-Fractions words (whole-word check, stdlib module names excluded);
  plan/contract/implement mention the brief; submit_plan brief enforcement. 120 passed, 1 skipped.

### 2026-10-19 — Phase 5, real run 2 (final example)
- Run 2 with the improved agent: completed on the first attempt, VERIFY PASSED + UI PROBE OK on 9 screens,
  27 requests, $0.096 (balance $1.89 → $1.72). Output: `examples/space_fractions_generated/` (+ `agent_run/cli_log.txt`).
- Screenshots of every screen: `docs/screenshots/run2/`. Findings (incl. the feedback-shows-next-answer logic bug,
  left unedited) in `docs/REAL_RUNS.md`. `.gitignore`: `examples/**/*.db` (created when the generated app runs).

### 2026-10-19 — Option B: agent rules from run 2's findings (Run 3 deferred to off-peak, after 15:00 PKT)
- System prompt rule 10: compute every value a user-visible message needs BEFORE advancing/mutating state and
  test every message incl. the wrong-input path (generic wording — targets run 2's "feedback shows the next
  item's expected value" bug). UI smoke test must cover one correct AND one wrong submission. New rule: buttons
  never cover text on text-heavy screens.
- UI probe: detects a button covering a text label on the visible screen (flags run 2's Help screen, no false
  positives on its other 8 screens); a broken `ui/app.py` is now a failure instead of "skipped".
- Tests: 123 passed, 1 skipped.
