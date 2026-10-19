"""Application controller: builds every screen and switches between them.

Contract used by the harness: create_app(root) -> App; App.screens: dict[str, tk.Frame];
App.show(name). Never calls mainloop().
"""
import tkinter as tk
from pathlib import Path

from ui import theme
from store.database import Database
from game.service import GameService
from game.generator import FractionGenerator
from question.question import Question


class App:
    def __init__(self, root: tk.Tk, db_path: str = None):
        self.root = root
        root.title("Space Fractions")
        root.configure(bg=theme.BG)
        root.minsize(1100, 750)
        self._center(root)
        try:
            root.state("zoomed")
        except tk.TclError:
            try:
                root.attributes("-zoomed", True)
            except tk.TclError:
                pass
        self._fullscreen = False
        root.bind("<F11>", lambda e: self.toggle_fullscreen())
        root.bind("<Escape>", lambda e: self._leave_fullscreen())

        # data layer
        db_path = db_path or str(Path(__file__).resolve().parent.parent / "game.db")
        self.db = Database(db_path)
        self._load_seed()
        self.generator = FractionGenerator()
        self.service = GameService(self.db.all_questions(), self.generator)
        self.current_game = None
        self.admin_unlocked = False

        self.screens: dict[str, tk.Frame] = {}
        self._build_screens()
        self.show("intro")

    # ---------- window helpers ----------
    @staticmethod
    def _center(root):
        root.update_idletasks()
        w, h = 1280, 800
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        self.root.attributes("-fullscreen", self._fullscreen)

    def _leave_fullscreen(self):
        if self._fullscreen:
            self._fullscreen = False
            self.root.attributes("-fullscreen", False)

    # ---------- seed ----------
    def _load_seed(self):
        import json
        seed_path = Path(__file__).resolve().parent.parent / "data" / "seed_questions.json"
        if seed_path.exists():
            data = json.loads(seed_path.read_text(encoding="utf-8"))
            self.db.seed([Question.from_dict(d) for d in data])

    # ---------- screens ----------
    def _build_screens(self):
        from ui.intro_screen import IntroScreen
        from ui.menu_screen import MenuScreen
        from ui.play_screen import PlayScreen
        from ui.results_screen import ResultsScreen
        from ui.score_screen import ScoreScreen
        from ui.help_screen import HelpScreen
        from ui.pin_screen import PinScreen
        from ui.admin_screen import AdminScreen

        container = tk.Frame(self.root, bg=theme.BG)
        container.pack(fill="both", expand=True)
        self.container = container

        def add(name, cls):
            screen = cls(container, self)
            screen.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.screens[name] = screen

        add("intro", IntroScreen)
        add("menu", MenuScreen)
        add("play", PlayScreen)
        add("results", ResultsScreen)
        add("score", ScoreScreen)
        add("help", HelpScreen)
        add("pin", PinScreen)
        add("admin", AdminScreen)

    def show(self, name: str):
        if name not in self.screens:
            raise KeyError(f"Unknown screen: {name}")
        # lock the admin area when leaving it
        if name != "admin" and name != "pin":
            self.admin_unlocked = False
        screen = self.screens[name]
        screen.on_show()
        screen.tkraise()

    def get_pin(self) -> str:
        import json
        settings_path = Path(__file__).resolve().parent.parent / "data" / "settings.json"
        if settings_path.exists():
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            return data.get("admin_pin", "1234")
        return self.db.get_setting("admin_pin", "1234")


def create_app(root: tk.Tk, db_path: str = None) -> App:
    """Factory required by the harness. Builds everything, no mainloop()."""
    return App(root, db_path=db_path)
