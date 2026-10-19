# Space Fractions

An educational fractions game for 6th-grade students (ages 11–12), built as a
single-user Windows desktop application using Python + Tkinter + SQLite.

Players blast through a 10-question space mission covering four question types:
equivalent fractions, compare, add/subtract, and simplify. Multiple-choice and
typed answers are both supported; correctness is judged with
`fractions.Fraction` so equivalent forms are accepted (2/4 = 1/2).

## Features

- Animated space **intro** scene (rocket + starfield) with Skip and auto-advance.
- **Main menu**: Play, High Scores, Help, Admin, Exit.
- **Player name** entry before playing.
- **Question flow** with progress bar, always-visible score, immediate green/red
  feedback, auto-cleared input, and a **Pause/Resume** overlay (Playing ⇄ Paused
  → GameOver state machine; invalid transitions raise `StateError`).
- **Ending scene** with final score, percentage, 1–3 stars, and confetti.
- **High Scores** from SQLite, **Help** screen, and **Admin** screen to
  add / edit / delete questions.

## Running

```bash
python main.py
```

## Testing

```bash
python -m pytest
```

Tests are headless (no display needed).

## UML → module mapping

| Component | Package |
|---|---|
| GameComponent | `game/` (`Game`, state machine, scoring) |
| QuestionComponent | `questions/` (`Question`, repository) |
| UserComponent | `users/` (`User`) |
| AdminComponent | `admin/` (`Admin`) |
| UI screens | `ui/` (one screen per use case/state) |

Persistence uses SQLite (schema in `sql/schema.sql`, seed data in
`data/questions.json`).
