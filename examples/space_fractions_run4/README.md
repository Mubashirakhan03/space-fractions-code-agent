# Space Fractions

A kid-friendly, space-themed educational fractions game for 6th-grade students
(ages 11–12), delivered as a **single-user Windows desktop application** built
with **Tkinter** and the **Python standard library** only.

## What it is

Players blast through a round of 10 fraction questions of four mixed types —
equivalent fractions, comparisons, add/subtract, and simplification — using
both multiple-choice and typed answers. `fractions.Fraction` is used to check
answers, so equivalent forms are accepted (e.g. `2/4` equals `1/2`).

The game mirrors the logical design of the original web/microservice
specification, adapted to a desktop app (see DESIGN_DECISIONS.md).

## Features

- Animated **intro** scene (rocket flying across moving stars, Skip button,
  auto-advance to the menu).
- **Main menu**: Play, High Scores, Help, Admin, Exit.
- **Player name** entry before playing.
- **Question flow** with progress ("Question 3 of 10"), a progress bar, an
  always-visible score, immediate big coloured feedback, automatic input
  clearing, and auto-advance to the next question.
- **Pause / Resume** (state machine `Playing ⇄ Paused → GameOver`);
  invalid transitions raise `ValueError`.
- **Ending scene** with final score, percentage, 1–3 stars and confetti,
  plus Play again / Main menu.
- **High Scores** persisted in SQLite; **Help** screen; **Admin** screen
  (passcode-gated) to add/edit/delete questions.
- Maximized on start (minimum 1100×750), `F11` full screen, `Esc` to leave.

## Requirements

- Python 3.11+
- Tests require `pytest`.

## Run

```
python main.py
```

## Test

```
python -m pytest -q
```

## Project layout

- `game/` — `Game` aggregate, `GameState` state machine, scoring (GameComponent).
- `questions/` — `Question`, answer checking, `QuestionRepository` (QuestionComponent).
- `users/` — `User` (UserComponent).
- `admin/` — `Admin` + passcode gate (AdminComponent).
- `ui/` — Tkinter screens, theme, space background, app controller.
- `sql/schema.sql` — SQLite schema (games, questions, scores).
- `data/questions.json` — 24 seed questions across all four types.
- `tests/` — headless domain, state-machine, persistence and UI smoke tests.

Domain logic is pure Python (no Tkinter) so it is fully testable without a
display. The UI layer only calls the domain.

## Adaptation notes

| Original (web/cloud) | Desktop equivalent |
|---|---|
| Microservices | In-process Python packages |
| Node.js / Express | Python 3.11 stdlib |
| REST / gRPC API | Direct method calls |
| PostgreSQL | SQLite file |
| Redis / RabbitMQ / Elasticsearch | In-memory deck / direct calls |
| OAuth2 | Local username + admin passcode |
| Prometheus | stdlib logging |
| Kubernetes / Docker / Terraform / Jenkins | not applicable |
