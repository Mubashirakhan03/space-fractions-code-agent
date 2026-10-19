# DESIGN_DECISIONS.md — Space Fractions

## 1. Adaptation table (platform conflicts → desktop equivalent)

| Original element | Desktop equivalent | Reason |
|---|---|---|
| Web-based (Express.js) | Tkinter desktop app (`main.py` + `ui/`) | Task constraint: single-user Windows desktop deliverable, not a web app |
| Microservices (GameComponent, QuestionComponent, UserComponent, AdminComponent) | In-process Python packages `game/`, `question/`, `user/`, `admin/` with the same responsibilities and public operations | Same logical architecture; no network boundary needed for a single user |
| Node.js 18–20 | Python 3.11+ standard library | Bundled-runtime constraint |
| PostgreSQL 14–15 | SQLite file (`sql/schema.sql`, `game.db`) | Single local user; SQLite is bundled |
| RESTful API (`/play`, openapi.yaml) | In-process Python interface `GameService.play(game_id)` | All operations are local; no HTTP |
| internal.proto (GameService.Play rpc) | `GameService.play()` method with typed returns | RPC → direct call |
| Redis 6–7 | In-memory `functools.lru_cache` / plain dict for session state | No cross-process cache needed |
| RabbitMQ 3–4 | Synchronous calls / `queue.Queue` within the app | No async messaging for a single user |
| Elasticsearch 7–8 | SQLite `LIKE`/filter queries | Local search over a small question pool |
| OAuth2 | In-window PIN gate (default `1234`, documented in README) | Admin role protection per UI rules; no remote IdP |
| Prometheus 2–3 | In-app stats (scores, totals) shown on Score screen | Observability read locally |
| Jenkins CI/CD, Docker, Terraform, Kubernetes, replicas, Vault, Istio, TLS | Not applicable (single desktop); optional `Dockerfile` runs pytest headless | No deployment pipeline for a desktop app |
| `games` table (JSONB game_state) / `question_ddl.sql` | SQLite `games` and `questions` tables | Adapted DDL to SQLite types |

## 2. Input issues found

- **EMPTY_TABLE (high):** testing-matrix cells empty → provide a complete testing matrix (component × test type → Python package/test file) in DESIGN_DECISIONS §4 and TRACEABILITY.csv.
- **ARTIFACT_MISMATCH (medium):** ASR-1 references `sql/question_ddl.sql` but deliverables lack it → we ship `sql/schema.sql` covering `questions` and `games`, noted in README mapping.
- **THIN_REQUIREMENTS (high):** only 4 requirement ids; features from summary (introductory movie, main menu, series of fraction questions, ending scene) have no FRs → created FR-2…FR-5 and mapped each to a screen + test.
- **UNTRACED_REQUIREMENT (medium):** ASR-2 absent from matrix → added to TRACEABILITY.csv.
- **GENERIC_JUSTIFICATIONS (medium):** 12 tech choices share 3 justifications → resolved by the adaptation table above; each is replaced by a desktop equivalent with an explicit reason.
- **DUPLICATE_BLOCKS (low):** 4 duplicated code blocks → irrelevant after adapting openapi/proto/sql to a desktop app; only one SQLite schema remains.
- **PLATFORM_CONFLICT (high):** web/cloud system → full desktop adaptation recorded in §1.
- **UML_SYNTAX (low × 8):** Mermaid arrows / artifact-vs-component / participant-vs-object → normalised to the class diagram, activity diagram and state machine in §4.

## 3. Assumptions where the spec is thin

- The game is an educational **fractions quiz**: each question shows a fraction prompt; the player picks the correct value among shuffled options. Question kinds implemented: fraction-equivalence (given a/b, pick p/q such that value equals), simplification (reduce to lowest terms), decimal conversion, and "which is larger/smaller". Correct values are **computed in code**; wrong options are distinct and never equivalent to the correct one.
- Questions also **generate new items per round** from code (computable content), so every round randomized + shuffled; two rounds differ.
- A "game" = series of N questions (default 10) drawn/generated randomly; score = correct count; ending scene shows score, a rating (e.g. "Excellent / Good / Keep practising") that only praises a strong result, and details of answers.
- States **Playing / Paused / GameOver** map to a pause button during play and the ending screen (GameOver); Paused pauses the timer/round and shows a resume button.
- Admin "Update Questions" = add / edit / delete questions in the SQLite store; protected by PIN `1234` (stored in `data/settings.json`, changeable, documented in README).
- Session length ("1 hour", "1000 concurrent") is irrelevant for a single desktop user; we still time each game and persist per-session history.

## 4. UML → code mapping

| Diagram element | Module / class | Test |
|---|---|---|
| Class `Game` (id, score; play(), viewScore()) | `game/game.py:Game` | `tests/test_game.py` |
| Class `Question` (id, prompt, options; getPrompt(), getOptions(), + checkAnswer()) | `question/question.py:Question` | `tests/test_question.py` |
| Class `User` (id, username; playGame(), viewScore()) | `user/user.py:User` | `tests/test_user.py` |
| Class `Admin` (id, username; updateQuestions()) | `admin/admin.py:Admin` | `tests/test_admin.py` |
| `Game --* Question` composition | `Game` holds a list of `Question` | `tests/test_game.py` |
| `User --* Game`, `Admin --* Question` | owned collections | `tests/test_user.py`, `tests/test_admin.py` |
| State machine Playing/Paused/GameOver (+pause/resume/gameOver) | `game/state.py:GameStateMachine` | `tests/test_state_machine.py` (valid + invalid transitions) |
| Activity diagram (play → game over? → continue → score → display score) | `game/game.py` round loop + `GameService` | `tests/test_game.py` |
| SequenceDiagram1 (play → getPrompt → submit → check → result) | `GameService.play_round` | `tests/test_game.py` |
| SequenceDiagram2 (Admin → Question update → success) | `admin/admin.py` + store | `tests/test_admin.py` |
| Use cases: Play Game / View Score / View Help / Update Questions | `ui/play_screen.py`, `ui/score_screen.py`, `ui/help_screen.py`, `ui/admin_screen.py` | `tests/test_ui_smoke.py` |
| Components Game/Question/User/Admin | packages `game/`, `question/`, `user/`, `admin/` | respective tests |

## 5. UI design brief

**Target users:** primary-school to early-secondary children and their teachers/parents (Admin) learning fractions. **Mood:** bright, encouraging, space-exploration theme — playful and motivating, like a rocket trip through the solar system.

**Palette** (dark space background with bright accents):
- background `#0B1026` (deep space navy)
- surface `#1A2140` (panel/card navy)
- primary `#4C5BF0` (indigo action buttons)
- accent `#FFB703` (warm star-yellow highlights, correct answers)
- success `#2DC653` (green)
- error `#E63946` (red)
- text `#F1FAEE` (near-white), muted text `#9AA7D4`

**Fonts:** Segoe UI / Tk default family; title 32–36 pt bold, content 24–28 pt, buttons/inputs 18–20 pt bold. High contrast (light text on dark).

**Layout:** main window ≥ 1100×750, maximized on start; F11 fullscreen toggle; bottom or right navigation with large padded flat buttons + hover colour. Each screen a `tk.Frame`. Long help/summary text in a scrollable `Text` above buttons (never covering text).

**Key screens (each an App.screens entry):**
1. **Intro movie** — animated Canvas (rocket + stars move, 5–10 s), Skip button, auto-advance to menu.
2. **Main menu** — Play, View Score, View Help, Admin (PIN-gated), Exit.
3. **Play** — fraction questions with shuffled options (choice buttons) and some typed answers; pause button; correct/wrong feedback naming the expected value.
4. **Results / ending scene** — score + rating driven by real result, answer review, Play Again.
5. **Score** — history table from store.
6. **Help** — instructions.
7. **Admin PIN** — masked entry (`show="*"`), Unlock button, red error on wrong PIN.
8. **Admin questions** — add/edit/delete forms with every field (prompt, correct value, kind); reached only through the PIN screen; locks again on leaving.
