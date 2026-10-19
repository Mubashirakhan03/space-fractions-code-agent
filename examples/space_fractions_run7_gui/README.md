# Space Fractions

A single-user Windows desktop educational game for learning fractions, themed around
space exploration. Built with Tkinter and the Python standard library only (plus pytest
for tests), with SQLite persistence.

## Run

```
python main.py
```

## Test

```
python -m pytest -q
```

Tests are headless (no display needed): domain logic, state machine, generators,
persistence, and a UI smoke test.

## Features

- **Intro screen** (introductory movie: animated starfield + title).
- **Main menu**: Play, View Score, Help, Admin, Quit.
- **Game**: a random, shuffled series of fraction questions (seeded + admin-added +
  code-generated). Typed or multiple-choice inputs, immediate green/red feedback,
  Enter-to-submit, auto-clear input, pause/resume.
- **Ending scene**: calibrated score feedback (no praise for a zero score).
- **Admin**: add/edit/delete questions (validated), persisted to SQLite.
- **Score history**: past mission scores.

Question kinds: compare, add, subtract, multiply, simplify, equivalent.

## Architecture (UML → module)

| Component | Module |
|---|---|
| GameComponent (Game, state machine, service) | `game/game.py`, `game/state.py`, `game/round.py`, `game/service.py`, `game/generator.py` |
| QuestionComponent (Question, persistence) | `question/question.py`, `question/repository.py` |
| UserComponent (User) | `user/user.py` |
| AdminComponent (Admin) | `admin/admin.py` |
| UI (screens, controller, theme) | `ui/` |

Domain logic never imports Tkinter; `ui/` calls the service layer.
