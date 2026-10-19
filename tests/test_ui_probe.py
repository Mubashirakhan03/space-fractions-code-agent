"""The harness UI probe catches broken layouts that unit tests miss (real window, generic checks)."""

import tkinter as tk

import pytest

from sfagent.agent.ui_probe import run_ui_probe
from sfagent.tools.runner import PythonRunner


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
        root.title("Good App")
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
        (tmp_path / "ui").mkdir(parents=True)
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
    assert not ok and "screen 'end' @1280x800: app.show() raised RuntimeError" in report


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


NO_ROOM = '''import tkinter as tk


class App:
    def __init__(self, root):
        panel = tk.Frame(root, bg="navy", height=300)
        panel.pack(fill="x")
        panel.pack_propagate(False)
        for i in range(8):
            tk.Button(panel, text=f"Option {i}", font=("Segoe UI", 20)).pack(pady=6)
        self.screens = {"menu": panel}

    def show(self, name):
        pass


def create_app(root):
    return App(root)
'''


def test_probe_flags_buttons_without_room(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, NO_ROOM))
    assert not ok and "is laid out but not shown" in report


CLIPPED = '''import tkinter as tk


class App:
    def __init__(self, root):
        root.minsize(1100, 750)
        frame = tk.Frame(root, bg="navy")
        frame.place(relwidth=1, relheight=1)
        row = tk.Frame(frame, height=30, bg="navy")
        row.pack(pady=40)
        row.grid_propagate(False)
        row.configure(width=600)
        tk.Button(row, text="Play again", font=("Segoe UI", 22), pady=20).grid(row=0, column=0)
        self.screens = {"end": frame}

    def show(self, name):
        pass


def create_app(root):
    return App(root)
'''

INPUT_NO_BUTTON = '''import tkinter as tk


class App:
    def __init__(self, root):
        root.minsize(1100, 750)
        frame = tk.Frame(root)
        frame.place(relwidth=1, relheight=1)
        tk.Label(frame, text="Type your answer", font=("Segoe UI", 24)).pack(pady=20)
        box = tk.Frame(frame)
        box.pack()
        tk.Entry(box, font=("Segoe UI", 24)).pack()
        self.screens = {"question": frame}

    def show(self, name):
        pass


def create_app(root):
    return App(root)
'''

FITS_ONLY_LARGE = '''import tkinter as tk


class App:
    def __init__(self, root):
        root.minsize(1100, 750)
        panel = tk.Frame(root)
        panel.pack(fill="both", expand=True)
        tk.Canvas(panel, height=735, highlightthickness=0).pack()  # fixed pixels: fits 800 px, not 750 px
        tk.Button(panel, text="Exit", font=("Segoe UI", 10)).pack()
        self.screens = {"menu": panel}

    def show(self, name):
        pass


def create_app(root):
    return App(root)
'''


def test_probe_flags_cut_off_button_text(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, CLIPPED))
    assert not ok and "is cut off" in report


def test_probe_flags_text_input_without_submit_button(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, INPUT_NO_BUTTON))
    assert not ok and "has no visible submit button" in report


def test_probe_checks_minimum_window_size(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, FITS_ONLY_LARGE))
    problems = report.split("):\n", 1)[-1]  # the list after the "checked: …" header
    # The min-size pass must report it. (Whether 1280x800 is also flagged depends on the test machine's screen:
    # CI runners have small virtual displays that cannot show a 1280x800 window.)
    assert not ok and "@1100x750" in problems


SCROLL_LIST = '''import tkinter as tk


class App:
    def __init__(self, root):
        root.minsize(1100, 750)
        root.title("Scroll App")
        frame = tk.Frame(root)
        frame.place(relwidth=1, relheight=1)
        tk.Label(frame, text="Questions", font=("Segoe UI", 28)).pack()
        canvas = tk.Canvas(frame, height=300)
        bar = tk.Scrollbar(frame, command=canvas.yview)
        canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        canvas.pack(fill="x")
        inner = tk.Frame(canvas)
        canvas.create_window(0, 0, window=inner, anchor="nw")
        for i in range(40):  # far more rows than fit: they scroll, which is fine
            tk.Button(inner, text=f"Row {i}", font=("Segoe UI", 16)).pack()
        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        self.screens = {"admin": frame}

    def show(self, name):
        pass


def create_app(root):
    return App(root)
'''


def test_probe_allows_rows_of_a_scrollable_list(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, SCROLL_LIST))
    assert ok, report


def test_probe_flags_default_tk_title(tmp_path):
    untitled = GOOD.replace('        root.title("Good App")\n', "")
    ok, report = run_ui_probe(make(tmp_path, untitled))
    assert not ok and "default 'tk'" in report


def test_probe_accepts_title_set_in_main(tmp_path):
    untitled = GOOD.replace('        root.title("Good App")\n', "")
    runner = make(tmp_path, untitled)
    (tmp_path / "main.py").write_text('import tkinter as tk\n\nroot = None\n\n\ndef main():\n'
                                      '    root = tk.Tk()\n    root.title("My Real App")\n')
    ok, report = run_ui_probe(runner)
    assert ok, report


INVISIBLE_INPUT = GOOD.replace(
    '''        self.screens = {"menu": self.title, "end": self.title}''',
    '''        form = tk.Frame(root, bg="#1C2340")
        form.place(relx=0.5, rely=0.7, anchor="center")
        tk.Entry(form, bg="#1C2340", relief="flat", highlightthickness=0).pack(side="left")
        tk.Button(form, text="Save").pack(side="left")
        self.screens = {"menu": form, "end": form}''')


def test_probe_flags_invisible_text_input(tmp_path):
    ok, report = run_ui_probe(make(tmp_path, INVISIBLE_INPUT))
    assert not ok and "cannot be seen" in report


ANIMATED = '''import tkinter as tk


class App:
    def __init__(self, root, skip=True, moving=True, pin=False):
        self.root = root
        root.title("Animated App")
        self.moving = moving
        self.canvas = tk.Canvas(root, bg="navy", highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)
        self.ship = self.canvas.create_rectangle(10, 100, 60, 130, fill="white")
        self.frame = tk.Frame(root, bg="#223")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self.frame, text="Opening scene", font=("Segoe UI", 28)).pack()
        if skip:
            tk.Button(self.frame, text="Skip", command=lambda: None).pack()
        if pin:
            tk.Entry(self.frame, show="*", relief="solid", bd=2).pack()
            tk.Button(self.frame, text="Unlock").pack()
        self.screens = {"intro": self.frame, "menu": self.frame}
        self.step()

    def step(self):
        if self.moving:
            self.canvas.move(self.ship, 5, 0)
        self.root.after(33, self.step)

    def show(self, name):
        pass


def create_app(root):
    return App(root, **OPTIONS)
'''
SPEC_REQ = {"animation": ["introductory movie"], "protected_roles": ["Admin"]}


def animated(tmp_path, **options):
    return make(tmp_path, f"OPTIONS = {options!r}\n" + ANIMATED)


def test_probe_flags_missing_animation_when_the_spec_asks_for_one(tmp_path):
    ok, report = run_ui_probe(animated(tmp_path, moving=False), requirements={"animation": ["introductory movie"]})
    assert not ok and "the spec asks for 'introductory movie', but no screen shows moving objects" in report


def test_probe_accepts_animation_with_skip_and_ignores_it_when_not_required(tmp_path):
    ok, report = run_ui_probe(animated(tmp_path), requirements={"animation": ["introductory movie"]})
    assert ok, report
    ok, report = run_ui_probe(make(tmp_path / "plain", GOOD), requirements={})  # no requirement → no check
    assert ok, report


def test_probe_flags_animation_without_skip_button(tmp_path):
    ok, report = run_ui_probe(animated(tmp_path, skip=False), requirements={"animation": ["introductory movie"]})
    assert not ok and "has no visible 'Skip' button" in report


def test_probe_requires_a_masked_pin_input_for_protected_roles(tmp_path):
    ok, report = run_ui_probe(animated(tmp_path / "a"), requirements=SPEC_REQ)
    assert not ok and "protected role(s) Admin, but no screen has a masked PIN input" in report
    ok, report = run_ui_probe(animated(tmp_path / "b", pin=True), requirements=SPEC_REQ)
    assert ok, report


MANAGED = '''import tkinter as tk


class App:
    def __init__(self, root, rows=3, buttons=("Add", "Edit", "Delete"), locked=False):
        self.root = root
        root.title("Records App")
        self.admin_unlocked = not locked
        self.rows = rows
        self.frame = tk.Frame(root)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self.frame, text="Manage records", font=("Segoe UI", 24)).pack()
        self.listbox = tk.Listbox(self.frame, height=5)
        self.listbox.pack()
        self.entry = tk.Entry(self.frame, relief="solid", bd=2)
        self.entry.pack()
        for text in buttons:
            tk.Button(self.frame, text=text).pack(side="left")
        self.screens = {"menu": self.frame, "admin": self.frame}

    def show(self, name):
        self.listbox.delete(0, "end")
        if name == "admin" and self.admin_unlocked:  # list filled only when unlocked
            for i in range(self.rows):
                self.listbox.insert("end", f"record {i}")


def create_app(root):
    return App(root, **OPTIONS)
'''
MANAGED_REQ = {"managed": [{"role": "Admin", "use_case": "Update Records"}]}


def managed(tmp_path, seeds=3, **options):
    runner = make(tmp_path, f"OPTIONS = {options!r}\n" + MANAGED)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "records.json").write_text(
        "[" + ",".join(f'{{"id": {i}}}' for i in range(seeds)) + "]")
    return runner


def test_probe_flags_empty_admin_list_when_seed_data_exists(tmp_path):
    ok, report = run_ui_probe(managed(tmp_path, rows=0), requirements=MANAGED_REQ)
    assert not ok and "shows no records although data/ holds 3 seed records" in report


def test_probe_flags_missing_edit_and_delete(tmp_path):
    ok, report = run_ui_probe(managed(tmp_path, buttons=("Add Record",)), requirements=MANAGED_REQ)
    assert not ok and "has no Edit, Delete button(s)" in report


def test_probe_accepts_full_admin_list_even_behind_an_unlock_flag(tmp_path):
    ok, report = run_ui_probe(managed(tmp_path / "a"), requirements=MANAGED_REQ)
    assert ok, report
    ok, report = run_ui_probe(managed(tmp_path / "b", locked=True), requirements=MANAGED_REQ)
    assert ok, report
