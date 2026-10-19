"""Application controller: screens dict, show(name), create_app(root)."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path

from game.controller import GameController
from questions.repository import QuestionRepository
from scores.repository import ScoreRepository
import ui.theme as theme

# import screens (they register nothing; app builds them explicitly)
from ui.screens import intro
from ui.screens import menu
from ui.screens import name_entry
from ui.screens import question as qscreen
from ui.screens import end as endscreen
from ui.screens import high_scores
from ui.screens import help as helpscreen
from ui.screens import admin as adminscreen


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "spacefractions.db"


class App:
    """Owns the root window, shared services, and the screen registry."""

    def __init__(self, root: tk.Tk):
        self.root = root
        root.minsize(1100, 750)
        root.configure(bg=theme.SPACE_BG)

        # centre the window
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"1100x750+{max(0, (sw - 1100)//2)}+{max(0, (sh - 750)//2)}")
        try:
            root.state("zoomed")
        except tk.TclError:
            root.attributes("-zoomed", True)

        # shared services
        self.question_repo = QuestionRepository(DB_PATH)
        seed = DATA_DIR / "questions.json"
        if seed.exists():
            self.question_repo.seed_from_file(seed)
        self.score_repo = ScoreRepository(DB_PATH)

        # session state
        self.current_user = ""
        self.controller: GameController | None = None

        self.screens: dict[str, tk.Frame] = {}
        self._build_screens()

        # global key bindings
        root.bind("<F11>", self._toggle_fullscreen)
        root.bind("<Escape>", self._exit_fullscreen)

    def _build_screens(self):
        factory = {
            "intro": intro.IntroScreen,
            "menu": menu.MenuScreen,
            "name_entry": name_entry.NameEntryScreen,
            "question": qscreen.QuestionScreen,
            "end": endscreen.EndScreen,
            "high_scores": high_scores.HighScoresScreen,
            "help": helpscreen.HelpScreen,
            "admin": adminscreen.AdminScreen,
        }
        for name, cls in factory.items():
            screen = cls(self.root, self)
            screen.place(x=0, y=0, relwidth=1, relheight=1)
            self.screens[name] = screen

    def show(self, name: str):
        screen = self.screens.get(name)
        if screen is None:
            return
        screen.refresh()
        screen.tkraise()
        screen.focus()

    def _toggle_fullscreen(self, event=None):
        state = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not state)

    def _exit_fullscreen(self, event=None):
        if self.root.attributes("-fullscreen"):
            self.root.attributes("-fullscreen", False)

    def start_game(self, username: str):
        self.current_user = username or "Astronaut"
        self.controller = GameController(self.question_repo.all())

    def record_score(self):
        if self.controller is None:
            return
        g = self.controller.game
        self.score_repo.save(
            self.current_user, g.score, g.total, round(g.percentage, 1)
        )


def create_app(root: tk.Tk) -> App:
    return App(root)


# keep imports referenced for linters
_ = (intro, menu, name_entry, qscreen, endscreen, high_scores, helpscreen, adminscreen)
