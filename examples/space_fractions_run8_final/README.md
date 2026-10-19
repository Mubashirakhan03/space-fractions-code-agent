# Space Fractions

A single-user Windows **desktop** learning game that teaches fractions through a
space-themed quiz. It is an adaptation (see `DESIGN_DECISIONS.md`) of a web/cloud
architecture specification into a Tkinter desktop app.

## What it is

- **Introductory movie** — an animated space scene (moving stars + rocket) with a Skip button.
- **Main menu** — Play, View Score, View Help, Admin.
- **Series of fraction questions** — equivalent, simplify, decimal and "which is larger"
  questions, drawn randomly from the seed pool **and** generated in code, shuffled each round.
- **Ending scene with feedback** — score + rating driven strictly by the real result, plus a
  per-question review.
- **Admin** — PIN-protected question management (add/edit/delete), with every field editable.

## How to run

```
python main.py
```

## How to test

```
python -m pytest -q
```

## Controls

- `F11` toggles full screen; `Esc` leaves full screen.
- Enter submits typed (decimal) answers.

## Admin PIN

The default admin PIN is **`1234`**, stored in `data/settings.json`.

## Data

- Persistence: SQLite file `game.db` (created on first run), schema in `sql/schema.sql`.
- Seed questions: `data/seed_questions.json` (20 items, loaded automatically when the store is empty).

## UML → module mapping

- `Game` / `GameState` / `GameStateMachine` → `game/game.py`, `game/state.py`
- `Question` / `QuestionKind` → `question/question.py`
- `User` → `user/user.py`; `Admin` → `admin/admin.py`
- Components → packages `game/`, `question/`, `user/`, `admin/`, `store/`
- Screens → `ui/*_screen.py` (one per use case / scene)
- The spec's `sql/question_ddl.sql` and `games` DDL → `sql/schema.sql`
