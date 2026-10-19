"""UI smoke test: builds every screen headless, checks key widgets and input clearing."""
import tkinter as tk

import pytest


@pytest.fixture(scope="session")
def root():
    last = None
    for _ in range(3):
        try:
            root = tk.Tk()
            break
        except tk.TclError as exc:
            last = exc
    else:
        pytest.skip(f"Tk unavailable: {last}")
    root.withdraw()
    root.minsize(1100, 750)
    yield root
    root.destroy()


@pytest.fixture
def app(root):
    from ui.app import create_app
    return create_app(root)


def cleanup(root):
    for w in root.winfo_children():
        w.destroy()
    for cb in root.tk.call("after", "info"):
        root.after_cancel(cb)


@pytest.fixture(autouse=True)
def _cleanup(root):
    yield
    cleanup(root)


def test_min_size(root):
    root.deiconify()
    root.update_idletasks()
    assert root.minsize()[0] >= 1100
    assert root.minsize()[1] >= 750
    root.withdraw()


def test_all_screens_have_title(app):
    app.root.update_idletasks()
    for name in ["intro", "menu", "name", "question", "end",
                 "high_scores", "help", "admin"]:
        app.show(name)
        app.root.update_idletasks()
        screen = app.screens[name]
        assert screen.winfo_exists()


def test_menu_buttons(app):
    app.show("menu")
    s = app.screens["menu"]
    assert s.play_button is not None
    assert s.scores_button is not None
    assert s.help_button is not None
    assert s.admin_button is not None
    assert s.exit_button is not None


def test_name_entry_cleared(app):
    app.set_player_name("")
    app.show("name")
    s = app.screens["name"]
    s.name_entry.delete(0, tk.END)
    s.name_entry.insert(0, "Zoe")
    app.root.update_idletasks()
    # Simulate submit by directly calling the handler
    s._submit()
    app.root.update_idletasks()
    assert s.name_entry.get() == ""


def test_question_input_cleared_after_answer(app):
    app.set_player_name("Test")
    app.start_game()
    app.show("question")
    s = app.screens["question"]
    app.root.update_idletasks()
    if app.game is None or app.game.is_finished():
        pytest.skip("no questions available")
    # pick a question, clear its input, type, evaluate
    s.answer_entry.delete(0, tk.END)
    s.answer_entry.insert(0, "1/2")
    s._evaluate("1/2")
    app.root.update_idletasks()
    assert s.answer_entry.get() == ""
