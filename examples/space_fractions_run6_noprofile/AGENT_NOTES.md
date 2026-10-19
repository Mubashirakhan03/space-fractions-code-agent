# AGENT_NOTES.md — agent memory

## Space Fractions — desktop adaptation

- Web microservice spec adapted to a single-user Windows Tkinter desktop app. Components → in-process Python packages: `game/`, `questions/`, `users/`; PostgreSQL → SQLite; REST/gRPC → method calls.
- Package responsibilities:
  - `game/` — Game class (+ score), GameState enum (Playing/Paused/GameOver), fraction question generator (computable content).
  - `questions/` — Question model + SQLite repository (question CRUD), seed loading on first start.
  - `users/` — User and Admin models (roles).
  - `app/` — controller façade wiring game + repository + user session.
  - `ui/` — one Frame class per use case; `theme.py` holds palette/fonts; `ui/app.py` exports `create_app(root) -> App` with `screens` dict + `show(name)`.
- Conventions: domain logic free of tkinter; SQLite persists questions (24+ seed items, choice + typed kinds); random draw + shuffle each round; score = first-attempt correct; pause/resume allowed.
- Key rules to keep: never mix pack/grid in one container; canvas redraws bind to <Configure>; messagebox only for confirmations; typed answers require a visible Check button, Enter submits and input clears; result screen feedback must match actual outcome (no praise for zero).
- Tests: full state machine incl. invalid transitions, persistence against a temp SQLite file, generator distinct/correct choices, message-correctness (right item named, incl. wrong-input path), and one-session Tk smoke test playing a full flow through real callbacks.
