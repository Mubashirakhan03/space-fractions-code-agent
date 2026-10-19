# DESIGN_DECISIONS.md — Space Fractions

## 1. Adaptation table (original element → desktop equivalent → reason)

| Original element | Desktop equivalent | Reason |
|---|---|---|
| web-based / microservices | single-process modular Python packages (`game/`, `questions/`, `users/`, `admin/`, `ui/`) | Target is a single-user Windows desktop app; no client/server split needed |
| Node.js / Express.js | Python 3.11 + Tkinter | Target platform mandates Python + tkinter |
| GameComponent | `game/` package (`Game`, state machine, scoring) | Maps component responsibility to in-process module |
| QuestionComponent | `questions/` package (`Question`, checker, repository) | Same responsibility, local |
| UserComponent | `users/` package (`User`) | Local player identity, no auth server |
| AdminComponent (implied) | `admin/` package (`Admin`) | Question management use case (`Update Questions`) |
| RESTful API (`/play`, OpenAPI) | `Game.play()` / `User.playGame()` in-process method calls | No network; same operation, direct call |
| gRPC proto `GameService.Play` | `Game.play()` method | Same operation migrated to class method |
| PostgreSQL | SQLite file (`sql/schema.sql`, `data/spacefractions.db`) | Single local user, file persistence mandated |
| JSONB `game_state` column | `games.game_state` stored as JSON TEXT | SQLite has no JSONB; JSON-serialisable state kept as TEXT |
| `question_ddl.sql` (referenced by ASR-1) | `sql/schema.sql` `questions` table | Deliverable correction: question persistence realised in SQLite |
| Redis (cache) | in-memory question cache in repository | Single user, no distributed cache needed |
| RabbitMQ (messaging) | direct in-process calls / Tkinter `after()` | No async message bus needed |
| Elasticsearch (search) | SQL `LIKE` / in-memory filter over question list | Local datasets are small |
| OAuth2 (authn/z) | local name entry + optional admin PIN-less local role screen | No remote identity provider for single user |
| Prometheus (observability) | stdlib `logging` | Local diagnostics only |
| Jenkins / Docker / Terraform | `tests/` with pytest (pytest optional) | CI-equivalent for a desktop deliverable |
| Kubernetes / replicas / Istio / TLS / Vault | n/a (single local instance) | No cluster, no secrets store, no transport security |

## 2. Input issues found

| Issue code | How I handled it |
|---|---|
| EMPTY_TABLE (testing matrix cells empty) | Derived a concrete test matrix from components × test types in TRACEABILITY.csv and implemented unit/integration/smoke tests |
| ARTIFACT_MISMATCH (`question_ddl.sql` missing) | Added `questions` table to `sql/schema.sql`; satisfied ASR-1 in SQLite |
| THIN_REQUIREMENTS (implied features lack FRs) | Gave each implied feature (intro movie, main menu, question series, ending scene) explicit rows in TRACEABILITY.csv and full implementation |
| UNTRACED_REQUIREMENT (ASR-2 missing) | Added ASR-2 (authn/z for admin) rows; realised as local admin screen gating |
| GENERIC_JUSTIFICATIONS | Replaced with per-component, honest justifications in traceability |
| DUPLICATE_BLOCKS | Kept single canonical copy of OpenAPI/proto/SQL in this repo's sql/ |
| PLATFORM_CONFLICT (web/cloud vs desktop) | The governing conflict; resolved per Section 1 adaptation table |
| UML_SYNTAX (Mermaid arrows, artifact/participant misuse) | Normalised per spec; treated object/participant elements as objects/components |

## 3. Assumptions made where the spec is thin

- A "round" is 10 questions (progress text "Question 3 of 10" given in task profile).
- Correctness uses `fractions.Fraction` so equivalent forms are accepted (e.g. `2/4` == `1/2`).
- Four question types: equivalent fractions, compare, add/subtract, simplify; each has a numeric (`Fraction`) answer and may provide multiple-choice options.
- Scoring: +1 per correct answer; percentage = score / questions × 100; stars = 3 for ≥90%, 2 for ≥70%, 1 for ≥50%, else 0.
- `scores` table persists (player name, score, total, percentage, timestamp) for the High Scores screen.
- Admin screen lets Admin add / edit / delete questions (Update Questions), persisted to SQLite and to `data/questions.json` seed source.
- The intro "movie" is a Tkinter Canvas animation (stars + rocket) with Skip and auto-advance via `after()`.
- Pause/Resume implement the Playing ⇄ Paused state machine; invalid transitions (e.g. pause when GameOver) raise a `StateError`.

## 4. UML → code mapping

| Diagram element | Module / class / test |
|---|---|
| Game class | `game/game.py:Game` — tests/test_game.py |
| Question class | `questions/question.py:Question` — tests/test_questions.py |
| User class | `users/user.py:User` — tests/test_users.py |
| Admin class | `admin/admin.py:Admin` — tests/test_admin.py |
| Game --* Question (composition) | `Game.questions: list[Question]` |
| User --* Game (composition) | `User.games` held by session |
| Admin --* Question (composition) | `Admin.updateQuestions()` manages repository |
| State machine (Playing/Paused/GameOver) | `game/state_machine.py` — tests/test_state_machine.py (valid + invalid) |
| SequenceDiagram1 (play flow) | `ui/question_screen.py` + `Game` methods |
| SequenceDiagram2 (admin update) | `ui/admin_screen.py` + `Admin.updateQuestions()` |
| Use case Play Game | `ui/question_screen.py`, `Game.play()` |
| Use case View Score | `ui/high_scores_screen.py`, `Game.viewScore()` |
| Use case View Help | `ui/help_screen.py` |
| Use case Update Questions | `ui/admin_screen.py` |
| games/question_ddl SQL | `sql/schema.sql`, `data/questions.json` — tests/test_persistence.py |

## 5. UI design brief

**Target users:** 11–12 year-old 6th-grade students (players) and a teacher/admin maintaining questions.

**Mood:** playful, adventurous, encouraging — an outer-space journey through fraction practice. Bright, high-energy but calm enough to focus on a math problem.

**Colour palette (hex):**

| Role | Hex |
|---|---|
| Background (deep space) | `#0B1736` |
| Panel / surface | `#16285A` |
| Surface alt | `#1E3A75` |
| Primary (yellow) | `#FFD54A` |
| Accent (cyan) | `#4DD0E1` |
| Accent (pink) | `#FF6B9D` |
| Accent (green) | `#69F0AE` |
| Success (correct) | `#69F0AE` |
| Error (incorrect) | `#FF5252` |
| Text | `#F5F7FF` |
| Text muted | `#B8C4E0` |

**Fonts:** Tk default families rendered large — titles 36+ pt bold (48 pt for menu title), questions 30 pt, body 26 pt, buttons/inputs 20+ pt. High contrast text on dark panels.

**Layout approach:** one full-window `tk.Canvas` per screen for the animated space background (stars, planets), with normal widgets placed via `grid`/`place(relx, rely)`; backgrounds and decorations redrawn on `<Configure>` using `event.width/height` (never at construction).

**Key screens & navigation:**
1. **Intro** — animated rocket/starfield, title, Skip → auto-advance to menu.
2. **Main menu** — Play, High Scores, Help, Admin, Exit.
3. **Name entry** — player name, big input, Enter submits → question flow.
4. **Question** — progress ("Question 3 of 10") + progress bar, always-visible score, question prompt, 2×2 coloured multiple-choice buttons or typed answer, Pause button, big green/red feedback, input cleared automatically, next question after ~1 s.
5. **Pause overlay** — Resume (→ Playing) and Quit to menu.
6. **End scene** — "Congratulations, <name>!", score/percentage, 1–3 stars, confetti animation, Play again / Main menu.
7. **High Scores** — table of top scores from SQLite.
8. **Help** — how to play.
9. **Admin** — list + add/edit/delete questions.

**Navigation contract:** `ui/app.py:create_app(root) -> App` builds all screens; `App.screens: dict[str, tk.Frame]`; `App.show(name)`. Every screen renders safely when shown directly (empty data → friendly defaults).