# DESIGN DECISIONS — Space Fractions

## 1. Adaptation table (original element → desktop equivalent → reason)

| Original element | Desktop equivalent | Reason |
|---|---|---|
| Node.js 18-20 runtime | Python 3.11+ standard library | Bundle into a single-user .exe; no runtime install needed |
| Express.js 4-5 web framework | Tkinter (+ ttk) screens switched by an App controller | Desktop GUI replaces HTTP routes |
| RESTful API (`/play` GET) | In-process `Game.play()` and `GameService`-style interface | Single-user desktop: no network boundary needed |
| gRPC/proto `GameService.play(PlayRequest)` | Python `game.game_service.play(game: Game)` interface | Same operation, in-process call |
| PostgreSQL 14-15 | SQLite file (`sql/schema.sql`, `data/space_fractions.db`) | Single local user, no server; stdlib `sqlite3` |
| `games` table (JSONB game_state) | `games` table with state as TEXT/JSON plus normalised columns | SQLite has no JSONB; store serialised state |
| `question_ddl.sql` (referenced, missing) | `sql/schema.sql` questions table + `questions.json` seed | Reconstruct the documented-but-missing DDL |
| Redis cache | In-memory question cache (`functools.lru_cache`) | No shared cache needed for one user |
| RabbitMQ messaging | Direct method calls / event queue in controller | No async decoupling needed |
| Elasticsearch search | Standard library indexing / in-memory search | Local dataset search only |
| OAuth2 authn/authz | Local login (username prompt; Admin via a role) | No third-party identity provider offline |
| Prometheus observability | `logging` to file + in-app trace | No metrics server needed |
| Jenkins CI/CD | pytest suite + Dockerfile for headless CI | Reproducible verification |
| Docker/K8s/Terraform/Istio/replicas/Vault/TLS | N/A (single-user desktop) | Removed; documented in AGENT_NOTES.md |
| 1000 concurrent users / 1-hour sessions (A1, A2) | Single sequential session model | Concurrency assumptions do not apply to desktop |

## 2. Input issues found

| Issue | Handling |
|---|---|
| EMPTY_TABLE (testing matrix headers, empty cells) | Implement tests matching the matrix's stated types: unit, integration (repository+game), contract (answer-checking), E2E (full game via app controller), persistence tests. Document mapping in TRACEABILITY.csv. |
| ARTIFACT_MISMATCH (`sql/question_ddl.sql` missing) | Create `sql/schema.sql` covering games, questions, scores; note it replaces question_ddl.sql. |
| THIN_REQUIREMENTS (implied features lack FRs) | Treat implied_features (intro, menu, fraction questions, ending feedback) as requirements FR-2…FR-6 and trace them. |
| UNTRACED_REQUIREMENT (ASR-2) | Add ASR-2 (security) = local data file permissions + no secret storage; trace to users/admin. |
| GENERIC_JUSTIFICATIONS | Re-justified each technology mapping concretely in §1. |
| DUPLICATE_BLOCKS | Normalised; single source of truth per artifact. |
| PLATFORM_CONFLICT | Full desktop adaptation per §1; web infra removed. |
| UML_SYNTAX (`->>` not PlantUML; `artifact` vs component/container; `participant` in object diagram) | Normalised to `->`; components/containers treated as components; participants as objects. No code impact. |

## 3. Assumptions where the spec is thin

- A "round" is 10 questions (task profile: "Question 3 of 10").
- Answer checking accepts equivalent fractions: `Fraction(input) == Fraction(answer)` so 2/4 == 1/2.
- Four question types: equivalent, compare, add/subtract, simplify (per task profile).
- Scoring: 100 points per correct answer; percentage = correct/answered×100; 1–3 stars by percentage (≥50/≥75/≥90).
- Pausing is allowed only between answers; invalid transitions raise (state machine contract).
- Admin screen requires an admin username (`admin`) to gate editing, satisfying ASR-2 locally.
- High scores persist a `name`, `score`, `percentage`, `stars`, `played_at` per game.

## 4. UML → code mapping

| Diagram element | Module / class | Test |
|---|---|---|
| Class `Game` (id, score; play, viewScore) | `game/game.py` → `Game` | `tests/test_game.py` |
| Class `Question` (id, prompt, options; getPrompt, getOptions) | `questions/question.py` → `Question` | `tests/test_questions.py` |
| Class `User` (id, username; playGame, viewScore) | `users/user.py` → `User` | `tests/test_users.py` |
| Class `Admin` (id, username; updateQuestions) | `admin/admin.py` → `Admin` | `tests/test_admin.py` |
| Rel. Game --* Question; User --* Game; Admin --* Question (composition) | Lists owned by composing class | same tests |
| Component GameComponent | `game/` | `tests/test_game.py` |
| Component QuestionComponent | `questions/` (Question + QuestionRepository) | `tests/test_questions.py`, `tests/test_persistence.py` |
| Component UserComponent | `users/` | `tests/test_users.py` |
| Component AdminComponent | `admin/` | `tests/test_admin.py` |
| State machine [\*]→Playing, Playing⇄Paused, Playing→GameOver | `game/game_state.py` (enum + transition table) | `tests/test_state_machine.py` |
| SequenceDiagram1 (play, getPrompt, submit, check, result) | `game/game_service.py` + `questions/` + UI flow | `tests/test_sequences.py` |
| SequenceDiagram2 (Admin→updateQuestions) | `admin/admin.py` | `tests/test_admin.py` |
| Use cases Play Game / View Score / View Help / Update Questions | UI screens + services | `tests/test_ui_smoke.py` |
| Activity diagram (start→play→score→display→stop) | `game/game_service.play_round()` | `tests/test_sequences.py` |
| OpenAPI/proto/SQL | `sql/schema.sql` (+ in-process interfaces) | `tests/test_persistence.py` |

## 5. UI design brief

- **Users**: 6th-grade students (11–12 yrs) as End Users; teachers/parents as Admin.
- **Mood**: playful, encouraging, space-exploration adventure ("Space Fractions" — travel through space solving fractions).
- **Palette** (ui/theme.py):
  - background `#0B1736` (deep space navy), surface `#16264A` (panels), surface-alt `#1D2F5C`
  - primary `#FFD166` (warm yellow star), accent `#36E0D0` (cyan), accent-2 `#FF6EC7` (pink), accent-3 `#6EEB7E` (green)
  - success `#6EEB7E`, error `#FF6B6B`, text `#F2F6FF`, text-muted `#9FB0D8`
- **Fonts**: Segoe UI default; titles 36–40 pt bold, questions 30 pt, input/buttons 20 pt, body/labels 16–20 pt.
- **Layout**: Canvas starfield background on every screen (drawn on `<Configure>`); dark rounded "surface" panels; 2×2 grid of large coloured answer buttons; progress bar + "Question N of 10"; score always visible; Pause button; pause overlay with Resume.
- **Key screens**: Intro (animated rocket + stars, Skip, auto-advance), Main Menu, Name entry, Question, Pause overlay, Ending (score/percentage/stars + confetti + Play again/Menu), High Scores, Help, Admin.
- **Navigation**: App controller `ui/app.py` with `screens` dict and `show(name)`; every screen is a Frame class; F11 full screen, Esc exit full screen, maximized on startup, min size 1100×750.
- **Feedback**: green "Correct! 🎉" / red "Not quite — the answer is 3/4"; input cleared automatically; next question after ~1s; Enter submits; messagebox only for confirmations.