"""UI smoke test: one Tk session, show every screen, play a full flow.

Runs headless using root.withdraw(); never destroys/recreates Tk between tests.
"""
import time

import tkinter as tk

import pytest


errors = []


def _retry_create():
    last = None
    for _ in range(3):
        try:
            return tk.Tk()
        except tk.TclError as e:
            last = e
    raise last


@pytest.fixture(scope="session")
def root():
    try:
        r = _retry_create()
    except tk.TclError:
        pytest.skip("No display available")
    r.withdraw()

    def _report(exc, val, tb):
        errors.append((exc, val))

    r.report_callback_exception = _report
    yield r
    for w in r.winfo_children():
        w.destroy()
    try:
        r.destroy()
    except tk.TclError:
        pass


def _cleanup(root):
    for w in root.winfo_children():
        w.destroy()
    errors.clear()


def _pump(root, seconds=0.05):
    end = time.time() + seconds
    while time.time() < end:
        root.update()


def test_window_sizing_and_screens(root, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from ui.app import create_app
    app = create_app(root)
    root.update_idletasks()
    mw, mh = root.minsize()
    assert mw >= 1100 and mh >= 750
    assert root.title() == "Space Fractions"
    for name in ("intro", "login", "menu", "play", "pause", "score", "help", "admin"):
        app.show(name)
        root.update_idletasks()
    assert len(errors) == 0, f"Tk callback errors: {errors}"
    _cleanup(root)


def test_typed_and_choice_flow(root, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from ui.app import create_app
    app = create_app(root)
    app.controller.login("tester", "user")
    app.show("menu")
    root.update()
    app.show("play")
    root.update()

    game = app.controller.game
    assert game is not None

    screen = app.screens["play"]
    typed_seen = False
    choice_seen = False
    steps = 0
    while game.state.value != "GameOver" and steps < 40:
        steps += 1
        q = game.current_question
        if q.kind == "choice":
            choice_seen = True
            screen._submit(q.correct)
        else:
            typed_seen = True
            # type the correct answer into the real entry, then submit
            screen._entry.delete(0, "end")
            screen._entry.insert(0, q.correct)
            screen._submit_typed()
        _pump(root, 0.9)  # allow the after(800) advance to fire
        game = app.controller.game
        if game is None:
            break

    assert typed_seen, "flow should include a typed question"
    assert choice_seen, "flow should include a choice question"
    assert len(errors) == 0, f"Tk callback errors: {errors}"
    _cleanup(root)
