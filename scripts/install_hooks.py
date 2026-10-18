"""Install the secret-scanning git pre-commit hook: python scripts/install_hooks.py"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / ".git" / "hooks" / "pre-commit"
SCRIPT = """#!/bin/sh
# Installed by scripts/install_hooks.py — blocks commits containing API keys.
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=python
exec "$PY" scripts/check_secrets.py
"""

if __name__ == "__main__":
    HOOK.write_text(SCRIPT, encoding="utf-8", newline="\n")
    HOOK.chmod(0o755)
    print(f"installed {HOOK}")
