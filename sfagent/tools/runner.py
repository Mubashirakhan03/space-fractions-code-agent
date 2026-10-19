"""Runs generated Python code with the interpreter bundled in this app (no Python needed on target PCs).

Frozen exe:  SpaceFractionsAgent.exe --run-pytest tests      (sys.executable is the exe)
Dev mode:    python -m app.main --run-pytest tests
The child runs with cwd = output dir, a timeout, no API keys in its environment, and writes its
output to a file (a windowed exe has no stdout), which is read back here.
"""

from __future__ import annotations

import contextlib
import os
import subprocess
import sys
import uuid
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent.parent
SKIP_DIRS = {"agent_run", "__pycache__", ".venv", "venv", ".git", ".pytest_cache"}
OUTPUT_ENV = "SFA_OUTPUT_FILE"


def _kill_tree(proc: subprocess.Popen) -> None:
    """Kill the child and anything it started (e.g. a Tk window)."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    else:
        proc.kill()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def base_command() -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable]
    return [sys.executable, "-m", "sfagent.main"]


def clean_env() -> dict[str, str]:
    """Environment for generated code: secrets removed, UTF-8 output, no .pyc clutter."""
    env = {k: v for k, v in os.environ.items()
           if not any(s in k.upper() for s in ("KEY", "TOKEN", "SECRET", "PASSWORD"))}
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if not getattr(sys, "frozen", False):
        env["PYTHONPATH"] = str(APP_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


class PythonRunner:
    def __init__(self, root: Path, run_dir: Path, timeout: int = 120):
        self.root = Path(root).resolve()
        self.run_dir = Path(run_dir)
        self.timeout = timeout

    def python_files(self) -> list[Path]:
        return sorted(p for p in self.root.rglob("*.py") if not SKIP_DIRS & set(p.relative_to(self.root).parts))

    def compile_all(self) -> tuple[bool, str]:
        """Syntax-check every generated .py file in-process (nothing is executed or written)."""
        files = self.python_files()
        errors = []
        for f in files:
            try:
                compile(f.read_text(encoding="utf-8"), str(f), "exec")
            except (SyntaxError, UnicodeDecodeError, ValueError) as exc:
                lineno = getattr(exc, "lineno", "?")
                errors.append(f"{f.relative_to(self.root).as_posix()}:{lineno}: {type(exc).__name__}: {exc}")
        if not files:
            return False, "No Python files found."
        if errors:
            return False, f"{len(errors)} of {len(files)} files have syntax errors:\n" + "\n".join(errors)
        return True, f"All {len(files)} Python files compile."

    def run_pytest(self, target: str = "tests") -> tuple[bool, str]:
        return self._run(["--run-pytest", target], self.timeout)

    def run_script(self, script: str, timeout: int = 60) -> tuple[bool, str]:
        return self._run(["--run-script", script], timeout)

    def _run(self, args: list[str], timeout: int) -> tuple[bool, str]:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        out_file = self.run_dir / f"proc_{uuid.uuid4().hex[:8]}.txt"
        env = clean_env()
        env[OUTPUT_ENV] = str(out_file)
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        proc = subprocess.Popen([*base_command(), *args], cwd=self.root, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
        try:
            code, timed_out = proc.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            _kill_tree(proc)
            code, timed_out = -1, True
        text = out_file.read_text(encoding="utf-8", errors="replace") if out_file.exists() else ""
        with contextlib.suppress(OSError):  # Windows may keep the handle briefly after a kill
            out_file.unlink(missing_ok=True)
        if timed_out:
            text += f"\n[process killed: timed out after {timeout}s]"
        return code == 0, (text.strip() or f"(no output, exit code {code})")
