# DESIGN DECISIONS — Space Fractions

## 1. Adaptation table (original element → desktop equivalent → reason)

| Original element | Desktop equivalent | Reason |
|---|---|---|
| web-based / microservices (Node.js, Express.js) | Single Tkinter desktop app, in-process Python packages | Task constraint: single-user Windows desktop application. Components become Python packages (`game/`, `questions/`, `users/`, `admin/`, `ui/`). |
| RESTful API (`openapi.yaml` `/play`) | In-process `GameComponent` with `play()` / `view_score()` operations | No network needed; UI calls logic directly. Same logical operations preserved. |
| gRPC `GameService.Play` (`internal.proto`) | `Game.play()` method (sync, in-process) | RPC becomes a plain method call; latency is negligible in-process so NFR-1 (performance) is trivially met and testable. |
| PostgreSQL `games` table (JSONB state) | SQLite `games` table with a TEXT `game_state` (JSON) column | Single-user persistence; SQLite file bundled with app. Adapted in `sql/schema.sql`. |
| Redis (cache) | In-memory caches (dict) in repositories | No distributed cache needed; seed questions loaded once into memory. |
| RabbitMQ (messaging) | Direct method calls / callback in UI controller | No asynchronous service boundaries. |
| Elasticsearch (search) | In-memory Python list scan | Question set is small (seed + admin-added). |
| OAuth2 (authn/authz) | Local username entry + admin PIN; user role field | Single local user per session; Admin screen gated by a PIN (default `space-admin`). |
| Prometheus (observability) | `logging` module + score persistence | Local monitoring suffices. |
| Jenkins / Docker / Terraform / Kubernetes / Istio / Vault / TLS / replicas | Removed; plain Python stdlib app | No CI/CD, container orchestration or infra needed for a desktop app. |
| Node.js runtime | Python 3.11+ (stdlib only) | Bundled in the user's exe; target platform mandates stdlib-only. |
| ASR-1 data durability (PostgreSQL backups/replication) | SQLite file + periodic `commit()` + seed JSON backup | Data durability via local file; `data/questions.json` seed and admin edits persisted to DB. |
| ASR-2 security | Admin PIN, local input, no network exposure | No remote attack surface in a single-user desktop app. |

## 2. Input issues found

- **EMPTY_TABLE** (high): The testing matrix has headers but empty cells. → I mapped each test type to relevant components myself: Unit (Game, Question, User, Admin), Integration (repository↔logic↔DB), Contract (component interfaces/state machine), E2E (UI smoke), Chaos (invalid state transitions + corrupt DB recovery). Documented in TRACEABILITY.csv/test files.
- **ARTIFACT_MISMATCH** (medium): ASR-1 references `sql/question_ddl.sql` but deliverables list `sql/game_ddl.sql`. → Adapting the document's `games` table and additionally creating `questions` and `scores` tables in a single `sql/schema.sql`, satisfying both the `games` DDL and question persistence (ASR-1).
- **THIN_REQUIREMENTS** (high): Only 4 requirement IDs; implied features (intro, menu, questions, ending) have no FRs. → Derived FRs (FR-2…FR-8) for each implied feature and recorded in TRACEABILITY.csv with their components/tests.
- **UNTRACED_REQUIREMENT** (medium): ASR-2 not in traceability matrix. → Added ASR-2 row (Admin PIN / local auth) mapping to `users/` + `admin/` + tests.
- **GENERIC_JUSTIFICATIONS** (medium): 12 copy-pasted justifications. → Noted; each tech item mapped in the adaptation table above with a specific reason.
- **DUPLICATE_BLOCKS** (low): 4 duplicated code blocks. → Deduplicated: single schema, single API/proto description consolidated; no functional impact.
- **PLATFORM_CONFLICT** (high): web/cloud → desktop. → Fully re-targeted per adaptation table (this is the core constraint).
- **UML_SYNTAX** (low): Mermaid `->>` arrows and `artifact`/`participant` misuse. → Normalised to PlantUML-style `->`; diagram semantics (sequence: play flow + admin update) preserved in domain model and implemented.

## 3. Assumptions made where the spec is thin

- The game is a **round of 10 fraction questions**, selected randomly from the question pool covering all four types (equivalent fractions, compare, add/subtract, simplify).
- **Answer checking** uses `fractions.Fraction` so equivalent forms are accepted (e.g. `2/4` equals `1/2`), including typed answers and multiple choice.
- **Scoring**: 1 point per correct answer; final percentage = correct/answered; 1–3 stars earned by percentage (≥50% 1★, ≥75% 2★, ≥90% 3★).
- **State machine** enforces only valid transitions: `[*]→Playing`, `Playing⇄Paused`, `Playing→GameOver`; `pause()` from GameOver or Paused, `resume()` from Playing/GameOver, and `gameOver()` from Paused raise `InvalidTransitionError`.
- **Admin** is gated by a PIN (default `space-admin`); Admin can add/edit/delete questions (Update Questions use case).
- **User** authentication: player enters a name (optional high-score persistence); Admin is a built-in role.
- **Persistence**: SQLite DB (`data/spacefractions.db`) created from `sql/schema.sql`; seed questions loaded from `data/questions.json` on first run.
- **Intro** auto-advances to the menu after ~5s or via Skip button.

## 4. UML → code mapping

| Diagram element | Module / class | Test |
|---|---|---|
| Game class (+play, viewScore) | `game/game.py` → `Game` | `tests/test_game.py` |
| Question class (+getPrompt, getOptions) | `questions/question.py` → `Question` | `tests/test_questions.py` |
| User class (+playGame, viewScore) | `users/user.py` → `User` | `tests/test_users.py` |
| Admin class (+updateQuestions) | `admin/admin.py` → `Admin` | `tests/test_admin.py` |
| State machine (Playing/Paused/GameOver) | `game/state.py` → `GameState`, `InvalidTransitionError` | `tests/test_state.py` |
| SequenceDiagram1 (play flow) | `game/game.py` + `questions/` + `ui/question_screen.py` | integration + UI smoke |
| SequenceDiagram2 (admin update) | `admin/admin.py` + `questions/repository.py` | `tests/test_admin.py` |
| UseCase: Play Game | `ui/menu_screen.py`, `ui/question_screen.py`, `game/game.py` | `tests/test_ui_smoke.py` |
| UseCase: View Score | `ui/highscores_screen.py`, `users/repository.py` | `tests/test_scores.py` |
| UseCase: View Help | `ui/help_screen.py` | `tests/test_ui_smoke.py` |
| UseCase: Update Questions | `ui/admin_screen.py`, `admin/admin.py` | `tests/test_admin.py` |
| games DDL (ASR-1) | `sql/schema.sql`, `questions/repository.py` | `tests/test_persistence.py` |
| Component Game/Question/User/Admin | `game/`, `questions/`, `users/`, `admin/` packages | per-package tests |