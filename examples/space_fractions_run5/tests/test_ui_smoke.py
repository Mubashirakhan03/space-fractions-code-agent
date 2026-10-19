"""UI smoke test: builds every screen, exercises a correct + wrong submission,
and plays one complete flow through the UI's own callbacks (headless-safe).

Uses ONE tk.Tk() for the whole session to avoid crashes on Windows.
"""
import tkinter as tk

import pytest

from ui.app import create_app


@pytest.fixture(scope="session")
def root():
    last = None
    for _ in range(3):
        try:
            r = tk.Tk()
            r.withdraw()
            return r
        except tk.TclError as e:
            last = e
    pytest.skip(f"Tk unavailable: {last}")


@pytest.fixture()
def window(root):
    """Build a fresh app; after each test, cancel timers and destroy widgets."""
    errors = []
    root.report_callback_exception = lambda exc, val, tb: errors.append(
        (exc, val)
    )
    app = create_app(root)
    root.update_idletasks()
    yield app, errors
    # cancel pending after callbacks and destroy children
    try:
        while root.after_pending():
            for t in root.tk.call("after", "info") or []:
                root.after_cancel(t)
    except Exception:
        pass
    for w in root.winfo_children():
        w.destroy()
    try:
        root.state("normal")
    except tk.TclError:
        pass


def test_min_size_and_screens_exist(window):
    app, errors = window
    assert app.root.minsize() >= (1100, 750)
    for name in ["intro", "menu", "name_entry", "question",
                 "end", "high_scores", "help", "admin"]:
        assert name in app.screens


def test_every_screen_renders(window):
    app, errors = window
    for name in ["intro", "menu", "name_entry", "question",
                 "end", "high_scores", "help", "admin"]:
        app.show(name)
        app.root.update_idletasks()
        assert errors == [], f"callback error on screen {name}: {errors}"


def test_name_entry_correct_and_wrong_submission(window):
    app, errors = window
    app.show("name_entry")
    screen = app.screens["name_entry"]
    # wrong: empty name
    screen.name_var.set("")
    screen._submit()
    app.root.update_idletasks()
    assert screen.feedback.cget("text") != ""
    # correct
    screen.name_var.set("Astro")
    screen._submit()
    app.root.update_idletasks()
    assert app.current_user == "Astro"
    assert app.controller is not None
    assert errors == []


def test_question_input_cleared_and_full_flow(window):
    app, errors = window
    app.start_game("Tester")
    app.show("question")
    screen = app.screens["question"]
    app.root.update_idletasks()

    ctl = app.controller
    total = ctl.game.total

    for i in range(total):
        q = ctl.current_question
        if q is None:
            break
        # exercise a typed-or-choice submission through the UI callback
        if q.is_multiple_choice:
            screen._submit(q.options[0])
        else:
            screen._input_var.set(q.answer)
            screen._submit(None)
        app.root.update()
        # input must be cleared automatically
        assert screen._input_var.get() == ""
        # pump real time for the after() timer
        for _ in range(20):
            app.root.update()

    assert ctl.is_finished
    assert ctl.state_machine.is_game_over
    # The feedback label shows the last answer result without error
    assert errors == [], f"callback errors: {errors}"


def test_pause_overlay_and_resume(window):
    app, errors = window
    app.start_game("PauseTester")
    app.show("question")
    screen = app.screens["question"]
    app.root.update_idletasks()
    screen._pause()
    app.root.update_idletasks()
    assert app.controller.state_machine.is_paused
    assert screen._pause_overlay.winfo_manager() == "place"
    screen._resume()
    app.root.update_idletasks()
    assert app.controller.state_machine.is_playing
    assert screen._pause_overlay.winfo_manager() == ""
    assert errors == []


def test_end_screen_renders_without_data(window):
    app, errors = window
    app.controller = None
    app.show("end")
    app.root.update_idletasks()
    screen = app.screens["end"]
    assert screen.title.cget("text")  # has some default text
    assert errors == []
