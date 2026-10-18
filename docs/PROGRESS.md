# Progress Tracker

Read this first when resuming work in a new session.

**Last updated:** 2026-10-18
**Current phase:** Phase 4 done (tag `phase-4`) → next: Phase 5 (ONE real DeepSeek run) — WAITING for user to add balance

| Phase | Status | Tag |
|---|---|---|
| 0 — Research & plan | ✅ done | `phase-0` |
| 1 — Skeleton, config, providers, parsers | ✅ done | `phase-1` |
| 2 — Tools, sandbox, loop, context, prompts | ✅ done | `phase-2` |
| 3 — GUI | ✅ done | `phase-3` |
| 4 — Exe build + GitHub Actions | ✅ done | `phase-4` |
| 5 — One real run → examples/ | ⏸ waiting for balance | |
| 6 — README, video script, release | ⬜ | |

## Environment facts
- Python 3.12.6 via `py`; tkinter 8.6; sqlite 3.45 — OK
- git 2.51; gh 2.102 at `C:\Program Files\GitHub CLI\gh.exe` (logged in as Mubashirakhan03)
- Repo: https://github.com/Mubashirakhan03/space-fractions-code-agent
- `.venv` with all deps; run tests: `.venv/Scripts/python -m pytest`; lint: `.venv/Scripts/python -m ruff check .`
- Pre-commit secret hook: `python scripts/install_hooks.py` (re-run after a fresh clone)

## Scope decisions (2026-10-18, see DECISIONS.md D-008…D-011)
- Model: **only `deepseek-v4-pro`**, official API `https://api.deepseek.com`. No flash anywhere.
- Providers: **DeepSeek official + MockProvider (+ replay)**. No OpenRouter / custom.
- Dev + tests: MockProvider only (zero cost).
- Phase 5: STOP first → tell user exact balance to add (with margin), runs covered, cost per run → wait for confirmation.

## How the agent works (quick map)
- `app/agent/loop.py` Agent.run(): plan (read-only + submit_plan) → implement → verify (harness: deliverables,
  compile, pytest) ⇄ fix (≤ fix_rounds) → RUN_REPORT.md. State saved after every step → `run(resume=True)`.
- Tools: `app/tools/builtin.py`; permissions: `sandbox.py`; generated code runs via `runner.py` → `app/main.py`.
- Replay: `ReplayProvider(transcript.jsonl)` re-runs recorded model replies with zero cost.
- GUI: `python -m app.main` (dev). Mock mode checkbox = zero-cost scripted demo.
- Exe: `scriptsuild_exe.bat` → `dist\SpaceFractionsAgent.exe` (26 MB); check with `python scripts/verify_exe.py`.
- CI: `.github/workflows/build-windows.yml` builds + verifies on every push; `v*` tag → GitHub Release with exe.

## Open decisions / waiting on user
- none right now

## Key files
- Plan & requirements: `docs/PROMPT.md`
- Research + mechanism table: `docs/RESEARCH_NOTES.md`
- Decisions: `docs/DECISIONS.md`
- Change log + rollback: `docs/CHANGELOG_WORK.md`
- Roman Urdu notes: `docs/LEARNING_NOTES_UR.md`
