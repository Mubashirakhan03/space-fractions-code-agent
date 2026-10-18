"""Permission layer for file tools.

- Every path is resolved relative to the output directory; absolute paths, `..` escapes and
  symlinks pointing outside are rejected (path traversal blocked).
- The harness folder `agent_run/` is read-only for the model (transcript/state cannot be forged).
- Executable/script file types are never written (no shell, no .bat/.ps1/.exe).
- ReadState implements Claude Code's "read before edit" + "file changed since read" checks.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

HARNESS_DIR = "agent_run"
BLOCKED_SUFFIXES = {".exe", ".bat", ".cmd", ".ps1", ".sh", ".dll", ".vbs", ".lnk", ".reg"}


class SandboxError(Exception):
    """Raised when a tool tries to touch something outside its permissions."""


class Sandbox:
    def __init__(self, root: Path | str):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, rel: str) -> Path:
        if not isinstance(rel, str) or not rel.strip() or "\x00" in rel:
            raise SandboxError("Path must be a non-empty string.")
        p = Path(rel.strip())
        if p.is_absolute() or p.drive or rel.strip().startswith(("/", "\\")):
            raise SandboxError(f"Absolute paths are not allowed ({rel}); use a path relative to the project root.")
        full = (self.root / p).resolve()  # resolve() follows symlinks, so links out of root are caught too
        if full != self.root and self.root not in full.parents:
            raise SandboxError(f"Path escapes the project directory: {rel}")
        return full

    def rel(self, full: Path) -> str:
        return full.relative_to(self.root).as_posix() or "."

    def check_writable(self, full: Path) -> None:
        rel = self.rel(full)
        if rel == "." or rel.split("/")[0] == HARNESS_DIR:
            raise SandboxError(f"'{rel}' is managed by the agent harness and is read-only.")
        if full.suffix.lower() in BLOCKED_SUFFIXES:
            raise SandboxError(f"Writing '{full.suffix}' files is not permitted.")
        if full.is_dir():
            raise SandboxError(f"'{rel}' is a directory.")


class ReadState:
    """Tracks which files the model has fully read (and their mtime at that moment)."""

    def __init__(self) -> None:
        self._mtimes: dict[Path, int] = {}
        self._lock = threading.Lock()

    def mark(self, full: Path) -> None:
        with self._lock:
            self._mtimes[full] = os.stat(full).st_mtime_ns

    def has_read(self, full: Path) -> bool:
        with self._lock:
            return full in self._mtimes

    def check_editable(self, full: Path, rel: str) -> None:
        with self._lock:
            seen = self._mtimes.get(full)
        if seen is None:
            raise SandboxError(f"You must read_file '{rel}' (whole file) before editing it.")
        if os.stat(full).st_mtime_ns != seen:
            raise SandboxError(f"'{rel}' changed since you last read it; read it again before editing.")
