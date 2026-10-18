"""Entry point: GUI by default, or hidden sub-commands used by the agent's runner.

    SpaceFractionsAgent.exe                         → GUI
    SpaceFractionsAgent.exe --run-pytest [args…]    → run pytest with the bundled interpreter (cwd = project)
    SpaceFractionsAgent.exe --run-script <file>     → run a Python script with the bundled interpreter
    SpaceFractionsAgent.exe --doctor                → offline health check (no API call)
    SpaceFractionsAgent.exe --self-test [dir]       → full scripted mock pipeline (no API call)
    SpaceFractionsAgent.exe --version
"""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

from app import __version__
from app.tools.runner import OUTPUT_ENV


def _redirect_output() -> None:
    """A windowed exe has no stdout; write output to the file the parent process asked for."""
    target = os.environ.get(OUTPUT_ENV)
    if target:
        stream = open(target, "w", encoding="utf-8", buffering=1)  # noqa: SIM115 - lives for the process
        sys.stdout = sys.stderr = stream
    elif sys.stdout is None:
        sys.stdout = sys.stderr = open(os.devnull, "w")  # noqa: SIM115


def run_pytest(args: list[str]) -> int:
    import pytest

    sys.path.insert(0, os.getcwd())
    return int(pytest.main(["-q", "-p", "no:cacheprovider", *(args or ["tests"])]))


def run_script(script: str, rest: list[str]) -> int:
    path = Path(script).resolve()
    sys.path.insert(0, str(path.parent))
    sys.argv = [str(path), *rest]
    runpy.run_path(str(path), run_name="__main__")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args[:1] == ["--run-pytest"]:
        _redirect_output()
        return run_pytest(args[1:])
    if args[:1] == ["--run-script"]:
        _redirect_output()
        if len(args) < 2:
            print("usage: --run-script <file.py> [args]")
            return 2
        return run_script(args[1], args[2:])
    if args[:1] == ["--doctor"]:
        _redirect_output()
        from app.selftest import doctor

        return doctor()
    if args[:1] == ["--self-test"]:
        _redirect_output()
        from app.selftest import self_test

        return self_test(args[1] if len(args) > 1 else None)
    if args[:1] == ["--version"]:
        _redirect_output()
        print(__version__)
        return 0
    from app.gui.app import launch

    return launch()


if __name__ == "__main__":
    raise SystemExit(main())
