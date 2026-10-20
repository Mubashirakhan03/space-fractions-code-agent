"""UI smoke tests: window setup, every screen, animation, Skip, PIN gate,
admin CRUD, and a full play-through flow."""
import time
import tkinter as tk

import pytest


def _make_root():
    for _ in range(3):
        try:
            root = tk.Tk()
            return root
        except tk.TclError:
            time.sleep(0.2)
    pytest.skip("Tk unavailable in this environment")


@pytest.fixture(scope="session")
def root():
    r = _make_root()
    r.withdraw()
    yield r
    try:
        r.destroy()
    except Exception:
        pass


def _clear_widgets(root):
    for aid in root.tk.call("after", "info"):
        try:
            root.after_cancel(aid)
        except Exception:
            pass
    for w in list(root.winfo_children()):
        try:
            w.destroy()
        except Exception:
            pass


@pytest.fixture
def app(root, tmp_path):
    _clear_widgets(root)
    root.deiconify()
    root.update_idletasks()
    seed = open("data/questions_seed.json", encoding="utf-8").read()
    from ui.app import create_app
    a = create_app(root, data_dir=tmp_path, seed_json=seed, rng_seed=7)
    yield a
    for s in a.screens.values():
        s.on_hide()
    _clear_widgets(root)


def _pump(root, seconds):
    end = time.time() + seconds
    while time.time() < end:
        root.update()
        time.sleep(0.02)


def _show(app, name):
    app.show(name)
    app.root.update_idletasks()


def test_window_minimum_size_and_title(root, app):
    root.update_idletasks()
    assert root.minsize()[0] >= 1100
    assert root.minsize()[1] >= 750
    assert root.title() == "Space Fractions"


def test_all_screens_exist(app):
    for name in ("intro_movie", "main_menu", "question_screen", "ending_scene",
                 "help_screen", "score_screen", "pin_screen", "admin_screen"):
        assert name in app.screens


def test_every_screen_renders(root, app):
    for name in app.screens:
        app.show(name)
        root.update_idletasks()
        assert app.current is app.screens[name]
    app.show("main_menu")


def test_intro_movie_objects_move_and_skip(root, app):
    _show(app, "intro_movie")
    movie = app.screens["intro_movie"]
    app.root.update()
    movie.canvas.update()
    before = movie.canvas.coords(movie.rocket)
    _pump(root, 0.6)
    after = movie.canvas.coords(movie.rocket)
    assert before != after, "rocket did not move"
    movie.skip()
    root.update_idletasks()
    assert app.current is app.screens["main_menu"]
    assert movie._after_ids == []


def test_pin_gate(root, app):
    _show(app, "pin_screen")
    pin = app.screens["pin_screen"]
    pin.pin_entry.insert(0, "9999")
    pin.unlock()
    root.update_idletasks()
    assert "Incorrect" in pin.error_label.cget("text")
    assert app.current is pin
    pin.pin_entry.delete(0, "end")
    pin.pin_entry.insert(0, app.settings.admin_pin)
    pin.unlock()
    root.update_idletasks()
    assert app.current is app.screens["admin_screen"]


def test_admin_list_seeded_and_crud(root, app):
    _show(app, "admin_screen")
    admin = app.screens["admin_screen"]
    assert admin.listbox.size() >= 20

    admin.prompt_entry.insert(0, "Brand new question")
    admin.correct_entry.insert(0, "5/6")
    admin.choices_entry.insert(0, "5/6, 1/2, 2/3")
    admin.kind_var.set("identify")
    before = admin.listbox.size()
    admin.add_question()
    root.update_idletasks()
    assert admin.listbox.size() == before + 1

    admin.listbox.selection_clear(0, "end")
    admin.listbox.selection_set("end")
    admin._on_select()
    admin.prompt_entry.delete(0, "end")
    admin.prompt_entry.insert(0, "Edited question")
    admin.edit_question()
    root.update_idletasks()
    assert "Edited question" in admin.listbox.get("end")

    import tkinter.messagebox as mb
    orig = mb.askyesno
    mb.askyesno = lambda *a, **k: True
    try:
        admin.listbox.selection_clear(0, "end")
        admin.listbox.selection_set("end")
        admin._on_select()
        after = admin.listbox.size()
        admin.delete_question()
        root.update_idletasks()
        assert admin.listbox.size() == after - 1
    finally:
        mb.askyesno = orig


def test_form_correct_and_wrong_submission(root, app):
    app.start_round()
    _show(app, "question_screen")
    qs = app.screens["question_screen"]
    rnd = app.service.current_round
    first = rnd.current
    expected = first.correct_value
    qs._handle_submit(expected)
    root.update_idletasks()
    assert qs.feedback_label.cget("text") != ""
    assert expected in qs.feedback_label.cget("text")

    if rnd.current is not None and not rnd.finished:
        cur = rnd.current
        exp = cur.correct_value
        if cur.has_choices():
            wrong = next((c for c in cur.choices if c != exp), None)
        else:
            wrong = "0/1"
        qs._handle_submit(wrong)
        root.update_idletasks()
        assert exp in qs.feedback_label.cget("text")


def test_full_playthrough_to_ending(root, app):
    _show(app, "main_menu")
    app.start_round()
    _show(app, "question_screen")
    qs = app.screens["question_screen"]
    guard = 0
    while app.service.current_round and not app.service.current_round.finished and guard < 20:
        rnd = app.service.current_round
        q = rnd.current
        if q is None:
            break
        qs._handle_submit(q.correct_value)
        _pump(root, 0.9)
        guard += 1
    root.update_idletasks()
    assert app.current is app.screens["ending_scene"]


def test_help_and_score_screens(root, app):
    _show(app, "help_screen")
    assert app.current is app.screens["help_screen"]
    _show(app, "score_screen")
    assert app.current is app.screens["score_screen"]
