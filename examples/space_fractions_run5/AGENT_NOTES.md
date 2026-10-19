# AGENT_NOTES.md — agent memory

# AGENT NOTES — Space Fractions

Desktop educational fractions game for 6th graders (Tkinter + stdlib only + pytest).

## Module responsibilities
- `game/` — `Game` model, `GameStateMachine` (Playing⇄Paused→GameOver; invalid transitions raise), `GameController` (round flow, scoring).
- `questions/` — `Question` model, `QuestionChecker` (uses `fractions.Fraction`), `QuestionRepository` (SQLite + seed from `data/questions.json`).
- `users/` — `User` model (username entry).
- `admin/` — `Admin` model + question add/edit/delete service.
- `scores/` — `ScoreRepository` for high scores.
- `ui/` — `theme.py` (palette/fonts), `spacebg.py` (`SpaceBackground` canvas drawing), `app.py` (`create_app`), screens in `ui/screens/`.

## Conventions
- Domain logic is pure and headless (no tkinter import) so it is unit-testable and usable in tests.
- Answers checked with `fractions.Fraction`; typed answers accept `a/b`, improper, etc.
- All user-visible feedback messages compute values BEFORE mutating state (correct/expected answer shown on wrong input).
- UI: each screen is its own Frame; pack/grid never mixed in one parent; canvas draws happen in `<Configure>`.
- `main.py` is the only entry point that starts Tk.
