# DESIGN_DECISIONS.md

## 1. Adaptation table (web/cloud → desktop)

| Original element | Desktop equivalent | Reason |
|---|---|---|
| web-based (REST/gRPC service) | single-process desktop app, in-process function calls | task constraint: Windows desktop deliverable |
| microservices (Game/Question/User/Admin) | Python packages `game`, `question`, `user`, `admin` | logical components kept as modules |
| Node.js 18-20 runtime | Python 3.11+, stdlib only | bundled exe constraint |
| Express.js 4-5 web framework | Tkinter `ui/` screens | desktop GUI |
| RESTful API (`openapi.yaml`, `/play`) | in-process `GameService` with same operations (Play, ViewScore) | interface preserved, transport removed |
| gRPC `internal.proto` (GameService.Play) | `game/service.py` `GameService.play(request)` | same operation, no network |
| PostgreSQL 14-15 (`games`, `question` tables) | SQLite file via `sqlite3` (`sql/schema.sql`) | stdlib persistence |
| Redis cache | in-memory `random`/lists | single-user, no shared cache needed |
| RabbitMQ messaging | direct method calls | no async workers needed |
| Elasticsearch search | `sqlite3` queries + in-memory filters | question admin search |
| OAuth2 authn/authz | single local user profile (username), Admin vs User role | single local user per session |
| Prometheus observability | `logging` to stdout/file | stdlib |
| Jenkins CI/CD | `run_python test` + pytest | harness handles CI |
| Docker 20-21 | optional `Dockerfile` (python:3.12-slim) running tests | headless test image |
| Terraform / Kubernetes / replicas / Istio / Vault / TLS | n/a (single-user desktop) | no distributed deployment |
| `sql/question_ddl.sql` (referenced but not delivered) | `sql/schema.sql` with `questions` + `games` + `users` tables | persistence for question data & scores (ASR-1) |

## 2. Input issues found

| Code | Handling |
|---|---|
| EMPTY_TABLE (unit/integration/… chaos matrix empty) | Filled a concrete testing matrix in README/TRACEABILITY mapping each test type to Game/Question components and files. |
| ARTIFACT_MISMATCH (`sql/question_ddl.sql` missing) | Created `sql/schema.sql` covering questions, games, users; traceability references it. |
| THIN_REQUIREMENTS (features w/o FRs) | Added implied feature ids FR-2…FR-6 (intro movie, main menu, fraction questions, ending scene, admin update) and traced each to files/tests. |
| UNTRACED_REQUIREMENT (ASR-2) | Added ASR-2 row (security: local-only, no network, hashed-ish session identity) in TRACEABILITY.csv. |
| GENERIC_JUSTIFICATIONS | Documented concrete per-technology rationale in adaptation table (not copy-pasted). |
| DUPLICATE_BLOCKS | Normalised single canonical copies (openapi/proto/sql) in DESIGN_DECISIONS only. |
| PLATFORM_CONFLICT | Whole document adapted to desktop (this table). |
| UML_SYNTAX (participant/artifact, `->>`) | Treated participants as objects, artifact→component/container, `->>` → `->`; mapped classes unchanged. |

## 3. Assumptions (spec is thin)

- **Space Fractions** is an educational fraction game for a single local user (End User) with an optional Admin role for updating questions.
- A **round** = a series of N fraction questions (default 10, configurable) drawn at RANDOM and shuffled; score = correct/total. State machine Playing/Paused/GameOver follows the spec's states/transitions.
- Questions are both **seeded** (data/questions.json, ≥20 items covering types: compare, addition, subtraction, multiplication, simplify, identify) and **code-generated** at runtime: math fraction questions where the correct value is computed in code and validated independently in tests. Wrong choices are distinct and never equal to the correct value.
- Question kinds: `compare` (which is larger/smaller), `add`, `subtract`, `multiply`, `simplify`, `equivalent`. Each generated item stores its operands so tests can RECOMPUTE the expected answer.
- **Admin** updates questions via an admin screen (add/edit/delete), persisted to SQLite; generated questions are not editable (computed) but seed/added questions form the pool.
- "Introductory movie", "main menu", "ending scene with feedback" are realised as Tkinter screens (intro/title with animated stars, menu, results/ending screen with score + encouraging/calibrated feedback).
- 1000 concurrent users / 1-hour sessions (A1, A2) are not applicable to single-user desktop; noted as non-goals. Session time is not enforced.
- Persistence: scores history in `games` table; questions in `questions` table; profile in `users` table (ASR-1 durability).

## 4. UML → code mapping

| Diagram element | Module / class / test |
|---|---|
| Actor End User | `user/user.py::User` |
| Actor Admin | `admin/admin.py::Admin` |
| Class Game (id, score, play(), viewScore()) | `game/game.py::Game` |
| Class Question (id, prompt, options, getPrompt(), getOptions()) | `question/question.py::Question` |
| Class User (id, username, playGame(), viewScore()) | `user/user.py::User` |
| Class Admin (id, username, updateQuestions()) | `admin/admin.py::Admin` |
| Game --* Question composition | `Game.questions: list[Question]` |
| User --* Game composition | `User.current_game: Game` |
| Admin --* Question composition | `Admin.updateQuestions()` managing pool |
| States Playing/Paused/GameOver | `game/state.py::GameState` enum + `GameStateMachine` |
| Transitions (start→Playing, pause, resume, gameOver) | `game/state.py`, tests `tests/test_state_machine.py` |
| SequenceDiagram1 (play/getPrompt/answer/result) | `game/service.py::GameService` + `ui/screens/game_screen.py` |
| SequenceDiagram2 (Admin update → success) | `admin/admin.py` + `ui/screens/admin_screen.py` |
| Activity diagram (play→score→display) | `game/round.py::Round` |
| Use cases Play/View Score/View Help/Update Questions | `ui/screens/{menu,game,results,help,admin}_screen.py` |
| Components GameComponent/QuestionComponent/UserComponent/AdminComponent | packages `game/ question/ user/ admin/` |

## 5. UI design brief

- **Target users**: children/students aged ~8–12 (End User) learning fractions, plus a teacher/parent (Admin) who updates questions. Single local user.
- **Mood**: bright, playful, encouraging, space-themed (fits "Space Fractions" title) — a fun learning game, not a serious test.
- **Colour palette** (roles):
  - background: `#0B1026` (deep space navy)
  - surface: `#1B2144` (panel background)
  - primary: `#4A90E2` (buttons, accents)
  - accent: `#FFD166` (stars, highlights, score)
  - secondary accent: `#9B5DE5` (space purple)
  - success: `#43D17C` (correct feedback)
  - error: `#FF5D73` (wrong feedback)
  - text: `#F4F6FF` (light, high contrast)
  - muted text: `#A9B4D6`
- **Fonts**: Tk defaults via `tkinter.font`; sizes: title 40 bold, subtitle 26, main content 26, buttons 20, inputs 20, feedback 24. Use `('Segoe UI', size, weight)`.
- **Layout**: fixed full window (minsize 1100x750, centered, maximized). Each screen a `tk.Frame`; navigation via controller `ui/app.py`. Title header bar top, content center, big buttons bottom. Canvas space background with animated stars drawn on `<Configure>`.
- **Key screens**:
  1. IntroScreen (introductory movie: animated starfield + title + "Start").
  2. MenuScreen (main menu: Play, View Score, Help, Admin, Quit).
  3. GameScreen (prompt + typed OR multiple-choice input, big submit button, Enter submits, input auto-clears, immediate green/red feedback).
  4. PauseScreen / HelpScreen (paused state, resume).
  5. ResultsScreen (ending scene: score, calibrated feedback — no praise for 0, stars for high score).
  6. AdminScreen (list/add/edit/delete questions, validate all fields).
  7. ScoreHistoryScreen (past scores from SQLite).
- **Feedback policy**: correct → green "Correct!" with the right value; wrong → red showing the expected value of the *just-submitted* item (computed before state advances). Ending screen rating matches actual score (0 = "Let's practice more", high = celebratory stars).
