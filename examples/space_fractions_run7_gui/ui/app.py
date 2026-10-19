"""App controller: builds all screens, exposes screens dict + show()."""
from __future__ import annotations

import tkinter as tk
from typing import Dict

from game.service import GameService
from question.repository import QuestionRepository
from ui import theme


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Space Fractions")
        root.minsize(1100, 750)
        self.repo = QuestionRepository()
        self.service = GameService(pool=self.repo.list_all(), default_total=5)

        container = tk.Frame(root, bg=theme.BACKGROUND)
        container.pack(fill="both", expand=True)

        self.screens: Dict[str, tk.Frame] = {}
        self._build_screens(container)
        self.show("intro")

    def _build_screens(self, container):
        from ui.screens.intro_screen import IntroScreen
        from ui.screens.menu_screen import MenuScreen
        from ui.screens.game_screen import GameScreen
        from ui.screens.pause_screen import PauseScreen
        from ui.screens.results_screen import ResultsScreen
        from ui.screens.help_screen import HelpScreen
        from ui.screens.score_screen import ScoreScreen
        from ui.screens.admin_screen import AdminScreen

        self.screens["intro"] = IntroScreen(container, self)
        self.screens["menu"] = MenuScreen(container, self)
        self.screens["game"] = GameScreen(container, self)
        self.screens["pause"] = PauseScreen(container, self)
        self.screens["results"] = ResultsScreen(container, self)
        self.screens["help"] = HelpScreen(container, self)
        self.screens["score"] = ScoreScreen(container, self)
        self.screens["admin"] = AdminScreen(container, self)

    def show(self, name: str):
        for key, frame in self.screens.items():
            if key == name:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()
        screen = self.screens[name]
        screen.tkraise()
        begin = getattr(screen, "begin", None)
        if callable(begin):
            begin()

    def quit(self):
        self.repo.close()
        self.root.destroy()


def create_app(root: tk.Tk) -> App:
    """Build the application without calling mainloop()."""
    app = App(root)

    def toggle_fullscreen(_event=None):
        cur = root.attributes("-fullscreen")
        root.attributes("-fullscreen", not cur)

    def exit_fullscreen(_event=None):
        root.attributes("-fullscreen", False)

    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", exit_fullscreen)
    return app


__all__ = ["App", "create_app"]
