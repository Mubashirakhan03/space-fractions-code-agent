"""Application controller: builds the app, holds shared state, switches screens.

Contract (used by the harness): ``ui/app.py`` defines ``create_app(root) -> App``.
The ``App`` exposes ``screens: dict[str, tk.Frame]`` and ``show(name)``.
"""
import sqlite3
import tkinter as tk
from pathlib import Path

from game.game import Game, ROUND_SIZE
from game.state import GameState
from questions.repository import QuestionRepository
from users.user import User
from admin.admin import Admin
import ui.theme as theme
from ui.space_background import SpaceBackground
from ui.screens import (
    IntroScreen, MenuScreen, NameScreen, QuestionScreen, ScoresScreen,
    HelpScreen, AdminScreen, EndScreen,
)

SCREEN_ORDER = ["intro", "menu", "name", "question", "scores", "help",
                "admin", "end"]


class App:
    def __init__(self, root, db_path=None):
        self.root = root
        self.round_size = ROUND_SIZE
        root.minsize(1100, 750)
        theme.init_fonts()

        # --- shared state ---------------------------------------------------
        self.repository = QuestionRepository()
        self.admin = Admin(id="a1", username="admin", repository=self.repository)
        self.player_name = ""
        self.game = None
        self.db_path = Path(db_path) if db_path else self._default_db_path()
        self._ensure_schema()

        # --- background canvas ---------------------------------------------
        self.background = SpaceBackground(root)
        self.background.pack(fill="both", expand=True)
        self.background.bind("<Configure>", self.background._draw)

        # --- screens --------------------------------------------------------
        self.screens = {}
        for name in SCREEN_ORDER:
            screen = self._build_screen(name)
            screen.place(in_=self.background, relx=0, rely=0,
                         relwidth=1, relheight=1)
            self.screens[name] = screen

        self._current = None
        self._bound_keys = False
        self._bind_global_keys()
        self.show("intro")

    # ------------------------------------------------------------------ build
    def _build_screen(self, name):
        cls = {
            "intro": IntroScreen,
            "menu": MenuScreen,
            "name": NameScreen,
            "question": QuestionScreen,
            "scores": ScoresScreen,
            "help": HelpScreen,
            "admin": AdminScreen,
            "end": EndScreen,
        }[name]
        return cls(self.background, self)

    def _default_db_path(self):
        home = Path.home()
        return home / ".space_fractions" / "spacefractions.db"

    # ------------------------------------------------------------------- keys
    def _bind_global_keys(self):
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._leave_fullscreen)

    def _toggle_fullscreen(self, event=None):
        try:
            self.root.attributes("-fullscreen", True)
        except tk.TclError:
            pass

    def _leave_fullscreen(self, event=None):
        try:
            self.root.attributes("-fullscreen", False)
        except tk.TclError:
            pass

    # ------------------------------------------------------------------- show
    def show(self, name):
        if name not in self.screens:
            raise KeyError(f"Unknown screen: {name}")
        for n, s in self.screens.items():
            if n == name:
                s.lift()
                s.on_show()
            else:
                s.lower()
        self._current = name

    # ---------------------------------------------------------------- flow
    def start_game(self):
        questions = self.repository.sample(self.round_size)
        self.game = Game(id="g1", questions=questions)
        self.game.play()
        self.show("question")

    def finish_game(self):
        if self.game is None:
            self.show("menu")
            return
        res = self.game.result()
        self._save_score(res)
        self.show("end")

    # ------------------------------------------------------------ persistence
    def _ensure_schema(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.executescript(self._schema_sql())
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _schema_sql():
        schema = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
        return schema.read_text(encoding="utf-8")

    def _save_score(self, res):
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(
                "INSERT INTO scores (username, score, total, percentage, stars)"
                " VALUES (?, ?, ?, ?, ?)",
                (self.player_name, res.score, res.total, res.percentage, res.stars),
            )
            conn.commit()
        finally:
            conn.close()

    def get_high_scores(self):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cur = conn.execute(
                "SELECT username, score, percentage, stars FROM scores"
                " ORDER BY percentage DESC, played_at DESC LIMIT 20")
            rows = cur.fetchall()
            conn.close()
            return rows
        except sqlite3.Error:
            return []


def create_app(root: tk.Tk, db_path=None) -> App:
    """Build the whole app WITHOUT calling mainloop()."""
    return App(root, db_path=db_path)
