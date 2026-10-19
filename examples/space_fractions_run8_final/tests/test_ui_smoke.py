"""UI smoke test: one Tk for the whole session, show all screens, exercise a
correct + wrong submission, play one full flow, assert no callback errors.

Headless: root is withdrawn; we never require a display to run callbacks.
"""
import time
import tempfile
import os
import tkinter as tk

import pytest


@pytest.fixture(scope="session")
def root():
    attempts = 0
    root = None
    while attempts < 3:
        try:
            root = tk.Tk()
            break
        except tk.TclError:
            attempts += 1
            time.sleep(0.1)
    if root is None:
        pytest.skip("No display available for Tk")
    root.withdraw()
    yield root
    try:
        root.destroy()
    except tk.TclError:
        pass


@pytest.fixture(scope="session")
def db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def _cancel_afters(root):
    for wid in root.winfo_children():
        wid.destroy()
    root.update_idletasks()


@pytest.fixture()
def app(root, db_path):
    from ui.app import create_app
    a = create_app(root, db_path=db_path)
    yield a
    a.db.close()
    _cancel_afters(root)


def test_window_min_size_and_title(app):
    assert app.root.title() == "Space Fractions"
    app.root.update_idletasks()
    assert app.root.minsize()[0] >= 1100
    assert app.root.minsize()[1] >= 750


def test_all_screens_exist(app):
    expected = {
        "intro", "menu", "play", "results", "score", "help", "pin", "admin",
    }
    assert expected <= set(app.screens.keys())


def test_every_screen_renders(app):
    for name, screen in app.screens.items():
        if name == "admin":
            app.admin_unlocked = True
        app.show(name)
        app.root.update()
        assert screen is not None
    app.admin_unlocked = False


def _pump(root, seconds):
    end = time.time() + seconds
    while time.time() < end:
        root.update()
        time.sleep(0.02)


def test_intro_animates_and_skip(app):
    errors = []
    app.root.report_callback_exception = lambda *a: errors.append(a)
    app.show("intro")
    screen = app.screens["intro"]
    app.root.update()
    _pump(app.root, 0.5)
    # item coordinates must have changed (stars/rocket moved)
    star = screen._stars[0]["item"]
    x0, y0, _, _ = screen.canvas.coords(star)
    _pump(app.root, 0.3)
    _, ny, _, _ = screen.canvas.coords(star)
    assert ny > y0, "stars should have moved downward"
    # skip cancels callbacks and goes to menu
    screen._skip()
    app.root.update()
    assert app.screens["menu"].winfo_ismapped()
    assert not errors, errors


def test_pin_protection(app):
    app.show("pin")
    pin = app.screens["pin"]
    app.root.update()
    # ensure entry is masked
    assert pin.entry.cget("show") == "*"
    # wrong pin
    pin.entry.insert(0, "0000")
    pin._unlock()
    app.root.update()
    assert not app.admin_unlocked
    assert "Incorrect" in pin.error.cget("text")
    # correct pin
    pin.entry.delete(0, "end")
    pin.entry.insert(0, app.get_pin())
    pin._unlock()
    app.root.update()
    assert app.admin_unlocked
    # leaving locks again
    app.show("menu")
    assert not app.admin_unlocked


def test_form_submissions(app):
    errors = []
    app.root.report_callback_exception = lambda *a: errors.append(a)
    # use a deterministic small game with a known question
    from question.question import Question
    from game.game import Game
    q = Question("Which equals 1/2?", ["2/4", "1/3", "2/5", "3/4"], 0)
    app.current_game = Game([q])
    app.show("play")
    play = app.screens["play"]
    app.root.update()
    assert play.prompt_label.cget("text") == "Which equals 1/2?"
    # correct submission
    play._submit("2/4")
    app.root.update()
    assert "Correct" in play.feedback.cget("text")
    assert "2/4" in play.feedback.cget("text")
    assert not errors, errors


def test_wrong_submission_names_expected_value(app):
    errors = []
    app.root.report_callback_exception = lambda *a: errors.append(a)
    from question.question import Question
    from game.game import Game
    q = Question("Which equals 1/2?", ["2/4", "1/3", "2/5", "3/4"], 0)
    app.current_game = Game([q])
    app.show("play")
    play = app.screens["play"]
    app.root.update()
    play._submit("1/3")  # wrong
    app.root.update()
    assert "Wrong" in play.feedback.cget("text")
    # expected value is the CORRECT answer of the just-submitted item (2/4),
    # NOT the next item's value
    assert "2/4" in play.feedback.cget("text")
    assert not errors, errors


def test_full_flow_to_results(app):
    errors = []
    app.root.report_callback_exception = lambda *a: errors.append(a)
    from question.question import Question, QuestionKind
    from game.game import Game

    # two questions: one typed (decimal), one choice — switches between variants
    q1 = Question("What is 1/2 as a decimal?", ["0.5", "0.2", "0.25", "0.1"],
                  0, kind=QuestionKind.DECIMAL)
    q2 = Question("Which is larger: 1/4 or 1/2?", ["1/2", "1/4", "1/3", "1/8"],
                  0, kind=QuestionKind.LARGER)
    app.current_game = Game([q1, q2])
    app.show("play")
    play = app.screens["play"]
    app.root.update()

    # first is decimal -> typed input
    assert play.entry.winfo_exists()
    play.entry.insert(0, "0.5")
    play._submit_text()
    app.root.update()
    assert "0.5" in play.feedback.cget("text")

    # second is choice
    play._submit("1/2")
    # after last answer, results should appear
    _pump(app.root, 0.8)
    app.root.update()
    assert app.screens["results"].winfo_ismapped()
    results = app.screens["results"]
    assert "Score: 2 / 2" in results.score_label.cget("text")
    assert not errors, errors
