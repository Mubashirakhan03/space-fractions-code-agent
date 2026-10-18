"""Optional task profiles: task-specific hints kept OUT of the agent's code.

A profile is a Markdown file the user selects in the GUI (e.g. profiles/space_fractions.md) with an
optional YAML front matter:

    ---
    name: Space Fractions
    required_files: [sql/schema.sql, data/questions.json]
    ---
    ...free-form hints for the model...

The hints are appended to the spec message (so the cached prompt prefix stays stable for the whole
run) and `required_files` are added to the harness's deliverable check. Without a profile the agent
derives everything from spec.json alone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class TaskProfile:
    name: str
    hints: str
    required_files: list[str] = field(default_factory=list)
    source: str = ""


def parse_profile(text: str, source: str = "") -> TaskProfile:
    meta: dict = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2]
    if not isinstance(meta, dict):
        raise ValueError("Profile front matter must be a YAML mapping.")
    files = meta.get("required_files") or []
    if not isinstance(files, list) or not all(isinstance(f, str) for f in files):
        raise ValueError("required_files must be a list of relative paths.")
    name = str(meta.get("name") or Path(source).stem or "custom profile")
    return TaskProfile(name=name, hints=body.strip(), required_files=files, source=source)


def load_profile(path: str | Path | None) -> TaskProfile | None:
    if not path:
        return None
    p = Path(path)
    return parse_profile(p.read_text(encoding="utf-8"), source=p.name)
