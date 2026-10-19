# RUN_REPORT — Code Agent run

> **Live run**

| Item | Value |
|---|---|
| Generated (UTC) | 2026-10-19 11:49:06 |
| Provider | DeepSeek (official) |
| Model | `deepseek-v4-pro` |
| Inputs | Architecture_Documentation.md, Architecture_View.md |
| Task profile | Space Fractions |
| Status | **completed** |
| Verification | FAILED |
| Fix rounds used | 3 / 3 |
| LLM requests | 47 (limit 80) |
| Agent steps | 47 |
| Context compactions | 0 |
| Prompt tokens | 1,641,930 (cache hit 1,615,872 / miss 26,058) |
| Completion tokens | 35,029 |
| Estimated cost | $0.1221 (cap $1.00) |
| Duration | 487 s |

## Generated files

- `AGENT_NOTES.md` (1,268 bytes)
- `DESIGN_DECISIONS.md` (6,939 bytes)
- `Dockerfile` (119 bytes)
- `README.md` (2,049 bytes)
- `TRACEABILITY.csv` (1,141 bytes)
- `admin/__init__.py` (44 bytes)
- `admin/service.py` (1,572 bytes)
- `data/questions.json` (2,901 bytes)
- `data/spacefractions.db` (24,576 bytes)
- `game/__init__.py` (71 bytes)
- `game/controller.py` (2,838 bytes)
- `game/models.py` (1,884 bytes)
- `game/state_machine.py` (1,627 bytes)
- `main.py` (343 bytes)
- `questions/__init__.py` (65 bytes)
- `questions/checker.py` (2,412 bytes)
- `questions/model.py` (1,364 bytes)
- `questions/repository.py` (3,521 bytes)
- `requirements.txt` (31 bytes)
- `scores/__init__.py` (51 bytes)
- `scores/repository.py` (2,054 bytes)
- `sql/schema.sql` (965 bytes)
- `tests/__init__.py` (21 bytes)
- `tests/test_game.py` (2,368 bytes)
- `tests/test_persistence.py` (2,193 bytes)
- `tests/test_questions.py` (1,929 bytes)
- `tests/test_state_machine.py` (1,378 bytes)
- `tests/test_ui_smoke.py` (4,149 bytes)
- `tests/test_users.py` (1,039 bytes)
- `ui/__init__.py` (24 bytes)
- `ui/app.py` (3,615 bytes)
- `ui/screens/__init__.py` (23 bytes)
- `ui/screens/admin.py` (7,409 bytes)
- `ui/screens/base.py` (1,412 bytes)
- `ui/screens/end.py` (3,390 bytes)
- `ui/screens/help.py` (1,428 bytes)
- `ui/screens/high_scores.py` (1,628 bytes)
- `ui/screens/intro.py` (2,419 bytes)
- `ui/screens/menu.py` (1,575 bytes)
- `ui/screens/name_entry.py` (1,762 bytes)
- `ui/screens/question.py` (6,732 bytes)
- `ui/spacebg.py` (3,107 bytes)
- `ui/theme.py` (1,083 bytes)
- `users/__init__.py` (39 bytes)
- `users/model.py` (588 bytes)

## Todo list (final)

- [x] Create package skeleton (game, questions, users, admin, ui) and theme
- [x] Implement domain logic: Game, state machine, scoring, Question, answer checking
- [x] Implement repositories + SQLite persistence + schema.sql + questions.json
- [x] Implement UI screens: intro, menu, name entry, question, pause, end, high scores, help, admin
- [x] Wire app controller, main.py, keyboard/fullscreen handling
- [x] Write domain/state/persistence tests + UI smoke test
- [x] Write README, TRACEABILITY.csv, AGENT_NOTES, requirements.txt, Dockerfile
- [x] Compile and run tests, fix failures

## Input issues detected during preprocessing

- **EMPTY_TABLE** (high): Table under 'Matrix mapping Unit / Integration / Contract / E2E / Chaos tests to components' has headers but every cell is empty.
- **ARTIFACT_MISMATCH** (medium): ASR-1 references 'sql/question_ddl.sql' but the deliverables list does not contain it (deliverables: k8s/spacefractions-deployment.yaml, sql/game_ddl.sql).
- **THIN_REQUIREMENTS** (high): Only 4 requirement ids exist (ASR-1, ASR-2, FR-1, NFR-1); features from the summary (introductory movie, main menu, series of fraction questions, ending scene with feedback) have no FR of their own.
- **UNTRACED_REQUIREMENT** (medium): Not in the traceability matrix: ASR-2.
- **GENERIC_JUSTIFICATIONS** (medium): 12 technology choices share only 3 copy-pasted justifications (e.g. 'meets ASR-1 (data durability)' for Jenkins 2-3).
- **DUPLICATE_BLOCKS** (low): 4 code block(s) appear more than once verbatim.
- **PLATFORM_CONFLICT** (high): Document targets a web/cloud microservice system (web-based, microservices, Node.js, Express.js, PostgreSQL, Redis, RabbitMQ, Elasticsearch, OAuth2, Prometheus…) but the required deliverable is a single-user desktop application.
- **UML_SYNTAX** (low): ObjectDiagram: Object diagram uses 'participant' (sequence syntax) instead of 'object'; participants treated as objects.
- **UML_SYNTAX** (low): SequenceDiagram1: 8 Mermaid-style '->>' arrow(s) are not PlantUML; normalised to '->'.
- **UML_SYNTAX** (low): SequenceDiagram2: 2 Mermaid-style '->>' arrow(s) are not PlantUML; normalised to '->'.
- **UML_SYNTAX** (low): CollaborationDiagram1: 8 Mermaid-style '->>' arrow(s) are not PlantUML; normalised to '->'.
- **UML_SYNTAX** (low): CollaborationDiagram2: 2 Mermaid-style '->>' arrow(s) are not PlantUML; normalised to '->'.
- **UML_SYNTAX** (low): ComponentDiagram: Component diagram declares its parts with 'artifact' instead of 'component'.
- **UML_SYNTAX** (low): ContainerDiagram: Container diagram declares its parts with 'artifact' instead of 'container'.

## Verification output

```text
COMPILE OK: All 36 Python files compile.

TESTS PASSED:
.........................................                                [100%]

UI LAYOUT PROBLEMS (268) found by opening the real window (checked: startup view @1280x800, screen 'intro' @1280x800, screen 'menu' @1280x800, screen 'name_entry' @1280x800, screen 'question' @1280x800, screen 'end' @1280x800, screen 'high_scores' @1280x800, screen 'help' @1280x800, screen 'admin' @1280x800, screen 'intro' @1100x750, screen 'menu' @1100x750, screen 'name_entry' @1100x750, screen 'question' @1100x750, screen 'end' @1100x750, screen 'high_scores' @1100x750, screen 'help' @1100x750, screen 'admin' @1100x750):
- screen 'admin' @1280x800: Button 'Which fraction is smaller: 5/8' is outside the visible window (centre at 573,828 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,828 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Which fraction is bigger: 7/10' is outside the visible window (centre at 573,882 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,882 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'What is 1/4 + 1/4?' is outside the visible window (centre at 573,936 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,936 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'What is 1/3 + 1/6?' is outside the visible window (centre at 573,990 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,990 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'What is 3/4 - 1/4?' is outside the visible window (centre at 573,1044 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,1044 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'What is 2/3 - 1/6?' is outside the visible window (centre at 573,1098 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,1098 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'What is 1/2 + 1/3?' is outside the visible window (centre at 573,1152 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,1152 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'What is 3/5 - 1/10?' is outside the visible window (centre at 573,1206 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,1206 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Simplify 2/4 to lowest terms.' is outside the visible window (centre at 573,1260 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,1260 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Simplify 6/8 to lowest terms.' is outside the visible window (centre at 573,1314 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,1314 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Simplify 4/6 to lowest terms.' is outside the visible window (centre at 573,1368 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,1368 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Simplify 8/12 to lowest terms.' is outside the visible window (centre at 573,1422 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Delete' is outside the visible window (centre at 1181,1422 in a 1280x800 window)
- screen 'admin' @1280x800: Button 'Simplify 10/15 to lowest terms' is outside the visible window (centre at 573,1476 in a 1280x800 window)
```

## Agent run artefacts

- `agent_run/spec.json` — structured input
- `agent_run/transcript.jsonl` — full transcript
- `agent_run/state.json` — resumable state
- `agent_run/tool-results/` — full long tool outputs
