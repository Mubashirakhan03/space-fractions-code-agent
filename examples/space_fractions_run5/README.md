# Space Fractions

An educational fraction-maths game for 6th-grade students, built as a single-user
Windows desktop application with Tkinter and the Python standard library only.

## What it is

A space-themed game where players answer a round of 10 fraction questions of four
types — equivalent fractions, comparing, add/subtract, and simplify — with a mix of
multiple-choice and typed answers. Answers are checked with `fractions.Fraction`, so
equivalent forms are accepted (`2/4 == 1/2`). The app features:

- Animated intro scene (rocket + twinkling stars, Skip button, auto-advance)
- Main menu (Play, High Scores, Help, Admin, Exit)
- Player-name entry
- Question flow with progress bar, live score, pause/resume, and immediate coloured feedback
- Ending scene with score, percentage, 1–3 stars, and confetti
- High Scores (persisted in SQLite), Help, and an Admin question editor

## How to run

```
python main.py
```

Opens maximized (minimum 1100x750). `F11` toggles full screen, `Esc` leaves full screen.

## How to test

```
python -m pytest
```

Tests are headless (no display required) and cover the state machine (valid *and* invalid
transitions), question checking, game scoring, User/Admin domain objects, SQLite persistence,
and a UI smoke test.

## Layout / UML → module mapping

| Component (UML) | Package | Notes |
|---|---|---|
| GameComponent | `game/` | `Game` model, `GameStateMachine` (Playing⇄Paused→GameOver), `GameController` |
| QuestionComponent | `questions/` | `Question` model, `QuestionChecker`, `QuestionRepository` (SQLite) |
| UserComponent | `users/` | `User` model (player identity) |
| AdminComponent | `admin/` | `Admin` model + add/edit/delete service |
| scores (persistence) | `scores/` | `ScoreRepository` for high scores |
| UI | `ui/` | theme, space background, app controller, screens |

## Data

- `data/questions.json` — 22 seed questions covering all four types.
- `sql/schema.sql` — SQLite DDL (adapted from the document's `games` table) plus
  `questions` and `scores` tables.
