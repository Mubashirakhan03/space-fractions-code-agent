# DESIGN DECISIONS — Space Fractions

## 1. Adaptation table (platform conflicts → desktop equivalents)

| Original element | Desktop equivalent | Reason |
|---|---|---|
| web-based (browser web app) | Tkinter desktop window | Platform constraint requires a Windows desktop app. |
| microservices (GameComponent/QuestionComponent/UserComponent/AdminComponent) | In-process Python packages `game/`, `questions/`, `users/`, `admin/` | Single-user app; keep the logical service boundaries as packages with the same operation names. |
| Node.js / Express.js | Python 3.11 stdlib | Required runtime. |
| RESTful API (openapi `/play`) | `Game.play()` method call on a local `Game` object | No HTTP for a single local user; the "Play" operation is a direct call. |
| gRPC `internal.proto GameService.Play` | `GameController.play()` / `Game.play()` in `game/` | Same message semantics, in-process. |
| PostgreSQL | SQLite file (`data/spacefractions.db`) | Stdlib-only persistence; adapt `games` DDL (SERIAL→INTEGER PK AUTOINCREMENT, JSONB→TEXT). |
| `games` table / `question_ddl.sql` | `sql/schema.sql` with `games`, `questions`, `scores` tables | Consolidate DDL; add tables the domain needs. |
| Redis cache | In-memory Python caching (question pool loaded once) | No cache needed for a single user session. |
| RabbitMQ messaging | N/A (direct calls) | No async messaging between local modules. |
| Elasticsearch search | N/A (list/dict lookup over question repository) | Small local dataset. |
| OAuth2 authn/authz | Local player-name entry (UserComponent); Admin from an in-app Admin screen | Single local user; keep "User"/"Admin" identities as domain objects. |
| Prometheus observability | Python `logging` | Stdlib-only observability. |
| Jenkins CI/CD | N/A (traces to local tests) | Build automation out of scope for a desktop deliverable. |
| Docker / Terraform / Kubernetes (k8s deployment, replicas, Vault, Istio, TLS) | N/A — single desktop process; `Dockerfile` provided only to run tests headless | No cluster/infra for a desktop app. |
| 1000 concurrent users / 1-hour sessions (assumptions A1, A2) | Single local user, short round (~10 questions) | Server-side scale assumptions do not apply; noted, not implemented. |

## 2. Input issues found & how each was handled

- **EMPTY_TABLE (testing matrix)** — the U/E/C/Chaos matrix has no cells. Handled by constructing a complete test matrix (unit/integration for each component) represented by the test suite and TRACEABILITY.csv.
- **ARTIFACT_MISMATCH (`sql/question_ddl.sql` missing)** — delivered `sql/schema.sql` containing a `questions` table (the source of truth for question data) alongside `games` and `scores`.
- **THIN_REQUIREMENTS (features with no FR)** — the summary features (introductory movie, main menu, series of fraction questions, ending scene with feedback) are treated as implied features and implemented; each gets a TRACEABILITY.csv row.
- **UNTRACED_REQUIREMENT (ASR-2)** — traced in TRACEABILITY.csv to security of local data (SQLite file, no network) and admin-only question editing.
- **GENERIC_JUSTIFICATIONS** — documentational; covered in section 1 with per-item reasons.
- **DUPLICATE_BLOCKS** — document-only artifact; the single DDL contract is de-duplicated into `sql/schema.sql`.
- **PLATFORM_CONFLICT** — the core adaptation (section 1).
- **UML_SYNTAX issues** — sequence/object/collaboration arrows and component/container syntax normalised; logic mapping is unchanged.

## 3. Assumptions where the spec is thin

- A "round" is 10 questions drawn from the seed set, mixed types, no immediate repeats.
- Scoring: +1 per correct answer; percentage = correct/total; 1–3 stars by percentage.
- Question types: equivalent-fractions (multiple choice), compare (choice), add/subtract (typed), simplify (typed). Correctness uses `fractions.Fraction`, so `2/4 == 1/2`.
- High scores list the top 10 by percentage then score, newest first on ties.
- Admin screen is a simple PIN-free local editor (add/edit/delete questions) persisted to SQLite and re-exported to `data/questions.json` for reseeding.
- Pause only from Playing; Resume only from Paused; GameOver is terminal (invalid transitions raise `InvalidTransitionError`).
- Intro animation auto-advances after ~8s and has a Skip button.

## 4. UML → code mapping

| Diagram element | Module / class | Test |
|---|---|---|
| `Game` (id, score; play, viewScore) | `game/models.py::Game`, `game/controller.py` | `tests/test_game.py`, `tests/test_state_machine.py` |
| `Question` (id, prompt, options; getPrompt, getOptions) | `questions/model.py::Question`, `questions/checker.py` | `tests/test_questions.py` |
| `User` (id, username; playGame, viewScore) | `users/model.py::User` | `tests/test_users.py` |
| `Admin` (id, username; updateQuestions) | `admin/service.py::Admin` | `tests/test_admin.py` |
| `Game --* Question`, `User --* Game`, `Admin --* Question` | composition via references in `game.controller`, `users.model`, `admin.service` | tests above |
| State machine Playing⇄Paused→GameOver | `game/state_machine.py` | `tests/test_state_machine.py` |
| SequenceDiagram1 (play→prompt→submit→result) | `GameController.submit_answer()` | `tests/test_game.py` |
| SequenceDiagram2 (admin update) | `Admin.update_questions()` | `tests/test_admin.py` |
| Use cases (Play Game, View Score, View Help, Update Questions) | `ui/app.py` + screens | `tests/test_ui_smoke.py` |
| Deployment diagram → SQLite | `questions/repository.py`, `scores/repository.py` | `tests/test_persistence.py` |

## 5. UI design brief

- **Target users**: 11–12-year-old 6th graders (players) and an occasional adult admin.
- **Mood**: playful, encouraging, "deep space adventure" — bright and friendly, never punishing.
- **Palette** (hex, roles):
  - Background (space): `#0B1736`
  - Panel / surface: `#14265A`
  - Primary (buttons): `#2C7BD6`
  - Accent (highlights / stars): `#FFD166` (yellow), `#4ECDC4` (cyan), `#FF6B9D` (pink), `#3DDC84` (green)
  - Success: `#3DDC84`, Error: `#FF5A5F`
  - Text: `#FFFFFF`, muted text `#AEC6E8`
- **Fonts**: default family but large sizes — titles 40 pt bold; question 30 pt; buttons/inputs 20–22 pt; body 18–20 pt.
- **Layout**: every screen is a `tk.Frame` with a themed `tk.Canvas` space background (stars/planets) drawn in a `<Configure>` handler; widgets laid out with `pack`/`grid` in inner frames (never mixing pack+grid in the same parent). Big flat buttons with hover colours.
- **Key screens & navigation**: Intro (auto→Menu) → Menu (Play / High Scores / Help / Admin / Exit) → Name Entry → Question (progress bar, score, pause) → Pause overlay (Resume) → End (stars, confetti, Play again / Main menu); High Scores, Help, Admin (add/edit/delete) reachable from menu.
- **Window**: `root.minsize(1100, 750)`, centred, opened maximized (`state("zoomed")`), F11 full-screen toggle, Esc exits full screen.
