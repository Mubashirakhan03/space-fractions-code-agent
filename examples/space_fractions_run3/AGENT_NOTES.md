# AGENT_NOTES.md — agent memory

Space Fractions — single-user Tkinter desktop adaptation of a web/cloud spec.

Key decisions:
- Single-user desktop: web infra (Node/Express/Postgres/Redis/RabbitMQ/Elasticsearch/OAuth2/Prometheus/Jenkins/Docker/K8s/Terraform/Vault/Istio/TLS/replicas) removed or mapped to stdlib (SQLite, lru_cache, direct calls, logging, pytest). See DESIGN_DECISIONS.md §1.
- Packages mirror components: game/ (Game, state machine Playing⇄Paused→GameOver, scoring), questions/ (Question, answer checking via fractions.Fraction + repository), users/, admin/, ui/.
- State machine raises on invalid transitions; pausing only between answers.
- Answer acceptance: Fraction(input) == Fraction(answer); 2/4 == 1/2.
- Round = 10 questions; 100 pts/correct; stars by percentage (≥50/≥75/≥90).
- Persistence: sql/schema.sql (games, questions, scores); data/questions.json 20+ seed questions (equivalent, compare, add_subtract, simplify).
- UI: ui/theme.py central palette/fonts; every screen a Frame class with a Canvas starfield drawn on <Configure>; App controller has screens dict + show(name); create_app(root) factory; maximized, F11 fullscreen, Esc exit; min 1100x750; no mainloop() in factory.
- tests/ headless domain + state machine + sequences + persistence (temp SQLite) + test_ui_smoke.py (single Tk, retry 3x, show every screen, correct+wrong submission with cleared input).