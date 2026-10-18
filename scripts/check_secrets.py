"""Block commits that contain API keys or secret files.

Used as a git pre-commit hook (installed by `scripts/install_hooks.py`) and runnable by hand:
    python scripts/check_secrets.py          # scans staged changes
Exit code 1 = secret found (commit blocked). Matches are reported masked, never printed in full.
"""

from __future__ import annotations

import re
import subprocess
import sys

PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),  # DeepSeek / OpenAI-style keys
    re.compile(r"gh[opsu]_[A-Za-z0-9]{20,}"),  # GitHub tokens
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{24,}"),
]
FORBIDDEN_FILES = re.compile(r"(^|/)(\.env|config\.json|api-keys-backup\.txt)$")


def staged_files() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                         capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if f]


def staged_added_lines() -> list[tuple[str, str]]:
    out = subprocess.run(["git", "diff", "--cached", "-U0", "--no-color"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout
    current, lines = "", []
    for ln in out.splitlines():
        if ln.startswith("+++ b/"):
            current = ln[6:]
        elif ln.startswith("+") and not ln.startswith("+++"):
            lines.append((current, ln[1:]))
    return lines


def main() -> int:
    problems = [f"forbidden file staged: {f}" for f in staged_files() if FORBIDDEN_FILES.search(f)]
    for path, line in staged_added_lines():
        for pat in PATTERNS:
            m = pat.search(line)
            if m:
                problems.append(f"{path}: possible secret {m.group(0)[:6]}…(masked)")
    if problems:
        print("COMMIT BLOCKED — secrets detected:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
