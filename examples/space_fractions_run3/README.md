# Space Fractions

A single-user Windows desktop educational fractions game for 6th-grade students, built with
Python + Tkinter (standard library only). Players solve a round of 10 fraction questions of
mixed types, earn a score and 1–3 stars, and see their high scores.

## Run

```
python main.py
```

## Test

```
pytest -q
```

## Features

- Animated space INTRO (rocket + twinkling stars) with Skip and auto-advance.
- MAIN MENU: Play, High Scores, Help, Admin, Exit.
- PLAYER NAME entry before playing.
- QUESTION round of mixed types: equivalent fractions, compare, add/subtract, simplify;
  multiple choice (2×2 coloured buttons) and typed answers; immediate coloured feedback;
  progress bar and always-visible score.
- Answer checking via `fractions.Fraction` so equivalent forms count (2/4 == 1/2).
- PAUSE / RESUME state machine (Playing ⇄ Paused → GameOver); invalid transitions raise.
- ENDING scene: score, percentage, 1–3 stars, confetti, Play again / Main menu.
- HIGH SCORES persisted in SQLite; HELP screen; ADMIN screen to add/edit/delete questions.
- F11 full screen, Esc exits full screen; opens maximized; min size 1100×750.

## UML → module mapping

| Component | Package | Classes |
|---|---|---|
| GameComponent | `game/` | `Game`, `GameState`, `GameService`, `scoring` |
| QuestionComponent | `questions/` | `Question`, `QuestionRepository`, `catalog` |
| UserComponent | `users/` | `User` |
| AdminComponent | `admin/` | `Admin` |
| UI | `ui/` | screen Frames + `App` controller + `Theme` |

Data: `sql/schema.sql` (games, questions, scores), `data/questions.json` (24 seed questions).
