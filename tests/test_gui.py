"""Controller tests (no window) + a GUI smoke test that drives a full mock run in the real window."""

import contextlib
import json
import time
import tkinter as tk
from pathlib import Path

import pytest

from app.config import AppConfig
from app.gui.controller import RunController, find_default_inputs, launch_generated_game
from app.llm.demo_script import BANNER


@pytest.fixture(autouse=True)
def _isolated_appdata(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))


def wait_done(ctrl: RunController, timeout: float = 90) -> list:
    events, end = [], time.time() + timeout
    while time.time() < end:
        for kind, data in ctrl.drain():
            events.append((kind, data))
            if kind == "approve":
                data["request"].approved = True
                data["request"].answered.set()
            if kind == "done":
                return events
        time.sleep(0.02)
    raise TimeoutError("run did not finish")


def mock_cfg(tmp_path, doc_path, view_path, **kw) -> AppConfig:
    return AppConfig(provider="mock", doc_path=str(doc_path), view_path=str(view_path),
                     output_dir=str(tmp_path / "out"), **kw)


def test_controller_mock_run_in_worker_thread(tmp_path, doc_path, view_path):
    ctrl = RunController()
    ctrl.start(mock_cfg(tmp_path, doc_path, view_path))
    events = wait_done(ctrl)
    result = dict(events)["done"]["result"]
    assert result["status"] == "completed" and result["verify_ok"] is True
    assert BANNER in (tmp_path / "out" / "README.md").read_text(encoding="utf-8")
    assert {"phase", "tool_call", "todos", "usage", "verify"} <= {k for k, _ in events}


def test_controller_ask_before_write_bridge(tmp_path, doc_path, view_path):
    ctrl = RunController()
    ctrl.start(mock_cfg(tmp_path, doc_path, view_path, ask_before_write=True))
    events = wait_done(ctrl)
    asked = [d["request"].path for k, d in events if k == "approve"]
    assert "main.py" in asked and dict(events)["done"]["result"]["verify_ok"]


def test_controller_reports_config_errors(tmp_path):
    ctrl = RunController()
    ctrl.start(AppConfig(provider="mock", output_dir=str(tmp_path / "o")))
    events = wait_done(ctrl)
    assert any(k == "error" and "input files" in d["text"] for k, d in events)


def test_controller_missing_key_is_friendly(tmp_path, doc_path, view_path):
    ctrl = RunController()
    ctrl.start(AppConfig(provider="deepseek", doc_path=str(doc_path), view_path=str(view_path),
                         output_dir=str(tmp_path / "o")))
    events = wait_done(ctrl)
    assert any(k == "error" and "API key" in d["text"] for k, d in events)


def test_find_default_inputs(tmp_path, doc_path, view_path):
    assert find_default_inputs([tmp_path]) != ("", "")  # falls back to the repo's samples/
    (tmp_path / doc_path.name).write_text("x")
    (tmp_path / view_path.name).write_text("y")
    assert find_default_inputs([tmp_path])[0] == str(tmp_path / doc_path.name)


def test_launch_game_requires_main(tmp_path):
    with pytest.raises(FileNotFoundError):
        launch_generated_game(tmp_path)


def _tk_available() -> bool:
    for _ in range(3):  # Tk init can fail transiently on Windows
        try:
            tk.Tk().destroy()
            return True
        except tk.TclError:
            time.sleep(0.3)
    return False


def close_window(w) -> None:
    """Cancel pending after() callbacks (customtkinter schedules many) before destroying, so the next
    test's Tk() starts from a clean interpreter state."""
    w._pulsing = False
    with contextlib.suppress(tk.TclError):
        for after_id in w.tk.call("after", "info"):
            w.after_cancel(after_id)
    with contextlib.suppress(tk.TclError):
        w.destroy()


def run_window(window, timeout=90):
    end = time.time() + timeout
    while window.controller.running or not window.controller.events.empty():
        window.update()
        assert time.time() < end, "GUI run timed out"
        time.sleep(0.02)
    for _ in range(20):
        window.update()
        time.sleep(0.02)


@pytest.fixture
def window(monkeypatch, doc_path, view_path):
    if not _tk_available():
        pytest.skip("no display")
    from app.gui import app as gui

    monkeypatch.setattr(gui.messagebox, "showerror", lambda *a, **k: pytest.fail(f"error dialog: {a}"))
    w = gui.create_window()
    w.results = []
    w._result_dialog = lambda ok, title, msg: w.results.append((ok, title, msg))
    w.vars["mock"].set(True)
    w.vars["doc_path"].set(str(doc_path))
    w.vars["view_path"].set(str(view_path))
    yield w
    close_window(w)


def test_gui_smoke_mock_generate(tmp_path, window):
    from app.gui import app as gui

    window.vars["output_dir"].set(str(tmp_path / "gui_out"))
    assert str(window.run_game_btn.cget("state")) == "disabled"  # nothing generated yet
    window._generate()
    assert str(window.stop_btn.cget("state")) == "normal"
    run_window(window)
    log = window.text["Log"].get("1.0", "end")
    assert "write_files main.py" in log and "VERIFY PASSED" in log
    assert window.text["Log"].tag_ranges("tool")
    assert "Run completed" in log
    assert "Verification | PASSED" in window.text["Report"].get("1.0", "end")
    assert "●" in window.text["Todos"].get("1.0", "end")
    assert str(window.generate_btn.cget("state")) == "normal"
    assert [window.phase_state(x) for x in gui.PHASES] == ["done", "done", "done", "skipped", "done"]
    assert "Mock" in window.provider_badge.cget("text")
    # clear success feedback + run button enabled and pulsing
    assert window.results and window.results[-1][0] is True and "Tests: PASSED" in window.results[-1][2]
    assert "successfully" in window.mode_banner.cget("text")
    assert str(window.run_game_btn.cget("state")) == "normal" and window._pulsing
    # switching to an empty folder disables it again
    window.vars["output_dir"].set(str(tmp_path / "other"))
    window.update()
    assert str(window.run_game_btn.cget("state")) == "disabled" and not window._pulsing


def test_gui_failed_run_shows_red_reason(tmp_path, window):
    window.vars["output_dir"].set(str(tmp_path / "fail_out"))
    window.vars["max_requests"].set("1")
    window._generate()
    run_window(window)
    ok, title, msg = window.results[-1]
    assert ok is False and "max LLM requests" in msg
    assert window.mode_banner.cget("text").startswith("✗")
    assert str(window.run_game_btn.cget("state")) == "disabled"


def test_gui_non_empty_folder_choices(tmp_path, window):
    out = tmp_path / "busy"
    out.mkdir()
    (out / "notes.txt").write_text("mine")
    window.vars["output_dir"].set(str(out))
    window._folder_dialog = lambda folder: None  # Cancel
    window._generate()
    assert not window.controller.running
    window._folder_dialog = lambda folder: "new"
    window._generate()
    assert Path(window.vars["output_dir"].get()).parent == out
    assert Path(window.vars["output_dir"].get()).name.startswith("run-")
    run_window(window)
    assert window.results[-1][0] is True and (out / "notes.txt").exists()


def test_show_hide_key_button(window):
    assert "Show" in window.show_key_btn.cget("text") and window.key_entry.cget("show") == "•"
    window._toggle_key()
    assert "Hide" in window.show_key_btn.cget("text") and window.key_entry.cget("show") == ""
    window._toggle_key()
    assert "Show" in window.show_key_btn.cget("text")


def test_folder_helpers(tmp_path):
    from datetime import datetime

    from app.gui.controller import clear_previous_run, new_run_subfolder, run_succeeded

    now = datetime(2026, 10, 19, 0, 19)
    first = new_run_subfolder(tmp_path, now)
    assert first.name == "run-2026-10-19_0019"
    first.mkdir()
    assert new_run_subfolder(tmp_path, now).name == "run-2026-10-19_0019-2"

    with pytest.raises(ValueError):
        clear_previous_run(tmp_path)  # no recorded run → nothing deleted
    (tmp_path / "agent_run").mkdir()
    (tmp_path / "agent_run" / "state.json").write_text(json.dumps(
        {"status": "completed", "verify_ok": True, "written": ["main.py", "pkg/a.py", "../outside.txt"]}))
    (tmp_path / "main.py").write_text("x")
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.py").write_text("x")
    (tmp_path / "mine.txt").write_text("keep")
    (tmp_path.parent / "outside.txt").write_text("keep")
    assert run_succeeded(tmp_path)
    removed = clear_previous_run(tmp_path)
    assert "main.py" in removed and "agent_run/" in removed
    assert (tmp_path / "mine.txt").exists() and (tmp_path.parent / "outside.txt").exists()
    assert not (tmp_path / "pkg").exists()  # emptied package folder tidied up
    assert not run_succeeded(tmp_path)


def test_friendly_key_messages():
    from app.gui.app import friendly_key_problem

    assert "start with sk-" in friendly_key_problem("abc123")
    assert "No API key" in friendly_key_problem("")
    assert friendly_key_problem("sk-abc") is None


def test_new_run_folders_are_siblings_not_nested(tmp_path):
    from datetime import datetime

    from app.gui.controller import new_run_subfolder, run_folder_base

    now = datetime(2026, 10, 19, 17, 25)
    workspace = tmp_path / "tictactoe"
    workspace.mkdir()
    (workspace / "notes.txt").write_text("user file")
    first = new_run_subfolder(workspace, now)
    assert first.parent == workspace                     # plain folder → subfolder inside it
    first.mkdir()
    (first / "agent_run").mkdir()
    second = new_run_subfolder(first, now)               # chosen folder IS a run folder → sibling
    assert second.parent == workspace and second.name == "run-2026-10-19_1725-2"
    assert run_folder_base(workspace / "run-2026-10-19_0050") == workspace  # run-… name alone is enough


def test_resume_marks_completed_phases_done(window):
    window._reset_phases()
    window._on_resume("verify", 0)
    assert [window.phase_state(p) for p in ("plan", "implement", "verify", "fix")] == ["done", "done", "pending",
                                                                                      "pending"]
    window._reset_phases()
    window._on_resume("report", 1)
    assert window.phase_state("fix") == "done" and window.phase_state("verify") == "done"
