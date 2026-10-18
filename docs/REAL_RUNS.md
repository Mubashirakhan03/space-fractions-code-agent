# Real DeepSeek runs (evidence log)

All runs use the official DeepSeek API, model `deepseek-v4-pro`, thinking off, the professor's two input files,
and the optional task profile `profiles/space_fractions.md`. The generated code is **never edited by hand**.
When a run shows a problem, the **agent** is improved (prompts, tools, verification) and run again.

## Run 1 — 2026-10-18 19:54 UTC (off-peak) → `examples/space_fractions_run1/`

| Item | Value |
|---|---|
| Result | completed, harness verification PASSED (compile + 42 tests), 0 fix rounds |
| Requests | 44: the first 40 stopped at the request cap, then **Resume** from `agent_run/state.json` added 4 |
| Tokens | 1,303,264 prompt (98.7 % cache hits), 31,984 completion |
| Cost | **$0.103** (cap $1.00) |
| Output | 35 Python files (~2,000 lines): `game/`, `questions/`, `users/`, `admin/`, `ui/` (9 screens), SQLite schema, 20+ seed questions, 9 test files, README, DESIGN_DECISIONS.md (adaptation table, all 8 input issues, assumptions, UML → code), TRACEABILITY.csv, Dockerfile |

Observed behaviour worth showing:
- Plan mode: `list_dir` → `update_todos` → `submit_plan` in 4 requests; DESIGN_DECISIONS.md written by the harness.
- The agent caught its own bug ("Wait — I referenced a `pause` screen…") and fixed it with `read_file` + `edit_file`.
- After a failing test run it diagnosed the cause (pending `after()` callbacks on destroyed widgets) and fixed the tests.

Problems found by looking at the real window. The tests could not catch them:
1. **Canvas backgrounds are drawn before the window is shown.** The code uses `w = winfo_width() or 1100`, but
   `winfo_width()` returns 1 (not 0) at that moment. All stars collapse into the top-left edge, planets land off-screen,
   and canvas text (intro title, question text) is invisible.
2. **Request efficiency.** Late in the run the model made one `edit_file` per request. That used up the 40-request cap.

Agent improvements made in response (generic, not Space-Fractions specific):
- New harness **UI layout probe** in Verify (`app/agent/ui_probe.py`). It opens the real window, shows every screen
  through the `create_app(root)` → `screens` / `show(name)` contract, and fails verification when widgets are
  outside the window, canvas items are squeezed into an edge or off-canvas, or a screen crashes when shown.
  On run 1's output it reports 11 problems. On a correct layout it passes.
- System prompt UI rules: draw canvases in a `<Configure>` handler from `event.width/height`. The `create_app` /
  `screens` / `show` contract is now explicit. Every screen must render safely when shown directly.
- Rule 5: send all `edit_file` calls for several files in ONE reply.

## Run 2 — pending (needs the user's approval)
