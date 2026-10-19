# AGENT_NOTES.md — agent memory

# AGENT_NOTES.md

Space Fractions — single-user Windows desktop learning game (Tkinter), adapted from a web/cloud spec.

Conventions:
- Domain logic (game/, question/, user/, admin/, store/) is Tkinter-free and headless-testable. UI (ui/) calls logic only.
- App controller: `ui/app.py::create_app(root) -> App` with `App.screens: dict[str, tk.Frame]` and `App.show(name)`; main.py only calls mainloop under `if __name__ == "__main__":`.
- Theme (palette/fonts) lives only in `ui/theme.py`.
- Persistence: SQLite `game.db` via `store/database.py`; seeded from `data/seed_questions.json` on first run when empty; admin PIN default `1234` in `data/settings.json`.
- Generator (`game/generator.py`) creates fraction questions in code; tests recompute expected answers independently. Wrong options distinct, never equal to correct.
- State machine: Playing/Paused/GameOver in `game/state.py` (pause/resume/gameOver) with invalid-transition tests.
- Screens required by harness: intro movie (animated Canvas + Skip), main menu, series of fraction questions (play), ending scene (results), plus View Score, View Help, Admin PIN (masked) and Admin questions. Admin area locks again on leaving.
- Tests: pytest (headless). `tests/test_ui_smoke.py` uses ONE session-scoped Tk, withdraw, show all screens, correct+wrong submissions, full flow, assert no callback errors.
