"""Application shell: window, screens, navigation."""
from __future__ import annotations

import tkinter as tk

from app.controller import Controller
from questions.repository import QuestionRepository
from ui import theme
from ui.admin_screen import AdminScreen
from ui.help_screen import HelpScreen
from ui.intro_screen import IntroScreen
from ui.login_screen import LoginScreen
from ui.menu_screen import MenuScreen
from ui.pause_screen import PauseScreen
from ui.play_screen import PlayScreen
from ui.score_screen import ScoreScreen


DB_PATH = "space_fractions.db"
SEED_PATH = "data/seed_questions.json"


class App:
    """Owns the window, the controller and all screens."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.controller = Controller(QuestionRepository(DB_PATH, SEED_PATH))
        self.screens: dict = {}
        self._build_screens()
        self.show("intro")

    def _build_screens(self):
        self.screens = {
            "intro": IntroScreen(self.root, self),
            "login": LoginScreen(self.root, self),
            "menu": MenuScreen(self.root, self),
            "play": PlayScreen(self.root, self),
            "pause": PauseScreen(self.root, self),
            "score": ScoreScreen(self.root, self),
            "help": HelpScreen(self.root, self),
            "admin": AdminScreen(self.root, self),
        }

    def show(self, name):
        screen = self.screens.get(name)
        if screen is None:
            return
        self._current = name
        for s in self.screens.values():
            s.place_forget()
        screen.place(relx=0, rely=0, relwidth=1, relheight=1)
        screen.tkraise()
        screen.show()


def create_app(root: tk.Tk):
    """Build the application on ``root`` (does not call mainloop)."""
    root.title("Space Fractions")
    root.minsize(1100, 750)
    root.configure(bg=theme.BG)

    # Only maximize when a real window manager is present (not when the root
    # is withdrawn, e.g. in headless tests): calling state("zoomed") on a
    # withdrawn window corrupts the Tk window path.
    if root.state() != "withdrawn":
        try:
            root.state("zoomed")
        except tk.TclError:
            try:
                root.attributes("-zoomed", True)
            except tk.TclError:
                pass

    root.bind("<F11>", lambda e: _toggle_fullscreen(root))
    root.bind("<Escape>", lambda e: _leave_fullscreen(root))
    return App(root)


def _toggle_fullscreen(root):
    cur = root.attributes("-fullscreen")
    root.attributes("-fullscreen", not cur)


def _leave_fullscreen(root):
    root.attributes("-fullscreen", False)
