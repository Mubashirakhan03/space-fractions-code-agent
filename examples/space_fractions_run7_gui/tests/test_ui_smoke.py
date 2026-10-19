"""UI smoke test: one Tk() for the session, show every screen, play a full flow.

Harness contract: root withdrawn, app built via create_app, minsize asserted,
every screen shown, correct+wrong form submission exercised, one full flow
through the UI's own callbacks, no Tk callback errors.
"""
import time

import pytest


@pytest.fixture(scope="session")
def tk_root():
    import tkinter as tk

    last = None
    for _ in range(3):
        try:
            root = tk.Tk()
            root.withdraw()
            root.report_callback_exception = _make_collector()
            yield root
            root.destroy()
            return
        except tk.TclError as e:  # pragma: no cover
            last = e
            time.sleep(0.2)
    pytest.skip(f"tk unavailable: {last}")


def _make_collector():
    errors = []

    def handler(exc, val, tb):
        import traceback
        errors.append("".join(traceback.format_exception(exc, val, tb)))

    handler.errors = errors
    return handler


def _clear_widgets(root):
    # cancel pending after() callbacks
    import tkinter as tk
    try:
        for child in root.winfo_children():
            child.destroy()
    except tk.TclError:
        pass
    # cancel all after callbacks
    try:
        for after_id in root.tk.call("after", "info"):
            root.after_cancel(after_id)
    except tk.TclError:
        pass


@pytest.fixture()
def app(tk_root):
    import tkinter as tk
    from ui.app import create_app

    _clear_widgets(tk_root)
    a = create_app(tk_root)
    tk_root.update_idletasks()
    yield a
    a.repo.close()
    _clear_widgets(tk_root)


def test_minsize(tk_root):
    import tkinter as tk
    from ui.app import create_app

    _clear_widgets(tk_root)
    a = create_app(tk_root)
    tk_root.update_idletasks()
    w, h = tk_root.minsize()
    assert w >= 1100
    assert h >= 750
    a.repo.close()
    _clear_widgets(tk_root)


def test_all_screens_show(app, tk_root):
    import ui.theme as theme  # noqa: F401

    names = ["intro", "menu", "game", "pause", "results", "help", "score", "admin"]
    for name in names:
        app.show(name)
        tk_root.update_idletasks()
        frame = app.screens[name]
        assert frame.winfo_manager(), f"{name} not managed/packed"
    # key widgets exist
    assert hasattr(app.screens["menu"], "play_btn")
    assert hasattr(app.screens["game"], "entry")
    assert hasattr(app.screens["game"], "submit_btn")
    assert hasattr(app.screens["admin"], "add_btn")


def test_typed_and_choice_input_and_full_flow(app, tk_root):
    # full flow: intro -> menu -> game -> (answers) -> results
    app.show("intro")
    tk_root.update()
    app.show("menu")
    tk_root.update()
    app.show("game")
    tk_root.update()

    game = app.screens["game"]
    # The round mixes typed and choice questions; drive the whole round to
    # completion by reading each question and submitting a valid answer.
    errors = []
    root = tk_root
    collector = root.report_callback_exception
    steps = 0
    max_steps = 50
    while steps < max_steps:
        steps += 1
        tk_root.update()
        time.sleep(0.01)
        q = app.service.current_question()
        if q is None:
            break
        assert collector.errors == [], f"callback error: {collector.errors}"
        if q.options:
            # choice input: click the correct button
            opt = q.correct
            for b in game.choice_buttons:
                if b.cget("text") == opt:
                    b.invoke()
                    break
            else:
                game.choice_buttons[0].invoke()
        else:
            # typed input: submit the correct value (correct path)
            game.entry.delete(0, "end")
            game.entry.insert(0, q.correct)
            assert game.entry.get() == q.correct
            game.submit_btn.invoke()
            # input cleared after submission
            tk_root.update()
            assert game.entry.get() == ""
        # pump for the after(900, ...) advance timer
        for _ in range(20):
            tk_root.update()
            time.sleep(0.02)

    # we should now be on results (or finished)
    assert app.service.game.is_finished
    # assert no callback errors occurred during the whole run
    assert collector.errors == []
    # feedback text from a wrong submission names the expected value
    test_wrong_submission_feedback(app, tk_root)


def test_wrong_submission_feedback(app, tk_root):
    app.show("game")
    tk_root.update()
    game = app.screens["game"]
    q = app.service.current_question()
    if q is None:
        # already finished; restart
        app.service.play()
        tk_root.update()
        q = app.service.current_question()
    # pick a definitely-wrong answer
    wrong = _a_wrong_answer(q)
    if q.options:
        game._submit_choice(wrong)
    else:
        game.entry.delete(0, "end")
        game.entry.insert(0, wrong)
        game.submit_btn.invoke()
    tk_root.update()
    # feedback should name the expected value of the just-submitted item
    text = game.feedback.cget("text")
    assert q.correct in text
    assert game.feedback.cget("fg") == theme_error_color()


def _a_wrong_answer(q):
    from fractions import Fraction
    # Build an answer that is genuinely different from the correct value.
    try:
        c = Fraction(q.correct)
    except (ValueError, ZeroDivisionError):
        return "999999999999/1"
    wrong = c + Fraction(1, max(1, c.denominator))
    return f"{wrong.numerator}/{wrong.denominator}"


def theme_error_color():
    from ui import theme
    return theme.ERROR


def test_enter_key_submits(app, tk_root):
    app.show("game")
    tk_root.update()
    game = app.screens["game"]
    q = app.service.current_question()
    if q is not None and not q.options:
        game.entry.delete(0, "end")
        game.entry.insert(0, q.correct)
        game.entry.event_generate("<Return>")
        tk_root.update()
        assert game.entry.get() == ""
