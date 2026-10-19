# DESIGN_DECISIONS.md

## 1. Adaptation table (platform conflicts / infrastructure → desktop equivalent)

| Original element | Desktop equivalent | Reason |
|---|---|---|
| Web-based / browser client | Tkinter desktop window | Constraint: deliverable must be a single-user Windows desktop app |
| Microservices (Game, Question, User, Admin components) | In-process Python packages: `game/`, `questions/`, `users/` | No network; components become Python modules with the same operations |
| Node.js 18-20 / Express.js 4-5 | Python 3.11+ / stdlib + tkinter | Target language mandated |
| PostgreSQL 14-15 | SQLite file (`space_fractions.db`) | Single-user local persistence |
| Redis 6-7 / RabbitMQ 3-4 / Elasticsearch | Not needed (no sessions/messages/search at scale) | Single local user; no cross-process state |
| OAuth2 authn/authz | Local profile (username) + roles (Admin/End User) | Single-user app; login is a simple user selection |
| Prometheus / observability | Python `logging` + local log file | Local diagnostics |
| Jenkins / CI/CD | `pytest` test suite | Standard-library only testing |
| Docker / Terraform / Kubernetes / Istio / Vault / TLS / replicas | Removed (Dockerfile optional, only to run tests headless) | No deployment infra needed |
| RESTful API (`/play`, `PlayRequest`/`PlayResponse`) | In-process service interfaces: `Game.play()`, `Question.get_prompt()`, etc. | Same operations, method calls instead of HTTP |
| gRPC (`GameService.Play`) | `Game.play()` method | Same contract, in-process |
| `games` table (SERIAL, JSONB) | `games`, `questions`, `users` tables in SQLite (JSON text columns) | SQLite DDL adapted |
| Assumption A1 (1000 concurrent users) | Ignored (single local user) | Contradicts desktop target |
| Assumption A2 (1 hour session) | Session length is user-driven; no enforced limit | Desktop app, no need to cap |

## 2. Input issues found

| Code | Severity | Handling |
|---|---|---|
| EMPTY_TABLE | high | Testing matrix had empty cells. I derived a full component→test-type matrix (GameComponent and QuestionComponent both get unit + integration tests; game logic gets a state-transition test; persistence gets integration tests; UI gets E2E via smoke test in-process). |
| ARTIFACT_MISMATCH | medium | ASR-1 references `sql/question_ddl.sql` not in deliverables. I created `sql/schema.sql` containing question persistence DDL (plus games/users), satisfying data durability intent. |
| THIN_REQUIREMENTS | high | Only 4 requirement ids; implied features (intro cinematic, main menu, series of fraction questions, ending scene with feedback) got their own FR ids (FR-2..FR-5) in TRACEABILITY.csv. |
| UNTRACED_REQUIREMENT | medium | ASR-2 (security/access) added to traceability; Admin update-questions requires admin role. |
| GENERIC_JUSTIFICATIONS | medium | Each adapted tech choice gets its own concrete justification in section 1. |
| DUPLICATE_BLOCKS | low | Duplicated code blocks de-duplicated; single SQL schema used everywhere. |
| PLATFORM_CONFLICT | high | Fully adapted to desktop (see section 1); all conflict terms covered. |
| UML_SYNTAX (participant/->>/artifact) | low | Normalised: participants→objects, '->>'→'->', artifact→component/container. Code follows the class/state/sequence semantics regardless of diagram syntax. |

## 3. Assumptions made where the spec is thin

1. **Domain**: "Space Fractions" is an educational game teaching fraction concepts to children (primary-school age). Questions present a fraction and ask the player to pick (or type) the correct value.
2. **Question kinds**: multiple-choice (select correct option) and typed answer (numeric fraction). Both supported; each question has prompt, correct answer, kind, and choices (for choice questions).
3. **Computable content**: fraction questions are generated in code (random fraction → correct value computed) AND drawn from a seeded pool. Wrong choices are distinct and never equal to the correct value.
4. **Game round**: a round draws N questions at random from the combined pool (seed + admin-added) and shuffles order. Score = count of first-attempt correct answers. User may pause/resume mid-round.
5. **States**: Playing, Paused, GameOver map to a single per-round state machine with valid transitions exactly as specified; invalid transitions raise errors.
6. **Persistence**: questions and users stored in SQLite; first start seeds 24+ questions covering both kinds. Admin-added questions persist.
7. **Admin vs End User**: login screen lets user pick a profile; Admin profile unlocks "Update Questions" (add/edit/delete). End User gets Play/View Score/View Help.
8. **Intro movie / ending scene**: implemented as lightweight full-screen cinematic screens (a short animated starfield with a text caption and Continue button), not a real video (no external codecs). Ending scene shows the score with factual feedback (no praise for a zero score).

## 4. UML → code mapping

| Diagram element | Module / class | Test |
|---|---|---|
| Class `Game` (id, score, play(), viewScore()) | `game/game.py` → `Game` | `tests/test_game.py` |
| Class `Question` (id, prompt, options, getPrompt(), getOptions()) | `questions/question.py` → `Question` | `tests/test_questions.py` |
| Class `User` (id, username, playGame(game), viewScore(game)) | `users/user.py` → `User` | `tests/test_users.py` |
| Class `Admin` (id, username, updateQuestions(list)) | `users/admin.py` → `Admin` | `tests/test_admin.py` |
| Composition Game--*Question | `Game._questions` list | `tests/test_game.py` |
| Composition User--*Game, Admin--*Question | `User`/`Admin` own collections | `tests/test_users.py`, `test_admin.py` |
| States Playing/Paused/GameOver + transitions | `game/game_state.py` → `GameState` enum + `Game` transition methods | `tests/test_state_machine.py` |
| SequenceDiagram1 (User→Game→Question) | `Game.play()`, `Question.get_prompt()`, `Question.check_answer()` | `tests/test_game.py`, `test_questions.py` |
| SequenceDiagram2 (Admin→Question update) | `QuestionRepository.update/delete/insert` | `tests/test_persistence.py` |
| Use case Play Game | `ui/play_screen.py` → `PlayScreen` | `tests/test_ui_smoke.py` |
| Use case View Score | `ui/score_screen.py` → `ScoreScreen` | `tests/test_ui_smoke.py` |
| Use case View Help | `ui/help_screen.py` → `HelpScreen` | `tests/test_ui_smoke.py` |
| Use case Update Questions | `ui/admin_screen.py` → `AdminScreen` | `tests/test_ui_smoke.py`, `test_admin.py` |
| GameComponent/UserComponent/QuestionComponent | `app/controller.py` (in-process façade) | `tests/test_game.py` |

## 5. UI design brief

**Target users**: primary-school children (End User) playing a fraction-learning game, and a teacher/parent (Admin) managing questions. Mood: bright, adventurous, encouraging — "space mission" theme.

**Mood**: playful but calm; a friendly mission-control aesthetic with a deep-space background and glowing accents.

**Colour palette (hex, roles)**:
- Background (deep space): `#0B1026` (dark navy) — main window background
- Surface (panels/cards/inputs): `#1C2340` — raised panels, buttons (subtle)
- Primary (buttons/actions): `#4C6EF5` (electric blue) — main buttons
- Accent (highlights, stars): `#FFD43B` (warm gold) — title text, stars, correct highlights
- Secondary accent: `#9775FA` (soft violet) — secondary buttons, progress
- Success (correct): `#40C057` (green)
- Error (wrong): `#FA5252` (red)
- Text: `#F1F3F5` (near-white), secondary text `#ADB5BD` (grey)

**Fonts and sizes**: Tkdefault 'Segoe UI'. Title 36 bold; screen headings 30 bold; question text 26; answer/choice buttons 20; body/feedback 20; small labels 16; input 18. High contrast text on dark backgrounds.

**Layout approach**: single main window (min 1100x750, maximised on launch, F11 fullscreen, Esc exit). Each screen is a `Frame` in `ui/`, switched via `show(name)`. Canvas starfield background bound to `<Configure>` (never use winfo_width at construction). Choice answers as large padded buttons; typed answers use a big Entry with a visible "Check" button next to it, Enter submits, input auto-cleared. All screens fit 1100x750; long help text placed above the button row (packed, never covered).

**Key screens and navigation**:
- `IntroScreen` (intro "movie"): animated starfield + title "Space Fractions" + Continue
- `MenuScreen`: Play, View Score, View Help, (Admin) — buttons
- `PlayScreen`: question prompt, choice buttons OR typed answer + Check, pause button; starfield
- `PauseScreen`: Resume / Quit to menu
- `ScoreScreen` (ending scene): factual result feedback, stars/rating reflecting score, Play Again / Menu
- `HelpScreen`: scrollable instructions
- `AdminScreen`: list of questions, add/edit/delete form with a field for every attribute (prompt, correct value, kind, choices)
- `LoginScreen`: pick profile (End User / Admin)

Navigation is driven by `app/controller.py → App`, which exposes `screens` and `show(name)`.