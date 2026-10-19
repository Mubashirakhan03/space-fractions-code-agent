---
name: Space Fractions
required_files:
  - sql/schema.sql
  - data/questions.json
---
Optional hints for the Space Fractions architecture documents (an educational fractions game for
6th-grade students). These complement spec.json; they do not replace it.

Screens / flow
- Animated INTRO scene (the "introductory movie"): space-themed tkinter.Canvas animation (stars, ship),
  a Skip button, auto-advances to the menu.
- MAIN MENU: Play, High Scores, Help, Admin, Exit.
- PLAYER NAME entry before playing (UserComponent).
- QUESTION FLOW: a round of fraction questions of mixed types — equivalent fractions, compare,
  add/subtract, simplify; multiple choice and typed answers; immediate feedback; progress and score.
  Check correctness with fractions.Fraction so equivalent forms are accepted (2/4 == 1/2).
- PAUSE / RESUME following the state diagram Playing ⇄ Paused → GameOver (invalid transitions raise).
- ENDING scene with final score, percentage and encouraging feedback; option to play again.
- HIGH SCORES (View Score) from SQLite; HELP screen (View Help); ADMIN screen to add / edit / delete
  questions (Update Questions).

Kid-friendly look and feel (players are 11–12 years old; this matters as much as correctness)
- Opens maximized (minimum 1100x750), F11 full screen, Esc leaves full screen.
- Space theme on a tkinter.Canvas background: dark blue (#0B1736-ish), twinkling stars, two or three
  colourful planets drawn with ovals/arcs. Bright accent colours (yellow, cyan, pink, green) on dark panels.
- Fonts: titles 36+ pt bold, questions 30 pt, answer input and buttons 20+ pt. Big flat buttons with a
  hover colour; multiple-choice answers as 2x2 big coloured buttons.
- Question screen: "Question 3 of 10" progress text plus a progress bar, the score always visible, the answer
  input focused, Enter submits, and a visible Pause button (state machine Paused shows an overlay with Resume).
- After every answer: big coloured feedback in the window — green "Correct! 🎉" or red
  "Not quite — the answer is 3/4" — the input is CLEARED automatically and the next question appears after
  about a second (no manual clearing, no popup).
- End screen: the score and percentage, a message that MATCHES the score — 0–49 %: "Good try! Keep practising",
  50–79 %: "Well done!", 80 %+: "Congratulations, <name>!" — and 0–3 stars by percentage (0 correct answers → 0 stars;
  never praise or stars for a zero score). Confetti/star animation only for a high score. Buttons "Play again" /
  "Main menu". Test the zero-score and the full-score end screens.
- Intro: animated rocket flying across moving stars with the game title, a Skip button, auto-advance.
- tests/test_ui_smoke.py must build every screen (intro, menu, name entry, question, pause overlay, end,
  high scores, help, admin) and check the answer input is cleared after a submission.

Data
- `data/questions.json`: at least 20 seed questions covering all four question types (equivalent, compare,
  add/subtract, simplify), with both typed and multiple-choice items; loaded into SQLite on first start.
- Random questions: besides the seed set, the game generates NEW fraction questions in code (no API) for
  every round — equivalent fractions, compare two fractions, add/subtract with unlike denominators, simplify —
  with random numerators/denominators, the correct answer computed with `fractions.Fraction`, and plausible
  wrong options for multiple choice (distinct, never equal to the answer). A round mixes seed and generated
  questions so every round is different. Test the generator: each type, valid answers, no duplicate options.
- Admin add/edit form: prompt, type, correct answer and options (for multiple choice); validate that the answer
  is a valid fraction and that the options contain it.
- `sql/schema.sql`: adapt the document's `games` table and add `questions` and `scores` tables.

Packages
- `game/` (Game, state machine, scoring), `questions/` (Question, answer checking, repository),
  `users/`, `admin/`, `ui/` — mirroring GameComponent, QuestionComponent, UserComponent, AdminComponent.
