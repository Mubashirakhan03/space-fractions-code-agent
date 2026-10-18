"""App controller: switches screens, owns repositories and app state."""
from __future__ import annotations

import tkinter as tk

from game.game import Game
from questions.repository import QuestionRepository
from users import ScoreRepository, User
from . import theme
from .intro_screen import IntroScreen
from .menu_screen import MenuScreen
from .name_screen import NameScreen
from .question_screen import QuestionScreen
from .pause_overlay import PauseScreen
from .end_screen import EndScreen
from .highscores_screen import HighScoresScreen
from .help_screen import HelpScreen
from .admin_screen import AdminScreen


class App:
    """Owns the root window, repositories, and screen switching."""

    DB_PATH = "data/spacefractions.db"

    def __init__(self, root: tk.Tk, db_path: str | None = None):
        self.root = root
        self.db_path = db_path or App.DB_PATH
        self.questions = QuestionRepository(self.db_path)
        self.scores = ScoreRepository(self.db_path)

        self.username: str = ""
        self.user: User | None = None
        self.game: Game | None = None
        self.round_questions: list = []
        self.current_index: int = 0

        self._screens = {}
        self._current = None

        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._leave_fullscreen)

    # ---- navigation ----
    def register(self, name: str, screen) -> None:
        self._screens[name] = screen

    def show(self, name: str) -> None:
        if self._current is not None:
            self._current.pack_forget()
        screen = self._screens[name]
        screen.refresh()
        screen.pack(fill="both", expand=True)
        self._current = screen

    # ---- fullscreen ----
    def _toggle_fullscreen(self, _event=None) -> None:
        state = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not state)

    def _leave_fullscreen(self, _event=None) -> None:
        self.root.attributes("-fullscreen", False)

    # ---- game flow helpers ----
    def start_round(self, count: int = 10) -> None:
        self.game = Game(game_id="round")
        self.round_questions = self.questions.sample(count)
        self.current_index = 0

    def next_question(self):
        if self.game is None or self.current_index >= len(self.round_questions):
            return None
        q = self.round_questions[self.current_index]
        self.current_index += 1
        return q

    def remaining(self) -> int:
        return max(0, len(self.round_questions) - self.current_index)

    def save_score(self) -> None:
        if not self.game or not self.username:
            return
        self.scores.add_score(
            self.username,
            self.game.score,
            self.game.total,
            self.game.percentage(),
            self.game.stars(),
        )


APP_FONT = theme.font


def create_app(root: tk.Tk, db_path: str | None = None) -> App:
    """Build the full application WITHOUT calling mainloop()."""
    root.title("Space Fractions")
    root.configure(bg=theme.BG)
    root.minsize(1100, 750)
    try:
        root.state("zoomed")
    except tk.TclError:
        try:
            root.attributes("-zoomed", True)
        except tk.TclError:
            pass

    app = App(root, db_path=db_path)

    screens = [
        IntroScreen(root, app),
        MenuScreen(root, app),
        NameScreen(root, app),
        QuestionScreen(root, app),
        PauseScreen(root, app),
        EndScreen(root, app),
        HighScoresScreen(root, app),
        HelpScreen(root, app),
        AdminScreen(root, app),
    ]
    for s in screens:
        app.register(s.name, s)

    app.show("intro")
    return app
