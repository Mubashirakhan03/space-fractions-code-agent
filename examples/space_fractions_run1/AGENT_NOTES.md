# AGENT_NOTES.md — agent memory

# AGENT_NOTES — Space Fractions

Single-user Windows desktop app: educational fractions game for 6th graders (Space Fractions).

## Key decisions
- Tkinter UI, Python stdlib only, SQLite persistence (`data/spacefractions.db`), seed `data/questions.json` (21 questions, 4 types).
- Components mirror UML packages: `game/` (Game, state machine, scoring), `questions/` (Question, checking with `fractions.Fraction`, repository), `users/`, `admin/`, `ui/`.
- Domain logic is pure Python (no Tkinter) — fully headless-testable. UI layer only calls into it.
- State machine: Playing ⇄ Paused → GameOver; invalid transitions raise `InvalidTransitionError`.
- Answer checking accepts equivalent fractions (2/4 == 1/2) via `fractions.Fraction`.
- Admin gated by PIN (default `space-admin`); factory `create_app(root)` builds UI without mainloop.

## Conventions
- Screen = one Frame class per file in `ui/`, switched by `ui/app.py` `App` controller.
- Factory `create_app(root)` exposed for smoke tests (never calls mainloop).
- Fonts: titles 36+, questions 30, inputs/buttons 20+. Theme: dark space blue `#0B1736`, accents yellow/cyan/pink/green.
- Window ≥1100x750, maximized on start, F11/Esc fullscreen.
- Tests: pytest, headless. UI smoke test uses ONE session-scoped Tk, retry 3x then skip on TclError, destroys children between tests.

## Data model
- `games` (id, game_state JSON), `questions` (id, prompt, type, options JSON, answer), `scores` (id, username, score, total, percentage, stars, timestamp).
