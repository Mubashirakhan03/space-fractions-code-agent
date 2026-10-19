# AGENT_NOTES.md — agent memory

## AGENT_NOTES.md (key decisions)
- Space Fractions: educational fractions game, Tkinter desktop, single local user.
- Packages mirror components: game/ (Game + state machine), questions/ (Question + checker + repository), users/ (User), admin/ (Admin), ui/ (screens + app controller).
- Domain logic is pure Python (no Tkinter) and headless-testable.
- Correctness via fractions.Fraction so equivalent fractions are accepted.
- State machine: Playing ⇄ Paused → GameOver; invalid transitions raise StateError.
- Round = 10 questions; +1 per correct; stars 3/2/1/0 by >=90/70/50/<50%.
- Persistence: SQLite (data/spacefractions.db), schema in sql/schema.sql (games, questions, scores). Seed from data/questions.json (20+ questions, 4 types).
- UI theme in ui/theme.py; animated space background via ui/space_canvas.py drawn on <Configure>.
- ui/app.py defines create_app(root) -> App with screens dict + show(name); no mainloop in factory.
- Every screen renders safely when shown directly (defaults for empty data).
- Input cleared automatically after each answer; ~1s delay before next question (no popups).