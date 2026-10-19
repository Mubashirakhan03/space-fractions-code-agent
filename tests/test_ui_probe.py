"""The harness UI probe catches broken layouts that unit tests miss (real window, generic checks)."""

import tkinter as tk

import pytest

from app.agent.ui_probe import run_ui_probe
from app.tools.runner import PythonRunner


def _tk_ok() -> bool:
    try:
        tk.Tk().destroy()
        return True
    except tk.TclError:
        return False


pytestmark = pytest.mark.skipif(not _tk_ok(), reason="no display")

BAD = '''import tkinter as tk


class App:
    def __init__(self, root):
        self.root = root
        self.screens = {}
        canvas = tk.Canvas(root, bg="navy")
        canvas.pack(fill="both", expand=True)
        w = canvas.winfo_width() or 1100   # BUG: winfo_width() is 1 here
        for i in range(40):
            canvas.create_oval(i * w // 40, 5, i * w // 40 + 2, 7, fill="white")
        self.screens["menu"] = canvas

    def show(self, name):
        pass


def create_app(root):
    return App(root)
'''

GOOD = '''import tkinter as tk


class App:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, bg="navy", highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)
        self.canvas.bind("<Configure>", self.draw)
        self.title = tk.Label(root, text="Hello", font=("Segoe UI", 32))
        self.title.place(relx=0.5, rely=0.3, anchor="center")
        self.screens = {"menu": self.title, "end": self.title}

    def draw(self, event):
        self.canvas.delete("all")
        for i in range(40):
            x = i * event.width // 40
            self.canvas.create_oval(x, 20, x + 3, 23, fill="white")

    def show(self, name):
        if name == "end" and getattr(self, "broken", False):
            raise RuntimeError("no game in progress")
        self.title.config(text=name)


def create_app(root):
    return App(root)
'''


def make(tmp_path, source: str | None):
    if source is not None:
        (tmp_path / "ui").mkdir()
        (tmp_path / "ui" / "__init__.py").write_text("")
        (tmp_path / "ui" / "app.py").write_text(source)
    return PythonRunner(tmp_path, tmp_path / "agent_run", timeout=60)


def test_probe_flags_canvas_drawn_before_window_is_shown(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, BAD))
    assert not ok
    assert "top-left edge" in report and "<Configure>" in report
    assert "no labels, buttons or inputs are visible" in report


def test_probe_passes_a_correct_layout(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, GOOD))
    assert ok, report
    assert "screen 'menu'" in report and "screen 'end'" in report


def test_probe_reports_screens_that_crash(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, GOOD.replace("self.screens = {", "self.broken = True\n        "
                                                                            "self.screens = {")))
    assert not ok and "screen 'end': app.show() raised RuntimeError" in report


def test_probe_skips_projects_without_ui_contract(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, None))
    assert ok and "SKIPPED" in report


OVERLAP = '''import tkinter as tk


class App:
    def __init__(self, root):
        frame = tk.Frame(root, bg="white")
        frame.place(relwidth=1, relheight=1)
        tk.Label(frame, text="help text " * 60, wraplength=700, font=("Segoe UI", 20)).place(
            relx=0.5, rely=0.5, anchor="center")
        tk.Button(frame, text="Back", font=("Segoe UI", 18)).place(relx=0.5, rely=0.55, anchor="center")
        self.screens = {"help": frame}

    def show(self, name):
        self.screens[name].tkraise()


def create_app(root):
    return App(root)
'''


def test_probe_flags_button_covering_text(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, OVERLAP))
    assert not ok and "button 'Back' covers the text" in report


def test_probe_fails_when_ui_module_is_broken(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, "def create_app(root:\n"))
    assert not ok and "failed: SyntaxError" in report


TIMER_CRASH = GOOD.replace('''        self.screens = {"menu": self.title, "end": self.title}''',
                           '''        self.screens = {"menu": self.title, "end": self.title}
        root.after(200, lambda: 1 / 0)  # a timer that crashes while the screen is running''')


def test_probe_reports_tk_callback_errors(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, TIMER_CRASH))
    assert not ok and "a Tk callback raised ZeroDivisionError" in report
