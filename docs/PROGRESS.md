# Progress Tracker

Read this first when resuming work in a new session.

**Last updated:** 2026-10-18
**Current phase:** Phase 0 done → waiting for OK to start Phase 1

| Phase | Status | Tag |
|---|---|---|
| 0 — Research & plan | ✅ done | (tag after git init) |
| 1 — Skeleton, config, providers, parsers | ⏳ next | |
| 2 — Tools, sandbox, loop, context, prompts | ⬜ | |
| 3 — GUI | ⬜ | |
| 4 — Exe build + GitHub Actions | ⬜ | |
| 5 — One real run → examples/ | ⬜ | |
| 6 — README, video script, release | ⬜ | |

## Environment facts
- Python 3.12.6 via `py`; tkinter 8.6; sqlite 3.45 — OK
- git 2.51 — OK; **gh CLI not installed** (install via `winget install GitHub.cli`, needs approval)
- No pip packages installed yet (will use a `.venv`)

## Scope decisions (2026-10-18, see DECISIONS.md D-008…D-011)
- Model: **only `deepseek-v4-pro`**, official API `https://api.deepseek.com`. No flash anywhere.
- Providers: **DeepSeek official + MockProvider (+ replay)**. No OpenRouter / custom.
- Dev + tests: MockProvider only (zero cost).
- Phase 5: STOP first → tell user exact balance to add (with margin), runs covered, cost per run → wait for confirmation.

## Open decisions / waiting on user
1. ~~Approve installing `gh`~~ approved 2026-10-18 → user does the `gh auth login` browser step.

## Key files
- Plan & requirements: `docs/PROMPT.md`
- Research + mechanism table: `docs/RESEARCH_NOTES.md`
- Decisions: `docs/DECISIONS.md`
- Change log + rollback: `docs/CHANGELOG_WORK.md`
- Roman Urdu notes: `docs/LEARNING_NOTES_UR.md`
