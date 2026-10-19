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
- New harness **UI layout probe** in Verify (`sfagent/agent/ui_probe.py`). It opens the real window, shows every screen
  through the `create_app(root)` → `screens` / `show(name)` contract, and fails verification when widgets are
  outside the window, canvas items are squeezed into an edge or off-canvas, or a screen crashes when shown.
  On run 1's output it reports 11 problems. On a correct layout it passes.
- System prompt UI rules: draw canvases in a `<Configure>` handler from `event.width/height`. The `create_app` /
  `screens` / `show` contract is now explicit. Every screen must render safely when shown directly.
- Rule 5: send all `edit_file` calls for several files in ONE reply.

## Run 2 — 2026-10-18 20:12 UTC (off-peak) → `examples/space_fractions_run2/`

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

## Run 3 — 2026-10-19 10:09 UTC (15:09 PKT, off-peak) → `examples/space_fractions_run3/`

Agent changes since run 2: rule 10 (build user-visible messages from values saved BEFORE changing state, test the
wrong-input path), the UI smoke test must cover a correct and a wrong submission, buttons must never cover text,
and the probe now checks button-over-text overlap and fails on a broken `ui/app.py`.

| Item | Value |
|---|---|
| Result | completed. Verify FAILED once: the UI probe found the "Main Menu" button **outside the window** on the Scores and Help screens, plus an empty startup view. **The agent fixed this itself in 1 fix round.** Then VERIFY PASSED and UI PROBE OK on all 9 screens |
| Requests | 54 (cap 60) |
| Tokens | 1,981,416 prompt (99 % cache hits), 38,384 completion |
| Cost | **$0.131** estimated; balance $1.72 → $1.59 |

How the agent fixed the probe findings, all through its tools: it wrote `diag.py` to measure widget positions, ran
it, then made the Help/Scores text scrollable so the buttons moved inside the window. It made `create_app` show
the intro, re-ran compile and tests, and removed its diagnostic files.

Screenshots: `docs/screenshots/run3/`. They were taken while playing through the real flow with the game's own timers
(Skip → name → round → wrong answer → pause → … → end).

Honest review:
- ✅ **Rule 10 worked.** A wrong answer now shows the SAME question's answer ("Which fraction is equivalent to
  5/10?" → "Not quite — the answer is 1/2"). The code saves `q = current_question` before `submit()`.
- ✅ Help is scrollable and the button sits below the text. The end screen ("Congratulations, Ayesha!", ★★★,
  confetti), the admin form (Type / Prompt / Options / Answer, Save / Delete / New), the name screen, the menu and the
  intro all look good.
- ❌ **Freeze bug:** when a *typed* question is followed by a *multiple-choice* one, `_build_answers` calls `grid()`
  in a frame where the Entry is still `pack`ed. The result is `TclError: cannot use geometry manager grid … managed by
  pack`, and the round stops advancing. This was reproduced in round 1 (order C, C, T → stuck). Neither the generated
  tests nor the probe play a whole round with mixed item kinds, so neither caught it.
- ⚠️ The feedback text sits partly behind the answer buttons. The pause overlay does not cover the answer buttons.
- ⚠️ Sandbox observation: the agent has no delete tool, so it deleted `diag.py` by running a small Python script
  through `run_python`. Scripts run with cwd = the output folder and no API keys, but they are ordinary Python. A
  `delete_file` tool inside the sandbox would remove the need for this.

Total real-API spend for runs 1–3: about **$0.41** of the $2.00 top-up.

## Run 4 — 2026-10-19 11:00 UTC (16:00 PKT, off-peak) → `examples/space_fractions_run4/`

Agent changes since run 3: never mix pack and grid in one container; the UI smoke test must play one complete
flow covering every input variant with real-time pumping and `report_callback_exception`; a sandboxed
`delete_file` tool, with scripts no longer allowed to change project files; the probe pumps every screen for 1.2 s and
fails on Tk callback errors.

| Item | Value |
|---|---|
| Result | completed: VERIFY PASSED + UI PROBE OK on all 9 screens, 0 fix rounds |
| Requests | 57: the first 54 stopped at the **token cap** (2,052,447 cumulative prompt tokens, 98 % of them cheap cache hits); **Resume** with a higher token cap added 3 |
| Cost | **$0.142** estimated; balance $1.59 → $1.45 |
| Notable | The agent wrote and debugged a full-flow UI test itself (`debug_test.py`). The sandbox blocked its attempt to write `/tmp/debug.py` ("Absolute paths are not allowed"). Two `write_files` entries came without `path` (model mistake) and were retried |

Play-test with the game's own timers: **5 complete rounds** with mixed typed and choice questions (e.g.
`CCCCTCCTTC`, `CTCCCCTCCC`). There were **0 Tk callback errors**, and every round reached the end screen. Screenshots:
`docs/screenshots/run4/`.

Honest review:
- ✅ The run-3 freeze is gone: typed and choice inputs use separate frames.
- ✅ A wrong answer shows that same question's answer in simplest form ("Which fraction is equal to 2/3?" →
  "Not quite — the answer is 2/3"). The input clears automatically and the feedback no longer sits behind buttons.
- ✅ Help, pause overlay, end screen ("Congratulations, Ayesha!", 9/10, ★★☆, confetti), high scores and admin all work.
- ⚠️ Visual polish is simpler than runs 2–3: a light grey margin around the dark panel and fewer decorations.
- ⚠️ At 125 % display scaling (window height 793 px) the menu's **Exit** button does not fit and is not shown by
  `pack`. The probe only checks widgets that are shown, so it missed this. In the bottom row of choice buttons the
  label is slightly clipped. The typed input has no Submit button (Enter submits).

## Run 5 — 2026-10-19 11:41 UTC (16:41 PKT, off-peak) → `examples/space_fractions_run5/` (**final example**)

Agent changes since run 4 (user request): the probe checks every screen at 1280×800 **and** at the minimum size
1100×750; it flags button text that is cut off and text inputs without a visible button; there is a rule that every
text input gets a visible Submit/Check button; clearer `write_files` errors; a 6M token cap.

| Item | Value |
|---|---|
| Requests / cost | 47 requests, **$0.122** estimated; balance $1.45 → $1.32 |
| Verify during the run | **FAILED after 3 fix rounds.** Round 1: the probe found that no screen was visible at all (screens were never placed in the window), and the agent fixed it. Round 2: the admin form was too tall, and the agent made the list scrollable. Round 3: the only remaining "problems" were rows of that **scrollable** list, which the probe counted as off-window. That was a **false positive in my probe**, not a bug in the game |
| Probe fix | Widgets inside a scrollable Canvas are no longer treated as off-window, clipped or overlapping (test `test_probe_allows_rows_of_a_scrollable_list`) |
| Re-verification | The same harness checks on the unchanged output, with no API calls: compile OK, **41 tests passed**, **UI PROBE OK at both sizes** → `docs/run5_reverification.txt` |

Play-test with the game's own timers: **5 complete rounds** with heavy typed/choice mixing (e.g. `TCTTCCCTTC`,
`TTTTTCCTTC`). There were **0 Tk callback errors**. Screenshots: `docs/screenshots/run5/` (14, including the menu and
end screen at 1100×750).

Honest review:
- ✅ Everything fits at 1100×750 (the menu shows all five buttons including Exit). Typed questions have a **Check**
  button. The pause overlay covers the whole question. The wrong-answer feedback names the same question's answer.
  The admin screen has a form plus a scrollable list with Delete.
- ❌ **Intro timer bug:** the intro schedules `after(8000, auto_advance)` and Skip does not cancel it. If a player
  skips and starts a round within 8 s of launch, the game jumps back to the menu once. (The play-test hit it because
  the script was fast; screenshots were retaken after waiting 9 s.)
- ⚠️ The choice buttons are left-aligned instead of centred. The intro screen is sparse, with the rocket partly
  hidden at the top.
- ⚠️ **Zero-score check (added later):** playing all 10 questions wrong gives the title "Congratulations, Ayesha!"
  with 0 stars and the message "Every astronaut needs practice. Keep going!" (`docs/screenshots/run5/14_end_zero_score.png`).
  The cause is the old profile text, which asked for a "Congratulations, <name>!" end screen with 1–3 stars in every
  case. The profile now asks for a score-dependent message (0–49 % "Good try! Keep practising", 50–79 % "Well done!",
  80 %+ "Congratulations, <name>!") and 0–3 stars with 0 stars for 0 correct answers. A generic prompt rule now says
  "no praise and no positive rating for a zero or failing result". Run 5's code was left as generated.

## Summary of all real runs

| Run | Requests | Cost | Verify | Main finding → agent improvement |
|---|---|---|---|---|
| 1 | 44 (resume) | $0.103 | passed | canvas drawn at width 1 → **UI probe**, <Configure> rule |
| 2 | 27 | $0.096 | passed first try | feedback showed the next item's answer → **rule 10**; Help overlap → overlap check |
| 3 | 54 | $0.131 | passed after 1 **self-fix** round | pack/grid freeze → pack/grid rule, **full-flow smoke test**, callback-error probe, `delete_file` |
| 4 | 57 (resume) | $0.142 | passed | hidden Exit / clipped text at small sizes → probe at min size, clipped-text and submit-button checks |
| 5 | 47 | $0.122 | probe false positive during the run → **passed on re-verification** | **final example**; scrollable-list false positive fixed in the probe |

Total: about **$0.68** of the $2.00 top-up. The generated code was never edited by hand.
