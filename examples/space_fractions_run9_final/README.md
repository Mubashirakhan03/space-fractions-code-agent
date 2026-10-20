# Space Fractions

A single-user Windows desktop fraction-practice game for young learners, built with Tkinter and the Python standard library only.

## What it is

Players answer a randomised series of fraction questions (identify, compare, add, subtract, reduce, and equivalent fractions) on a space-adventure themed interface. A teacher/parent (Admin) can manage the question pool behind a PIN.

## How to run

```bash
python main.py
```

## How to test

```bash
python -m pytest -q
```

Tests cover domain logic, the game state machine, question generation (with independent recomputation of expected values), SQLite persistence, and a headless UI smoke test (animation, PIN gate, admin CRUD, and a full play-through).

## Features

- **Introductory movie**: an 8-second animated opening (rocket, planets, fraction stars) with a Skip button.
- **Main menu**: Play Game, View Help, View Score, Admin.
- **Play Game**: 10 randomised questions per round, drawn from the whole pool (stored + generated) and shuffled. Multiple-choice and typed answers, live score, pause/resume.
- **Ending scene**: score, correct/wrong counts, and outcome-matched feedback with a star rating.
- **View Score**: best and last-round scores.
- **View Help**: how to play plus a fraction refresher.
- **Update Questions (Admin)**: list all records (seed included), Add, Edit, and Delete (with confirmation). Reached only through the in-window PIN screen.

## Admin PIN

The admin PIN is stored in `data/settings.json` (created on first run). The **default PIN is `4321`**.

## Questions are computable

In addition to the 22 seeded questions in `data/questions_seed.json`, the game generates new fraction questions in code each round: the correct value is computed programmatically and wrong choices are distinct and never equivalent to the correct answer.

## Architecture

UML components map to in-process Python packages:

- `game/` — Game, GameService (RPC-equivalent), Round, state machine, question generator
- `question/` — Question entity
- `user/` — User, Admin entities
- `admin/` — QuestionRepository, Settings (PIN)
- `store/` — SQLite persistence (ASR-1 data durability)
- `ui/` — Tkinter screens (one per use case/scene) and theme

See `sql/schema.sql` for the SQLite DDL and `TRACEABILITY.csv` for the requirement/use-case mapping.
