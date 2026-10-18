"""UI smoke test: build every screen headless, check key widgets and a form submission."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def tk_root():
    import tkinter as tk

    last_err = None
    for _ in range(3):
        try:
            root = tk.Tk()
            break
        except tk.TclError as e:
            last_err = e
            import time
            time.sleep(0.2)
    else:
        pytest.skip(f"tk.Tk unavailable: {last_err}")
    root.withdraw()
    yield root
    # Cancel pending callbacks and destroy the root once.
    try:
        pending = root.tk.call("after", "info")
        for p in pending:
            try:
                root.after_cancel(p)
            except tk.TclError:
                pass
    except tk.TclError:
        pass
    try:
        root.destroy()
    except tk.TclError:
        pass


@pytest.fixture
def app(tk_root, tmp_path):
    import tkinter as tk

    from ui.app import create_app
    a = create_app(tk_root, db_path=str(tmp_path / "smoke.db"))
    tk_root.update_idletasks()
    yield a
    # Stop any animation loops, cancel pending afters, then destroy children.
    for screen in a._screens.values():
        canvas = getattr(screen, "canvas", None)
        if canvas is not None and hasattr(canvas, "stop"):
            try:
                canvas.stop()
            except tk.TclError:
                pass
        stop = getattr(screen, "_cancel_pending", None)
        if stop is not None:
            try:
                stop()
            except tk.TclError:
                pass
    _pending_cancel(tk_root)
    for child in list(tk_root.winfo_children()):
        try:
            child.destroy()
        except tk.TclError:
            pass
    tk_root.update_idletasks()


def _pending_cancel(root):
    pending = root.tk.call("after", "info")
    for p in pending:
        try:
            root.after_cancel(p)
        except tk.TclError:
            pass


def test_window_size(app):
    root = app.root
    w, h = root.minsize()
    assert w >= 1100 and h >= 750


def test_intro_screen(app):
    app.show("intro")
    screen = app._screens["intro"]
    assert screen.title is not None
    assert screen.skip_btn is not None
    assert screen.title.cget("text") == "Space Fractions"
    _pending_cancel(app.root)


def test_menu_screen(app):
    app.show("menu")
    screen = app._screens["menu"]
    assert screen.play_btn is not None
    assert screen.scores_btn is not None
    assert screen.help_btn is not None
    assert screen.admin_btn is not None
    assert screen.exit_btn is not None


def test_show_all_screens(app):
    for name in ["intro", "menu", "name", "question", "pause", "end",
                 "highscores", "help", "admin"]:
        app.show(name)
        assert app._current is app._screens[name]


def test_name_form_submission(app):
    app.show("name")
    screen = app._screens["name"]
    screen.name_var.set("AstroKid")
    screen._submit()
    app.root.update_idletasks()
    # After a valid name, input should be cleared and question screen shown.
    assert screen.name_var.get() == ""
    assert app._current is app._screens["question"]
    assert app.username == "AstroKid"


def test_question_answer_input_cleared(app):
    app.show("name")
    app._screens["name"].name_var.set("Kid")
    app._screens["name"]._submit()
    screen = app._screens["question"]
    app.root.update_idletasks()
    # Ensure we have a current typed question (seed typed questions have no options)
    q = screen._current_question
    assert q is not None
    # Type a wrong answer and submit; input must be cleared after.
    screen.answer_var.set("999/1")
    screen._submit()
    assert screen.answer_var.get() == ""
    # Cancel the pending auto-advance.
    _pending_cancel(app.root)


def test_pause_overlay(app):
    app.show("question")
    app.root.update_idletasks()
    screen = app._screens["question"]
    screen._pause()
    assert app._current is app._screens["pause"]
    pause = app._screens["pause"]
    assert pause.resume_btn is not None
