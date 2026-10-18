"""Controller tests (no window) + a GUI smoke test that drives a full mock run in the real window."""

import time
import tkinter as tk

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
    try:
        tk.Tk().destroy()
        return True
    except tk.TclError:
        return False


@pytest.mark.skipif(not _tk_available(), reason="no display")
def test_gui_smoke_mock_generate(tmp_path, doc_path, view_path, monkeypatch):
    from app.gui import app as gui

    monkeypatch.setattr(gui.messagebox, "showerror", lambda *a, **k: pytest.fail(f"error dialog: {a}"))
    window = gui.AgentApp()
    try:
        window.vars["mock"].set(True)
        window.vars["doc_path"].set(str(doc_path))
        window.vars["view_path"].set(str(view_path))
        window.vars["output_dir"].set(str(tmp_path / "gui_out"))
        window._generate()
        assert str(window.stop_btn.cget("state")) == "normal"
        end = time.time() + 90
        while window.controller.running or not window.controller.events.empty():
            window.update()
            assert time.time() < end, "GUI run timed out"
            time.sleep(0.02)
        for _ in range(20):
            window.update()
            time.sleep(0.02)
        log = window.text["Log"].get("1.0", "end")
        assert "write_files main.py" in log and "VERIFY PASSED" in log
        assert "tool" in window.text["Log"].tag_names("3.0") or window.text["Log"].tag_ranges("tool")
        assert "Run completed" in log
        assert "Verification | PASSED" in window.text["Report"].get("1.0", "end")
        assert "●" in window.text["Todos"].get("1.0", "end")
        assert "MOCK MODE" in window.mode_banner.cget("text")
        assert str(window.generate_btn.cget("state")) == "normal"
        assert [window.phase_state(x) for x in gui.PHASES] == ["done", "done", "done", "skipped", "done"]
        assert "deepseek-v4-pro" in window.provider_badge.cget("text") or "Mock" in window.provider_badge.cget("text")
    finally:
        window.destroy()


def test_friendly_key_messages():
    from app.gui.app import friendly_key_problem

    assert "start with sk-" in friendly_key_problem("abc123")
    assert "No API key" in friendly_key_problem("")
    assert friendly_key_problem("sk-abc") is None
