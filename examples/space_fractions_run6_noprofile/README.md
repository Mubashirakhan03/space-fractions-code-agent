# Space Fractions

A single-player **Windows desktop game** (Tkinter) that teaches primary-school
children about fractions through a "space mission" theme. It adapts the web /
microservice *Space Fractions* architecture specification into a desktop app.

## Features

- **Intro movie**: animated starfield title scene (Continue to proceed).
- **Main menu**: Play Game, View Score, View Help, Update Questions (admin).
- **Series of fraction questions**: random draw + shuffle each round; mix of
  multiple-choice and typed answers. Computable questions are generated fresh
  in code every round, with correct values computed and distinct wrong choices.
- **State machine**: Playing → Paused → Playing (pause/resume), Playing →
  GameOver.
- **Ending scene with feedback**: factual result screen that reflects the real
  score (no praise for a zero).
- **Admin**: add / edit / delete questions, persisted to SQLite; seed data
  (24 questions) loaded on first start.

## Run

```
python main.py
```

## Test

```
pytest
```

## Layout / UML mapping

| Component | Package |
|---|---|
| GameComponent | `game/` |
| QuestionComponent | `questions/` |
| UserComponent | `users/` |
| UI screens | `ui/` |
| Controller | `app/` |

See `DESIGN_DECISIONS.md` for the adaptation rationale and UI design brief.
