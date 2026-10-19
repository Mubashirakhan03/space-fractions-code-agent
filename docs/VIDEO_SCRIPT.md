# Video script (4–6 minutes) — Space Fractions Code Agent

Recording tips: 1920×1080 at 100 % scaling if possible (the app opens at 1400×850). Use a light desktop and close
other windows. Rehearse once in **mock mode** (free). Do the live part with a real run, or with **Replay** of the
recorded run if the internet or API is not available, and say so on screen.

| Time | Show on screen | Say (English — speak slowly, plain words) |
|---|---|---|
| 0:00–0:25 | Title slide or README top; GitHub repo | "Hi, I'm Mubashira. This is my Task 1: a simplified Claude-Code-style code agent. It reads an architecture document and UML views, and uses DeepSeek v4-pro to generate a complete desktop game, Space Fractions." |
| 0:25–1:10 | `docs/ARCHITECTURE.md` flow diagram | "First, a deterministic parser turns the two Markdown files into spec.json, with no AI involved. It also finds problems in the input: the document describes a web microservice system, the testing table is empty, a file name does not match, and the UML has syntax errors. The agent then runs in phases: plan, implement, verify, fix and report." |
| 1:10–1:50 | Mechanism table in README | "These are the Claude Code mechanisms I implemented. A two-layer agent loop. A tool registry where read-only tools run in parallel. Plan mode, where write tools are denied. Search-and-replace editing with read-before-edit. A sandbox. Context compaction. Prompt caching: 98 % of the prompt tokens were cache hits. Resume and replay. And a mock provider, so all 144 tests run without API cost." |
| 1:50–2:30 | Double-click `SpaceFractionsAgent.exe` (explain: no Python needed). Show the GUI header, the API key field, the inputs, the task profile and the limits | "This is the Windows exe. It needs no Python installation, because generated code runs on the interpreter bundled inside the exe. Here I enter the DeepSeek key, choose the two input files and an empty output folder, and set hard limits: one dollar and sixty requests." |
| 2:30–3:30 | Press **Generate** (live or Replay). Point at the phase bar, the log lines (`→ write_files …`), Todos, and the status bar with cost | "The plan phase is read-only. The model writes a UI design brief and the design decisions, which adapt Node, PostgreSQL, Redis and Kubernetes to one desktop process with SQLite. Then it writes files in batches. Then the harness verifies everything: compile, pytest, and a UI probe that opens the real window. If something fails, the agent gets the report and fixes it itself." (Show run 3's fix round in the log or in `docs/REAL_RUNS.md`.) |
| 3:30–4:30 | Success dialog → **Run generated app**: intro → menu → name → question (one right, one wrong answer) → pause → end screen with stars | "The generated game: an animated space intro, the menu, a name entry, fraction questions with immediate feedback, pause and resume from the state diagram, and an ending scene with stars. The whole game was written by the agent. I did not edit it." |
| 4:30–5:10 | Generated folder: DESIGN_DECISIONS.md, TRACEABILITY.csv, tests; `agent_run/RUN_REPORT.md` | "It also wrote the README, the design decisions with every input issue, a traceability matrix and tests. The run report records the model, the requests, the tokens and the cost: about ten to fifteen cents per run." |
| 5:10–5:40 | `docs/REAL_RUNS.md` | "I was honest about the results. After each real run I looked at the real window. When I found a bug, I improved the agent instead of the code, for example with the UI probe and new rules, and I ran it again. The remaining known limitations are listed in the README." |
| 5:40–6:00 | README links (repo, release) | "The code, the exe release and all the evidence are on GitHub. Thank you!" |

## Backup plan
- If there is no internet, use **Replay**: choose `examples/space_fractions_run5/agent_run/transcript.jsonl` and an
  empty folder. The banner says "REPLAY of recorded run". Say this out loud.
- Keep the generated game folder ready, so you can press **Run generated app** directly.
