"""UI smoke test (headless): builds the app once, shows every screen, plays a
full flow through real callbacks, checks input clearing and no Tk callback
errors. One Tk root for the whole session.
"""
import time
import tkinter as tk

import pytest


@pytest.fixture(scope="session")
def root():
    attempts = 0
    while True:
        try:
            root = tk.Tk()
            break
        except tk.TclError:
            attempts += 1
            if attempts >= 3:
                pytest.skip("Tk unavailable in this environment")
            time.sleep(1)
    root.withdraw()
    yield root
    try:
        root.destroy()
    except tk.TclError:
        pass


@pytest.fixture()
def app(root, tmp_path):
    from ui.app import create_app
    # fresh app each test, using a tmp db
    errors = []
    root.report_callback_exception = lambda exc, val, tb: errors.append(val)
    a = create_app(root, db_path=tmp_path / "test.db")
    root.update_idletasks()
    a._test_errors = errors
    yield a
    # cancel pending after callbacks (intro animation, question advance)
    for name, screen in a.screens.items():
        for attr in ("_after_id", "_next_after", "_confetti_after"):
            aid = getattr(screen, attr, None)
            if aid is not None:
                try:
                    screen.after_cancel(aid)
                except Exception:
                    pass
    # destroy child frames of the background canvas
    for w in a.background.winfo_children():
        w.destroy()


def _flush(root, seconds=0.05, steps=2):
    for _ in range(steps):
        root.update()
        time.sleep(seconds / steps)
    root.update()


def test_minsize_and_screens(app, root):
    assert root.minsize()[0] >= 1100
    assert root.minsize()[1] >= 750

    app.show("intro")
    root.update_idletasks()
    assert app.screens["intro"].skip_button.winfo_exists()

    app.show("menu")
    root.update_idletasks()
    menu = app.screens["menu"]
    for attr in ("play_button", "scores_button", "help_button", "admin_button",
                 "exit_button"):
        assert getattr(menu, attr).winfo_exists()

    app.show("name")
    assert app.screens["name"].name_entry.winfo_exists()
    app.show("question")
    assert app.screens["question"].question_label.winfo_exists()
    app.show("scores")
    assert app.screens["scores"].scores_text.winfo_exists()
    app.show("help")
    assert app.screens["help"].help_text.winfo_exists()
    app.show("admin")
    assert app.screens["admin"].pass_entry.winfo_exists()
    app.show("end")
    assert app.screens["end"].title_label.winfo_exists()


def test_full_flow_with_typed_and_choice(app, root):
    # name entry -> typed question -> choice question -> end screen
    from questions.question import Question, QuestionType
    from game.game import Game
    app.show("name")
    name_screen = app.screens["name"]
    name_screen.name_entry.insert(0, "Mia")
    app.player_name = "Mia"
    # Set a deterministic game directly (skip the random 10-question sample).
    app.game = Game(id="g1", questions=[
        Question(id="t", prompt="Type 1/2", answer="1/2", is_choice=False),
        Question(id="c", prompt="Pick", options=["1/2", "3/4"], answer="1/2",
                 qtype=QuestionType.EQUIVALENT, is_choice=True),
    ])
    app.game.play()
    qs = app.screens["question"]
    app.show("question")
    root.update_idletasks()

    # typed question: submit correct answer
    qs.answer_entry.insert(0, "2/4")  # equivalent accepted
    qs.submit_typed()
    root.update_idletasks()
    assert qs.answer_entry.get() == ""  # cleared after submission

    # wait for auto-advance to next (choice) question
    _flush(root, seconds=1.1)
    # now a choice question: click first (correct) button
    assert len(qs.choice_buttons) == 2
    qs.choice_buttons[0].invoke()
    _flush(root, seconds=1.1)

    # should now be game over -> end screen
    _flush(root, seconds=1.1)
    app.show("end")
    root.update_idletasks()
    end = app.screens["end"]
    assert "Mia" in end.title_label.cget("text")
    assert app._test_errors == []


def test_wrong_answer_feedback_names_expected(app, root):
    from questions.question import Question
    from game.game import Game
    app.show("name")
    app.screens["name"].name_entry.insert(0, "Kai")
    app.player_name = "Kai"
    app.game = Game(id="g1", questions=[Question(id="x", prompt="Type 3/4",
                                                 answer="3/4", is_choice=False)])
    app.game.play()
    qs = app.screens["question"]
    app.show("question")
    root.update_idletasks()
    qs.answer_entry.insert(0, "1/2")  # wrong
    qs.submit_typed()
    root.update_idletasks()
    fb = qs.feedback.cget("text")
    assert "3/4" in fb
    assert qs.answer_entry.get() == ""


def test_pause_overlay(app, root):
    from game.game import Game
    from questions.question import Question
    app.player_name = "Lea"
    app.game = Game(id="g1", questions=[Question(id="p", prompt="Type 1/2",
                                                 answer="1/2", is_choice=False)])
    app.game.play()
    qs = app.screens["question"]
    app.show("question")
    root.update_idletasks()
    qs.pause()
    root.update_idletasks()
    assert app.game.state.value == "Paused"
    assert qs.overlay.winfo_manager() == "place"
    qs.resume()
    root.update_idletasks()
    assert app.game.state.value == "Playing"
    assert qs.overlay.winfo_manager() != "place"


def test_high_scores_and_admin(app, root):
    # admin passcode unlock
    app.show("admin")
    admin_screen = app.screens["admin"]
    admin_screen.pass_entry.insert(0, "admin")
    admin_screen.unlock()
    root.update_idletasks()
    assert admin_screen.feedback.cget("text") == "Unlocked ✓"

    # wrong passcode path
    app.show("admin")
    admin_screen.pass_entry.insert(0, "nope")
    admin_screen.unlock()
    root.update_idletasks()
    assert "Wrong passcode" in admin_screen.feedback.cget("text")

    # high scores default (no data) -> advisory
    app.show("scores")
    root.update_idletasks()
    assert app.screens["scores"].scores_text.get("1.0", "end").strip() != ""
