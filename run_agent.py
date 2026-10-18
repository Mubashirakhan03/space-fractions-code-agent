"""PyInstaller entry point (and `python run_agent.py` in dev)."""

from app.main import main

if __name__ == "__main__":
    raise SystemExit(main())
