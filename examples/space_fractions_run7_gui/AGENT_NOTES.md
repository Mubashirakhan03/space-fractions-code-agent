# AGENT_NOTES.md — agent memory

Key decisions: Space Fractions = single-user educational fraction game. Pure-python domain in packages game/question/user/admin; Tkinter UI in ui/ with theme.py; SQLite persistence via sql/schema.sql + data seed. Questions drawn randomly+shuffled; math questions generated in code with independent recomputation in tests. GameStateMachine: start→Playing, pause/resume, gameOver. UI: screen Frames switched by ui/app.py create_app(root)->App with screens dict + show(name). No third-party runtime deps; pytest for tests. Convention: domain modules never import tkinter; UI calls service layer. Run tests via run_python test.

## Module responsibilities
- question/question.py: Question dataclass + QuestionKind; validate(); normalise() for fraction answers; from_kwargs/to_kwargs.
- question/repository.py: QuestionRepository (SQLite), auto-seeds from data/questions.json on empty store, CRUD + scores + users.
- game/game.py: Game entity (score, current question, submitAnswer).
- game/state.py: GameState (PLAYING/PAUSED/GAMEOVER) + GameStateMachine with valid/invalid transitions.
- game/round.py: build_round(pool, total, generated_count, rng) — random draw + shuffle + generated questions.
- game/generator.py: generated fraction questions keyed by kind; each carries operands for independent recomputation; wrong choices distinct + non-equivalent.
- game/service.py: GameService facade (play/pause/resume/submit/view_score); AnswerResult built BEFORE state advance (rule 10).
- user/user.py: User; admin/admin.py: Admin (validate on add/update).
- ui/theme.py: palette + fonts (design brief section 5). ui/widgets.py: StarCanvas (redraws on <Configure>).
- ui/app.py: App.show(name) packs target, forgets others, calls screen.begin() if present; create_app sets title, F11/Esc, minsize.

## Gotchas
- write_files entries MUST list "path" key before "content", else tool rejects.
- Question options are validated for equivalence-class duplicates (2/4 == 1/2 counts as duplicate).
- Play -> GameOver is a VALID transition (state diagram); GameOver is terminal.
- Ignore 1000-concurrency / 1-hour session assumptions (single-user desktop).

## Build status
compile: PASS. test: 29 passed (domain, state machine, generator, persistence, UI smoke).
