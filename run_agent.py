"""PyInstaller entry point (and `python run_agent.py` in dev)."""

from sfagent.main import main

if __name__ == "__main__":
    raise SystemExit(main())
