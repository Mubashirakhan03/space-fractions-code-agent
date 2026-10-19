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

## Run 2 — 2026-10-18 20:12 UTC (off-peak) → `examples/space_fractions_generated/` (final)

Same inputs, profile and limits ($1.00 / 60 requests), with the improved agent (UI design brief, UI layout probe,
<Configure> drawing rule, batch-edit rule).

| Item | Value |
|---|---|
| Result | completed **on the first attempt**: VERIFY PASSED (compile + tests) and **UI PROBE OK on all 9 screens** (intro, menu, name, question, end, high_scores, help, admin + startup), 0 fix rounds, no resume needed |
| Requests | **27** (run 1: 44) |
| Tokens | 902,320 prompt (98 % cache hits), 32,561 completion |
| Cost | **$0.096** estimated by the agent; account balance went from $1.89 to $1.72 |
| Recovered errors | one malformed tool-call JSON ("Invalid JSON arguments… re-send") and one missing `path` argument. Both came back to the model as `is_error` results and were corrected |
| UI design brief | DESIGN_DECISIONS.md §5: users (11–12-year-olds + admin), mood, 11-colour hex palette with roles, font sizes, layout (<Configure> redraw), 9 screens |

Screenshots of every screen: `docs/screenshots/run2/` (intro, menu, name, high scores, help, admin, question,
feedback, pause, end). Taken from a copy of the folder with Win32 PrintWindow, the way `main.py` opens it (maximized).

Honest review of the result:
- ✅ Animated space intro with title and Skip; menu with icons; name entry; 2×2 multiple-choice question screen
  with progress bar, score and Pause; pause overlay; end screen with "Congratulations, <name>!", 3 stars and
  confetti; SQLite high scores; admin list with Edit / ✕ / Add Question.
- ✅ Input is cleared automatically after an answer; coloured feedback; the next question follows after a delay.
- ⚠️ **Logic bug:** after a wrong answer the feedback shows the **next** question's answer ("Not quite — the
  answer is 2/3" for a question whose answer is 1/2), because the game advances before the message is built.
  The generated tests did not cover this. It is left as generated (no hand edits) and recorded here.
- ⚠️ Help screen: at 125 % display scaling the "← Menu" button overlaps the last line of help text.
- ℹ️ Maximizing is done in `main.py`, not in `create_app()`. Opening via `create_app` alone gives a normal window.

Total real-API spend for runs 1 + 2: about **$0.28** of the $2.00 top-up.
