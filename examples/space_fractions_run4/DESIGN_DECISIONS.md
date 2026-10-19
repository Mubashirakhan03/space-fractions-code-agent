# DESIGN_DECISIONS — Space Fractions (desktop adaptation)

## 1. Adaptation table (original element → desktop equivalent → reason)

| Original element | Desktop equivalent | Reason |
|---|---|---|
| web-based game | single-window Tkinter desktop app | Task constraint: deliverable must be a desktop app |
| microservices (Game/Question/User/Admin components) | in-process Python packages `game/`, `questions/`, `users/`, `admin/` | keep logical component boundaries; no network, single user |
| Node.js 18-20 / Express.js | Python 3.11+ / standard library | mandated runtime |
| RESTful API (`/play`, openapi.yaml) | `game/` service object with `play()` operation | same operations, direct call |
| gRPC `GameService.Play` (internal.proto) | `Game.play()` method | same operation semantics |
| PostgreSQL | SQLite database file | mandated persistence |
| Redis cache | in-memory question cache/deck in `questions.Repository` | single user, no cache needed; keep a loaded deck |
| RabbitMQ messaging | direct method calls | single process |
| Elasticsearch search | none (in-memory list) | not needed for single-user game |
| OAuth2 authn/authz | local username entry (`users/`) + admin passcode | single local user per session |
| Prometheus observability | logging (stdlib `logging`) | local app, no metrics sink |
| Jenkins CI/CD, Docker, Terraform, Kubernetes, replicas, Vault, Istio, TLS | n/a — see assumption notes | infrastructure not applicable to desktop |
| PostgreSQL `games` table (id, game_state JSONB) | SQLite `scores` table storing final game results | persistence of play results (data durability ASR-1) |

## 2. Input issues found

- **EMPTY_TABLE** (high): testing matrix has headers but empty cells. → We defined a complete test matrix ourselves in tests/ covering Game, Question, User, Admin at unit + integration + UI/E2E (smoke) level; recorded in TRACEABILITY.csv.
- **ARTIFACT_MISMATCH** (medium): ASR-1 references `sql/question_ddl.sql` not in deliverables. → We deliver `sql/schema.sql` containing `questions`, `scores`, and `games` tables; persisted question data is in `data/questions.json` and loadable/recoverable.
- **THIN_REQUIREMENTS** (high): features (intro movie, main menu, fraction questions, ending scene) lack FR ids. → We introduced derived requirement ids FR-2..FR-9 for these implied features and traced each.
- **UNTRACED_REQUIREMENT** (medium): ASR-2 untraced. → We map ASR-2 (security) to the admin passcode gate and traced it in TRACEABILITY.csv.
- **GENERIC_JUSTIFICATIONS** (medium): 12 copy-pasted justifications. → Only 2 tech choices remain (Python, SQLite); each has a distinct justification in the README.
- **DUPLICATE_BLOCKS** (low): duplicating openapi/proto/sql = single API definition. → Resolved to one `game/` service; noted.
- **PLATFORM_CONFLICT** (high): web/cloud spec vs desktop deliverable. → Handled via section 1 adaptation.
- **UML_SYNTAX** (low, ×7): Mermaid `->>` arrows and `participant`/`artifact` keywords. → Normalised to `->` and objects/components per spec.

## 3. Assumptions (spec was thin)

- "1000 users concurrently / 1 hour sessions" (A1/A2) are irrelevant to a single-user desktop app; kept only as rationale for responsive UI (NFR-1).
- Round length = 10 questions (mixed types: equivalent, compare, add/subtract, simplify; multiple-choice and typed answers).
- Answer checking uses `fractions.Fraction` so equivalent forms (2/4 == 1/2) are accepted; typed answers are also reduced for comparison.
- Scoring: progress and percent correct; end screen shows 1–3 stars by percentage (≥60% 1 star, ≥80% 2, ≥95% 3).
- High scores persist to SQLite (`scores`); admin screen requires a fixed passcode ("admin" default, overridable via constant) — ASR-2 mapping.
- `games` table (document DDL) retained for data-durability parity, storing a JSON game-state snapshot.
- Pause/Resume follow the state machine; invalid transitions raise `ValueError`.

## 4. UML → code mapping

| Diagram / element | Module / class | Test |
|---|---|---|
| Class `Game` (id, score; play(), viewScore()) | `game/game.py` `Game` | `tests/test_game.py` |
| Class `Question` (id, prompt, options; getPrompt(), getOptions()) | `questions/question.py` `Question` | `tests/test_questions.py` |
| Class `User` (id, username; playGame(), viewScore()) | `users/user.py` `User` | `tests/test_users.py` |
| Class `Admin` (id, username; updateQuestions()) | `admin/admin.py` `Admin` | `tests/test_admin.py` |
| Composition Game *— Question, User *— Game, Admin *— Question | constructors hold references | tests above |
| State machine Playing ⇄ Paused → GameOver | `game/state.py` `GameState` enum + `Game.play/pause/resume/finish` | `tests/test_game.py` (valid + invalid) |
| SequenceDiagram1 (play flow) | `game/game.py` play → `Question.getPrompt/getOptions` → `Repository.checkAnswer` | `tests/test_game.py` |
| SequenceDiagram2 (admin update) | `admin/admin.py` → `questions/repository.py` | `tests/test_admin.py` |
| Use cases Play Game / View Score / View Help / Update Questions | `ui/screens.py` + `ui/app.py` | `tests/test_ui_smoke.py` |
| Components Game/Question/User/Admin | packages `game/`, `questions/`, `users/`, `admin/` | per-package tests |

## 5. UI design brief

- **Target users**: 6th-grade students (ages 11–12) playing an educational fractions game, plus a teacher/admin who maintains questions.
- **Mood**: playful, encouraging, space-exploration adventure — bright and energising but calm enough to not overwhelm.
- **Palette** (roles in `ui/theme.py`):
  - Background (deep space): `#0B1736`
  - Panel/surface: `#14274E`
  - Primary (buttons): `#FFB400` (golden yellow)
  - Accent (cyan): `#23E6FF`
  - Accent 2 (pink): `#FF6B9D`
  - Accent 3 (green): `#3DDC84`
  - Success: `#2ECC71`; Error: `#E74C3C`
  - Text: `#FFFFFF`; muted text: `#B8C4E0`
- **Fonts**: title 36+ pt bold, question 30 pt, inputs/buttons 20+ pt; Segoe UI family with helvetica fallback.
- **Layout**: full-window Canvas space background (stars + 2–3 planets) drawn on `<Configure>`; each screen is a Frame with a translucent dark panel over the canvas; progress bar + score always visible during play; 2×2 grid of large coloured multiple-choice buttons; typed input focused with Enter to submit.
- **Key screens & navigation**: Intro (animated rocket, Skip, auto-advance) → Main Menu (Play / High Scores / Help / Admin / Exit) → Name entry → Question flow (with Pause overlay + Resume) → End scene (score %, 1–3 stars, confetti, Play again / Main menu). High Scores / Help / Admin reachable from menu; Admin gated by passcode.
