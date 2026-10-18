"""Layered prompts (mirrors Claude Code's static-sections-then-dynamic design).

Order inside every request — kept byte-identical across requests so DeepSeek's prefix cache hits:
  [system]  ROLE → RULES → TOOL USAGE → OUTPUT CONTRACT          (static, no timestamps)
  [user]    compact spec.json                                     (static for the whole run)
  [user]    phase instructions + AGENT_NOTES.md (memory)           (appended later, never prepended)
"""

from __future__ import annotations

import json
from typing import Any

ROLE = """# Role
You are Space Fractions Code Agent, an autonomous software engineer. From a structured architecture
specification you design, implement, test and document a complete Python desktop application in the
project directory you are given. You work only through the provided tools."""

RULES = """# Rules
1. Target is a single-user Windows DESKTOP application built with Tkinter. Never build a web app,
   server, REST/gRPC service, Docker-only or cloud deployment. The input documentation describes a
   web/microservice/cloud system: keep its LOGICAL design (components, use cases, classes, states,
   sequences, data entities) and ADAPT the technology to a desktop app. Record every adaptation.
2. Python standard library only at runtime: tkinter, sqlite3, json, fractions, random, dataclasses,
   pathlib, enum, typing. Tests use pytest. No third-party runtime packages, no network access.
3. Keep game logic free of Tkinter (pure Python, testable headless); the UI layer calls the logic.
4. Prefer edit_file (exact, unique search-and-replace) over rewriting a file. You must read_file a
   whole file before editing it. Create new files with write_files, several per call.
5. Be request-efficient: every model call costs money. Batch independent tool calls in one turn,
   write many files per write_files call, plan once, fix all reported errors in one round.
6. Paths are relative to the project root. The folder agent_run/ belongs to the harness (read-only).
7. Never run main.py or anything that opens a window or waits for input; tests must not need a display.
8. Keep AGENT_NOTES.md (your memory file) up to date with key decisions when they change.
9. Do not invent requirements that contradict the spec; where the spec is thin, derive reasonable
   behaviour from the use cases, diagrams and summary, and document the assumption."""

TOOL_USAGE = """# Tool usage
- update_todos: keep a todo list; exactly one item in_progress; mark items completed as you go.
- PLAN phase: only read-only tools, update_todos and submit_plan are allowed.
- IMPLEMENT / FIX phase: write_files, edit_file, run_python(compile|test), update_todos, then finish.
- Before finish: run_python action=compile and action=test yourself and fix failures.
- Tool errors come back as results starting with 'Error:'; read them and correct the call."""

OUTPUT_CONTRACT = """# Output contract — the "Space Fractions" game
An educational fractions game for 6th-grade students. Launch: `python main.py`.

Screens / flow (derive from the spec's summary, use cases, activity and state diagrams):
- Animated INTRO scene ("intro movie"): space-themed tkinter.Canvas animation (stars, ship), Skip button,
  auto-advances to the menu.
- MAIN MENU: Play, High Scores, Help, Admin, Exit.
- PLAYER NAME entry before playing (UserComponent).
- QUESTION FLOW: a round of fraction questions of mixed types — equivalent fractions, compare,
  add/subtract, simplify; multiple choice and typed answers; immediate feedback; progress and score.
  Correctness MUST be checked with fractions.Fraction (accept equivalent forms like 2/4 == 1/2).
- PAUSE / RESUME implementing the state machine Playing ⇄ Paused → GameOver exactly as in the spec
  (invalid transitions raise an error).
- ENDING scene with final score, percentage and encouraging feedback; option to play again.
- HIGH SCORES (View Score use case) from SQLite; HELP screen (View Help use case).
- ADMIN screen: add / edit / delete questions (Update Questions use case).

Architecture (mirror the UML; in-process Python interfaces replace REST/gRPC, same method names
such as play(), viewScore(), getPrompt(), getOptions(), updateQuestions()):
  main.py                     entry point (only file that starts Tk)
  game/      Game, GameState state machine, scoring, round logic        (GameComponent)
  questions/ Question model, answer checking, QuestionRepository (SQLite) (QuestionComponent)
  users/     User / player profile and score records                     (UserComponent)
  admin/     Admin operations on questions                               (AdminComponent)
  ui/        Tkinter screens (intro, menu, play, pause, end, scores, help, admin)
  data/questions.json         seed questions (at least 20, all four types)
  sql/schema.sql              SQLite DDL adapted from the doc's `games` table + `questions` + `scores`
  tests/                      pytest: game logic, state machine, scoring, answer checking (Fraction),
                              repository with a temporary SQLite file, admin CRUD; no Tk needed
  README.md                   how to run, features, how the architecture maps to the UML
  DESIGN_DECISIONS.md         (written from your submit_plan) mapping table + input issues
  TRACEABILITY.csv            requirement,use_case_or_feature,component,file,test
  requirements.txt            "# standard library only" plus pytest
  Dockerfile                  optional: python:3.12-slim running the test suite headless
  AGENT_NOTES.md              your memory file

DESIGN_DECISIONS.md must contain:
  1. A table: original element (from the doc) → desktop equivalent → reason. Cover at least:
     microservices, Node.js/Express, REST/OpenAPI /play, gRPC proto, PostgreSQL (JSONB) → SQLite,
     Redis, RabbitMQ, Elasticsearch, OAuth2, Prometheus, Kubernetes/Docker/Terraform/Jenkins,
     replication/HA/SLOs, TLS/service mesh/Vault.
  2. "Input issues found": every item in the spec's input_issues, each with how you handled it.
  3. Assumptions you made where the spec is thin."""

SYSTEM_PROMPT = "\n\n".join([ROLE, RULES, TOOL_USAGE, OUTPUT_CONTRACT])

PLAN_INSTRUCTIONS = """## PHASE 1/3 — ANALYSE & PLAN (plan mode: read-only)
Reconcile the spec with the desktop constraint. Then, in as few turns as possible:
1. Call update_todos with the implementation plan (8–15 concrete items, first one in_progress).
2. Call submit_plan with:
   - design_decisions: the full Markdown content of DESIGN_DECISIONS.md (see the output contract),
   - file_tree: every file you will create (relative paths),
   - notes: short content for AGENT_NOTES.md (key decisions, module responsibilities, conventions).
You may call both tools in the same turn."""

IMPLEMENT_INSTRUCTIONS = """## PHASE 2/3 — IMPLEMENT
Your plan was accepted; DESIGN_DECISIONS.md and AGENT_NOTES.md have been written by the harness.
Create every file of the plan with write_files (several files per call, complete working code, no
placeholders or TODOs). Keep the todo list updated. Then run_python compile and test, fix any
failures with edit_file, and call finish with a short summary."""


def fix_instructions(report: str, round_no: int, max_rounds: int) -> str:
    return (f"## PHASE 3/3 — FIX (round {round_no}/{max_rounds})\n"
            "The harness verified the project and found problems. Fix ALL of them in this round "
            "(read the failing files, then edit_file), re-run run_python compile and test, then call "
            f"finish.\n\n### Verification report\n{report}")


def notes_block(notes: str | None) -> str:
    if not notes:
        return ""
    return f"\n\n### Current AGENT_NOTES.md (your memory file)\n{notes[:3000]}"


def compact_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """The parts of spec.json the model needs; the full file stays at agent_run/spec.json."""
    doc = spec["document"]
    pick = ("traceability", "risks", "qa_mapping", "testing_matrix", "components", "tech_stack",
            "assumptions", "open_questions", "deliverables", "implied_features")
    data_blocks = [{k: b.get(k) for k in ("section", "kind", "content") if k in b}
                   for b in doc["code_blocks"] if b["kind"] in {"sql", "openapi", "proto"} and b["section"] != "L"]
    return {
        "target_platform": spec["target_platform"],
        "domain_model": spec["domain_model"],
        "requirements": spec["requirements"],
        "input_issues": spec["input_issues"],
        "platform_conflicts": [c["term"] for c in spec["platform_conflicts"]],
        "document": {k: doc[k] for k in pick} | {"contracts_and_schemas": data_blocks},
    }


def initial_messages(spec: dict[str, Any]) -> list[dict[str, Any]]:
    spec_json = json.dumps(compact_spec(spec), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    user = ("# Input specification (compact spec.json)\n"
            "Preprocessed deterministically from Architecture_Documentation.md and Architecture_View.md. "
            "The full version is at agent_run/spec.json.\n\n```json\n" + spec_json + "\n```")
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]
