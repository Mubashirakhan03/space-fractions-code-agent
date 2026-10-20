"""Application controller: builds all screens and switches between them."""
from __future__ import annotations

import random
from pathlib import Path
import tkinter as tk

from ui import theme
from ui.screens.intro_movie import IntroMovieScreen
from ui.screens.main_menu import MainMenuScreen
from ui.screens.question_screen import QuestionScreen
from ui.screens.ending_scene import EndingSceneScreen
from ui.screens.help_screen import HelpScreen
from ui.screens.score_screen import ScoreScreen
from ui.screens.pin_screen import PinScreen
from ui.screens.admin_screen import AdminScreen
from store.store import QuestionStore
from admin.admin import QuestionRepository
from admin.settings import Settings
from game.game import GameService

APP_NAME = "Space Fractions"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class App:
    def __init__(self, root: tk.Tk, data_dir: Path = DATA_DIR,
                 seed_json: str = None, rng_seed: int = None) -> None:
        self.root = root
        self.data_dir = Path(data_dir)
        db_path = self.data_dir / "space_fractions.db"
        seed_path = self.data_dir / "questions_seed.json"
        self.store = QuestionStore(db_path, seed_path=seed_path, seed_json=seed_json)
        self.repository = QuestionRepository(self.store)
        self.settings = Settings(self.data_dir / "settings.json")
        self.settings.load()
        self.rng = random.Random(rng_seed)
        self.service = GameService(self.repository.list_all(), self.rng)

        self.screens = {}
        self._build_screens()
        self._bind_keys()
        self.current = None

    def _build_screens(self) -> None:
        self.screens = {
            "intro_movie": IntroMovieScreen(self.root, self),
            "main_menu": MainMenuScreen(self.root, self),
            "question_screen": QuestionScreen(self.root, self),
            "ending_scene": EndingSceneScreen(self.root, self),
            "help_screen": HelpScreen(self.root, self),
            "score_screen": ScoreScreen(self.root, self),
            "pin_screen": PinScreen(self.root, self),
            "admin_screen": AdminScreen(self.root, self),
        }

    def _bind_keys(self) -> None:
        self.root.bind("<F11>", lambda _e: self._toggle_fullscreen())
        self.root.bind("<Escape>", lambda _e: self._leave_fullscreen())

    def _toggle_fullscreen(self) -> None:
        state = bool(self.root.attributes("-fullscreen"))
        self.root.attributes("-fullscreen", not state)

    def _leave_fullscreen(self) -> None:
        self.root.attributes("-fullscreen", False)

    def show(self, name: str) -> None:
        if self.current is not None:
            self.current.on_hide()
            self.current.pack_forget()
        screen = self.screens[name]
        screen.pack(fill="both", expand=True)
        screen.on_show()
        self.current = screen

    def start_round(self) -> None:
        # reload the pool so admin additions are included
        self.service.pool = self.repository.list_all()
        self.service.play(question_count=10)

    def finish_round(self) -> None:
        self.service.finish_round()

    def start(self) -> None:
        self.show("intro_movie")


def create_app(root: tk.Tk, data_dir: Path = None, seed_json: str = None,
               rng_seed: int = None) -> App:
    """Build the whole app WITHOUT calling mainloop()."""
    root.title(APP_NAME)
    root.minsize(1100, 750)
    root.configure(bg=theme.BG)
    _center_and_maximise(root)
    app = App(root, data_dir=data_dir or DATA_DIR, seed_json=seed_json,
              rng_seed=rng_seed)
    app.start()
    return app


def _center_and_maximise(root: tk.Tk) -> None:
    root.update_idletasks()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    x = max(0, (w - 1100) // 2)
    y = max(0, (h - 750) // 2)
    root.geometry(f"1100x750+{x}+{y}")
    try:
        root.state("zoomed")
    except tk.TclError:
        try:
            root.attributes("-zoomed", True)
        except tk.TclError:
            pass
