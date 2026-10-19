"""Harness-side import check (part of Verify).

`compile()` only checks syntax, and tests usually import the UI factory, never `main.py`. A wrong name in an
import (e.g. `from ui.widgets import centered` when widgets.py has no `centered`) then passes verification but
crashes when the user presses "Run generated app". This check imports every project module, and loads `main.py`
WITHOUT running its `if __name__ == "__main__":` block, in a child process of the bundled interpreter. Generic: it
knows nothing about the app.
"""

from __future__ import annotations

import json

from sfagent.tools.runner import PythonRunner

CHECK_REL = "agent_run/import_check.py"

CHECK_SOURCE = r'''
import importlib, json, runpy, sys, traceback
from pathlib import Path
sys.path.insert(0, ".")
SKIP = {"agent_run", "tests", "__pycache__", ".venv", "venv", ".git"}
problems, checked = [], []
for path in sorted(Path(".").rglob("*.py")):
    parts = path.parts
    if SKIP & set(parts) or path.name.startswith(("test_", "conftest")):
        continue
    rel = path.as_posix()
    try:
        if rel == "main.py":
            runpy.run_path(rel, run_name="__import_check__")  # top-level imports only, main() is not called
        else:
            mod = ".".join(parts[:-1] + (() if path.stem == "__init__" else (path.stem,)))
            if mod:
                importlib.import_module(mod)
        checked.append(rel)
    except SystemExit:
        checked.append(rel)
    except BaseException as exc:  # ImportError, AttributeError, NameError, … at import time
        last = traceback.extract_tb(exc.__traceback__)[-1]
        problems.append(f"{rel}: {type(exc).__name__}: {exc} (at {Path(last.filename).name}:{last.lineno})")
print("IMPORT_CHECK_RESULT " + json.dumps({"checked": checked, "problems": problems}), flush=True)
'''


def run_import_check(runner: PythonRunner, timeout: int = 60) -> tuple[bool, str]:
    target = runner.root / CHECK_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(CHECK_SOURCE, encoding="utf-8")
    ok, out = runner.run_script(CHECK_REL, timeout=timeout)
    line = next((ln for ln in reversed(out.splitlines()) if ln.startswith("IMPORT_CHECK_RESULT ")), None)
    if line is None:
        return False, ("IMPORT CHECK FAILED to run — importing the project's modules (or loading main.py without "
                       "running main()) did not finish. Module top-level code must not open windows or block:\n"
                       + out[-2000:])
    data = json.loads(line[len("IMPORT_CHECK_RESULT "):])
    if data["problems"]:
        return False, (f"IMPORT CHECK FAILED ({len(data['problems'])}): these modules cannot be imported, so the app "
                       "would crash on start:\n- " + "\n- ".join(data["problems"][:20]))
    return True, f"IMPORT CHECK OK: {len(data['checked'])} modules incl. main.py"
