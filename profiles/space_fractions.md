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

Data
- `data/questions.json`: at least 20 seed questions covering all four question types.
- `sql/schema.sql`: adapt the document's `games` table and add `questions` and `scores` tables.

Packages
- `game/` (Game, state machine, scoring), `questions/` (Question, answer checking, repository),
  `users/`, `admin/`, `ui/` — mirroring GameComponent, QuestionComponent, UserComponent, AdminComponent.
