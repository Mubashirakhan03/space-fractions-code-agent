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
