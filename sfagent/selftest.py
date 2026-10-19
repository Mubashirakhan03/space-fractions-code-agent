"""`--doctor` and `--self-test`: offline health checks of the (frozen) app. No network, no API cost.

--doctor     imports every bundled module, checks tkinter/sqlite/pytest/openai client and config dir.
--self-test  runs the full scripted mock pipeline (agent → tools → child process → pytest) in a folder.
Both print a report and return exit code 0 on success (mirrors claw-code's `doctor`).
"""

from __future__ import annotations

import importlib
import sys
import tempfile
from pathlib import Path

from sfagent import __version__
from sfagent.bundled import BUNDLED_STDLIB, TEST_PACKAGES
from sfagent.config import AppConfig, config_dir


def doctor() -> int:
    checks: list[tuple[str, bool, str]] = []
    missing = []
    for mod in [*BUNDLED_STDLIB, *TEST_PACKAGES]:
        try:
            importlib.import_module(mod)
        except Exception as exc:  # noqa: BLE001 - report every failure
            missing.append(f"{mod} ({type(exc).__name__})")
    checks.append(("bundled modules", not missing, ", ".join(missing) or f"{len(BUNDLED_STDLIB) + 1} importable"))
    try:
        import tkinter

        checks.append(("tkinter", True, f"Tk {tkinter.TkVersion}"))
    except Exception as exc:  # noqa: BLE001
        checks.append(("tkinter", False, str(exc)))
    import sqlite3

    con = sqlite3.connect(":memory:")
    checks.append(("sqlite3", con.execute("select 1").fetchone() == (1,), sqlite3.sqlite_version))
    con.close()
    try:
        from openai import OpenAI

        OpenAI(api_key="doctor-check", base_url="https://api.deepseek.com", max_retries=0)
        checks.append(("openai client", True, "constructed (no request sent)"))
    except Exception as exc:  # noqa: BLE001
        checks.append(("openai client", False, str(exc)))
    try:
        d = config_dir()
        d.mkdir(parents=True, exist_ok=True)
        checks.append(("config dir", True, str(d)))
    except OSError as exc:
        checks.append(("config dir", False, str(exc)))
    checks.append(("API key", True, "set" if AppConfig().resolved_api_key() else "not set (enter it in the GUI)"))

    print(f"Space Fractions Code Agent {__version__} - doctor (frozen={getattr(sys, 'frozen', False)})")
    for name, ok, detail in checks:
        print(f"  [{'OK' if ok else 'FAIL'}] {name}: {detail}")
    ok_all = all(ok for _, ok, _ in checks)
    print("RESULT:", "OK" if ok_all else "PROBLEMS FOUND")
    return 0 if ok_all else 1


def self_test(out_dir: str | None = None) -> int:
    from sfagent.agent.loop import Agent
    from sfagent.gui.controller import find_default_inputs
    from sfagent.llm.demo_script import demo_provider
    from sfagent.parsers.spec import build_spec

    out = Path(out_dir) if out_dir else Path(tempfile.mkdtemp(prefix="sfa_selftest_"))
    doc, view = find_default_inputs()
    if not doc:
        print("FAIL: sample input files not found")
        return 1
    spec = build_spec(Path(doc), Path(view))
    print(f"spec.json built: {len(spec['input_issues'])} input issues, "
          f"{len(spec['views']['diagrams'])} diagrams")
    result = Agent(demo_provider(), AppConfig(provider="mock"), out, spec,
                   on_event=lambda k, d: print(f"  {k}: {d.get('text') or d.get('phase') or d.get('summary') or ''}")
                   if k in ("phase", "tool_call", "log") else None).run()
    print(f"status={result.status} verify_ok={result.verify_ok} requests={result.requests} output={out}")
    return 0 if result.status == "completed" and result.verify_ok else 1
