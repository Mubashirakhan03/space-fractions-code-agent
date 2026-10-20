# AGENT_NOTES.md — agent memory

# AGENT_NOTES.md

Key decisions:
- Space Fractions desktop game: fraction-practice quiz for young learners, built with Tkinter + stdlib only (no third-party runtime deps).
- Logical components preserved as in-process packages: `game/`, `question/`, `user/`, `admin/`, `store/` (SQLite persistence). Domain logic is pure Python (headless-testable); `ui/` is the only Tkinter layer.
- `game/question_generator.py` generates computable fraction questions in code (correct value computed programmatically, distinct wrong choices, min/max denominators), plus seed questions from `data/questions_seed.json`.
- State machine in `game/state_machine.py`: Playing/Paused/GameOver with pause(), resume(), gameOver().
- Admin is a protected role: reached only through `pin_screen` (masked entry, in-window); PIN stored in `data/settings.json` (default `4321`, documented in README). Admin screen lists ALL questions (seed included) with Add/Edit/Delete confirmation.
- Each screen is its own Frame class in `ui/screens/`, switched by `ui/app.py` `App.show(name)`; `App.screens` dict must contain: intro_movie, main_menu, question_screen, ending_scene, help_screen, score_screen, pin_screen, admin_screen.
- Intro movie is a real Canvas animation (5–10s, moving objects, Skip button, auto-advance, after() ids cancelled on skip/leave).
- Theme in `ui/theme.py`: space palette (#0B1026 bg, #1B2440 surface, #4C7DFF primary, #FFD166 accent, #06D6A0 success, #E63946 error), titles 36pt, content 26pt, buttons/inputs 18pt.
- main.py runs Tk only under `if __name__ == "__main__":`.
- `create_app(root)` in `ui/app.py` builds everything WITHOUT mainloop.
- Messages must compute expected values BEFORE mutating state; test every user-visible message for the RIGHT item (including wrong-input path).
- Conventions: snake_case packages/files; single store instance passed to app; seeds load on first start when DB empty.
