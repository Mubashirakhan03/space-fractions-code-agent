# Space Fractions

An educational fractions game for 6th-grade students, delivered as a single-user Windows
desktop application (Tkinter). Players answer a round of fraction questions in a fun,
space-themed environment.

## Features

- **Animated intro** — a rocket flies across a starfield with twinkling stars and planets;
  a Skip button or auto-advance (6s) takes you to the menu.
- **Main menu** — Play, High Scores, Help, Admin, Exit.
- **Player name entry** before each round.
- **Question flow** — a round of 10 randomly selected questions covering four types:
  equivalent fractions, comparing, adding/subtracting, and simplifying. Answers may be
  multiple-choice or typed. Equivalent fractions are accepted (`2/4` == `1/2`) using
  `fractions.Fraction`. Immediate coloured feedback, progress bar, and a live score.
- **Pause / Resume** — full state machine (`Playing` ⇄ `Paused` → `GameOver`); invalid
  transitions raise `InvalidTransitionError`.
- **Ending scene** — final score, percentage, 1–3 stars, confetti animation, encouraging
  message, and Play again / Main menu buttons.
- **High Scores** — persisted in SQLite.
- **Help** screen.
- **Admin** screen (PIN `space-admin`) to add / edit / delete questions.

## How to run

```bash
python main.py
```

The app opens maximized (minimum 1100×750). F11 toggles full screen; Esc leaves full screen.

Database (`data/spacefractions.db`) and schema (`sql/schema.sql`) are created automatically
on first run; `data/questions.json` seeds the question pool (21 questions).

## How to test

```bash
pip install -r requirements.txt   # only pytest
python -m pytest -q
```

All tests are headless (no display needed). The UI smoke test builds every screen using a
single session-scoped `tk.Tk`.

## Architecture

Logic is pure Python (no Tkinter) and lives in domain packages; the UI layer calls it.

| Package | Responsibility | UML component |
|---|---|---|
| `game/` | `Game`, scoring, state machine | GameComponent |
| `questions/` | `Question`, answer checking, repository | QuestionComponent |
| `users/` | `User`, `ScoreRepository` | UserComponent |
| `admin/` | `Admin` | AdminComponent |
| `ui/` | Tkinter screens + controller | (presentation) |

## UML → module mapping

See `DESIGN_DECISIONS.md` (section 4) and `TRACEABILITY.csv` for the full mapping of
use cases, classes, state machine, and sequences to modules and tests.
