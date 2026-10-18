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
