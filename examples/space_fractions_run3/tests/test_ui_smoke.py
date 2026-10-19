"""UI smoke test: build every screen headless, exercise one correct and one
wrong form submission (input cleared, feedback names the right item)."""
import tkinter as tk

import pytest


@pytest.fixture(scope="session")
def root():
    for _ in range(3):
        try:
            r = tk.Tk()
            break
        except tk.TclError:
            r = None
    if r is None:
        pytest.skip("No display available for Tk")
    r.withdraw()
    yield r
    # cancel pending after() callbacks
    try:
        for aid in r.tk.call("after", "info"):
            try:
                r.after_cancel(aid)
            except Exception:
                pass
    except Exception:
        pass
    try:
        r.destroy()
    except Exception:
        pass


@pytest.fixture(scope="session")
def app(root, tmp_path_factory):
    db = str(tmp_path_factory.mktemp("smoke") / "smoke.db")
    import os
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seed = os.path.join(here, "data", "questions.json")
    from ui.app import create_app
    a = create_app(root, db_path=db, seed_path=seed)
    return a


@pytest.fixture(autouse=True)
def _cleanup(app):
    # Cancel any pending after() callbacks between tests; keep screens intact.
    yield
    root = app.root
    for aid in list(root.tk.call("after", "info")):
        try:
            root.after_cancel(aid)
        except Exception:
            pass


def test_minsize(root, app):
    root.update_idletasks()
    w, h = root.minsize()
    assert w >= 1100
    assert h >= 750


KEY_ATTRS = {
    "intro": ("title_label", "skip_button"),
    "menu": ("title_label", "play_button"),
    "name": ("title_label", "name_entry", "start_button"),
    "question": ("progress_label", "score_label", "pause_button", "prompt_label"),
    "end": ("congrats_label", "again_button", "menu_button"),
    "scores": ("title_label", "menu_button"),
    "help": ("title_label", "menu_button"),
    "admin": ("title_label", "save_button", "delete_button"),
}


def test_all_screens_show(root, app):
    for name in ["intro", "menu", "name", "question", "end", "scores", "help", "admin"]:
        app.show(name)
        root.update_idletasks()
        screen = app.screens[name]
        for attr in KEY_ATTRS[name]:
            assert hasattr(screen, attr), f"{name} missing {attr}"


def test_name_entry_correct_submission(root, app):
    screen = app.screens["name"]
    app.show("name")
    screen.name_entry.insert(0, "Astro Kid")
    screen._start()
    root.update_idletasks()
    assert app.player_name == "Astro Kid"
    assert screen.name_entry.get() == ""


def test_question_submission_clears_input_and_shows_feedback(root, app):
    # Start a known round to control the first question.
    app.start_round("Tester")
    qs = app.screens["question"]
    app.show("question")
    q = app.game_service.game.current_question
    # Wrong submission: typed input path
    if q.options:
        # choose a wrong option by clicking the equivalent of a wrong answer
        wrong = next((o for o in q.options if o != q.answer), None)
        if wrong is not None:
            qs._submit_text(wrong)
            root.update_idletasks()
            # feedback names the expected value of the item just answered
            assert q.answer in qs.feedback_label.cget("text")
            assert qs.entry.get() == ""
