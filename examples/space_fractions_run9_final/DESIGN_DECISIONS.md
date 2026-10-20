# DESIGN_DECISIONS.md — Space Fractions (desktop game)

## 1. Adaptation table: original element → desktop equivalent → reason

| Original element | Desktop equivalent | Reason |
|---|---|---|
| Web-based game (browser) | Tkinter desktop window (1100×750+, maximised) | Task constraint: single-user Windows desktop app |
| Microservices (Game/Question/User/Admin components) | In-process Python packages `game/`, `question/`, `user/`, `admin/` with the same operations | Same logical separation, no network |
| Node.js / Express.js runtime | Python 3.11+ (Tkinter + stdlib only) | Required target platform |
| PostgreSQL (`games` table, `question_ddl.sql`) | SQLite file via `sqlite3`, DDL in `sql/schema.sql` | Required persistence; local single user |
| Redis cache | Not needed — in-memory round state | No shared state per session |
| RabbitMQ messaging | Direct in-process method calls | Single process |
| Elasticsearch search | SQL `LIKE`/in-memory filter for question search | Local single user |
| OAuth2 authn/authz | In-window PIN screen for the Admin role + local `settings.json` PIN | Desktop role protection; Admin = "administrator-type actor" |
| Prometheus observability | Python `logging` to a local log file | Local diagnostic |
| Jenkins CI/CD, Docker, Terraform, K8s, Vault, Istio, TLS, replicas, load balancing | N/A — single-user desktop; document as removed | No cloud infra needed |
| RESTful API (openapi.yaml) / gRPC (internal.proto) `GameService.Play` | `GameService` class with `play()`, `view_score()`, `pause()`, `resume()`, `game_over()` methods | Same contract, in-process |
| `PlayRequest`/`PlayResponse` messages | Method parameters/return values | In-process calls |
| ASR-1 data durability | SQLite persistence + seed data + backup via store | Questions persist/recoverable |
| ASR-2 security | PIN-gated Admin area | Role protection |

## 2. Input issues found

| Issue | Severity | Handling |
|---|---|---|
| EMPTY_TABLE (testing matrix cells empty) | high | Filled conceptually: each component gets Unit/Integration/Contract/E2E/Chaos tests in our test suite (documented in TRACEABILITY.csv) |
| ARTIFACT_MISMATCH (question_ddl.sql not in deliverables) | medium | Provide `sql/schema.sql` covering questions AND games; note mismatch |
| THIN_REQUIREMENTS (only 4 requirement ids) | high | Derived feature requirements FR-2..FR-6 for movie, menu, fraction questions, ending scene, help, from implied_features and use cases |
| UNTRACED_REQUIREMENT (ASR-2 untraced) | medium | Added ASR-2 row to TRACEABILITY.csv (Admin PIN) |
| GENERIC_JUSTIFICATIONS (copy-paste tech justifications) | medium | Removed in desktop adaptation; every adaptation has an individual reason |
| DUPLICATE_BLOCKS, UML_SYNTAX (Mermaid arrows, artifact/participant) | low | Normalised to PlantUML `->`; treated `artifact` as component/container; documented |
| PLATFORM_CONFLICT (web/cloud vs desktop) | high | Full desktop adaptation (see table) |

## 3. Assumptions made where the spec is thin

- **Fraction questions are computable**: the app GENERATES fraction questions in code (identify/compare/add/subtract fractions, reduce to lowest terms, find equivalent fractions) with the correct value computed programmatically; wrong choices are distinct and never equivalent to the correct value. Admin-added questions are also drawn into rounds.
- **Question model**: the spec's `Question` (id, prompt, options) is extended with `correct_value`, `kind`, and `choices` (list) so grading follows the prompt's own criterion (e.g. "lowest terms" accepts only the reduced form).
- **Introductory movie** = a 5–10s Canvas animation (rocket + planets + fraction stars moving) with a Skip button, auto-advancing to the main menu.
- **Main menu** = start screen with Play, View Help, View Score, Admin buttons.
- **Ending scene with feedback** = result screen showing score, correct/wrong counts, and a message/rating that matches the actual outcome (no praise for a zero result).
- **Round length**: 10 random questions per round by default (seed pool has 20+ across kinds; rounds shuffled; generators add variety).
- **Sessions** (~1 hour per A2, 1000 users A1): concurrency assumptions are irrelevant for a single-user desktop app; the game supports unlimited rounds and paused/resumed play within a round.
- **Score** is integer points (1 per correct answer); persisted as high score.
- **Paused state**: pause/resume via in-round buttons and the state machine (`Paused ↔ Playing`).

## 4. UML → code mapping

| UML element | Module / class | Test |
|---|---|---|
| Game (id, score; play(), viewScore()) | `game/game.py` → `Game` | `tests/test_game.py` |
| Question (id, prompt, options; getPrompt(), getOptions()) | `question/question.py` → `Question` | `tests/test_question.py` |
| User (id, username; playGame(), viewScore()) | `user/user.py` → `User` | `tests/test_user.py` |
| Admin (id, username; updateQuestions()) | `admin/admin.py` → `Admin` (+ `admin/question_repository.py`) | `tests/test_admin.py` |
| Game--*Question composition | `Game.questions` list | `tests/test_game.py` |
| User--*Game, Admin--*Question | owner collections | `tests/test_user.py`, `tests/test_admin.py` |
| State machine: Playing/Paused/GameOver; transitions [*]→Playing, pause(), resume(), gameOver() | `game/state_machine.py` → `GameStateMachine` | `tests/test_state_machine.py` |
| SequenceDiagram1 (play flow) | `game/game_service.py` → `GameService.play_round()` | `tests/test_game_flow.py` |
| SequenceDiagram2 (admin update questions) | `admin/question_repository.py` | `tests/test_admin.py` |
| GameService (RPC Play) | `game/game_service.py` → `GameService` | `tests/test_game_service.py` |
| OpenAPI /play | `GameService.play()` | `tests/test_game_service.py` |
| Games SQL DDL | `sql/schema.sql` (`games`, `questions` tables) | `tests/test_store.py` |
| Use case Play Game | `ui/screens/question_screen.py` | `tests/test_ui_smoke.py` |
| Use case View Score | `ui/screens/score_screen.py` | `tests/test_ui_smoke.py` |
| Use case View Help | `ui/screens/help_screen.py` | `tests/test_ui_smoke.py` |
| Use case Update Questions | `ui/screens/admin_screen.py` (+ PIN) | `tests/test_admin.py`, `tests/test_ui_smoke.py` |

## 5. UI design brief

**Target users**: primary-school / early-learners (and their teachers) practising fractions, with an admin (teacher/parent) maintaining questions. **Mood**: playful, exploratory, space adventure — bright and encouraging but clearly readable (large text for young readers).

**Palette** (hex roles):
- Background (deep space): `#0B1026`
- Surface (cards/panels): `#1B2440`
- Surface-alt (inputs): `#232F54`
- Primary (buttons): `#4C7DFF`
- Accent (rocket/highlight): `#FFD166`
- Accent-2 (fraction stars): `#EF476F`
- Success (green): `#06D6A0`
- Error (red): `#E63946`
- Text (on dark): `#F4F6FF`
- Muted text: `#9AA7D0`

**Fonts**: Tk default family (Segoe UI on Windows); titles 36pt bold, content 26pt, buttons/inputs 18pt bold, feedback 22pt. High contrast (light text on dark).

**Layout**: single main window ≥1100×750, resizable, centred, maximised/zoomed on start (`F11` fullscreen, `Esc` exit); every screen is a `tk.Frame` switched by `App.show(name)`. Consistent header (app name), content area, footer nav. Buttons: large, flat, hover colour.

**Screens** (each in `App.screens`):
1. `intro_movie` — 5–10s Canvas animation (rocket moves across, planets orbit, fraction stars drift), Skip button; auto-advances to `main_menu`.
2. `main_menu` — Play Game, View Help, View Score, Admin (→ PIN).
3. `question_screen` — series of fraction questions: prompt, multiple-choice buttons (or typed input when no choices), Submit/Check, Pause/Resume, live score.
4. `ending_scene` — score, correct/wrong, outcome-matched message and star rating; Play Again, Menu.
5. `help_screen` — how to play, fraction refresher.
6. `score_screen` — current/high score, best scores.
7. `pin_screen` — masked `tk.Entry(show='*')`, Unlock button, Enter submits, red error on wrong PIN.
8. `admin_screen` — lists ALL records (seed included): Add / Edit / Delete (with confirmation); fields for prompt, kind, choices, correct value. Relocks when leaving.

**Navigation**: intro_movie → main_menu → question_screen → ending_scene → main_menu; admin via PIN; help/score directly from menu.

**Seed data**: ≥20 fraction questions across all kinds (identify, compare, add, subtract, reduce, equivalent) in `data/questions_seed.json`, auto-loaded on first start.
