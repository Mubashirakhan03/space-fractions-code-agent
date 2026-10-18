"""Pause overlay: shown when the game is Paused; Resume returns to the question."""
from __future__ import annotations

import tkinter as tk

from . import theme
from .widgets import SpacePanel


class PauseScreen(tk.Frame):
    """A modal-style overlay over the question screen."""

    name = "pause"

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.dim = tk.Frame(self, bg=theme.BG)
        self.dim.pack(fill="both", expand=True)

        self.panel = SpacePanel(self)
        self.panel.place(relx=0.5, rely=0.5, anchor="center")

        self.title = tk.Label(
            self.panel, text="Paused", bg=theme.PANEL, fg=theme.YELLOW,
            font=theme.font(40, "bold"),
        )
        self.title.pack(pady=(30, 20))

        self.resume_btn = theme.big_button(
            self.panel, "Resume", command=self._resume, bg=theme.GREEN, width=16,
        )
        self.resume_btn.pack(pady=8)

        self.quit_btn = theme.big_button(
            self.panel, "Main Menu", command=self._menu, bg=theme.MUTED, width=16,
        )
        self.quit_btn.pack(pady=(8, 30))

    def refresh(self) -> None:
        pass

    def _resume(self) -> None:
        try:
            self.app.game.resume()
        except Exception:
            pass
        self.app.show("question")

    def _menu(self) -> None:
        # Abort the current game and go back to the menu.
        new_game = self.app.game
        if new_game is not None:
            try:
                new_game.game_over()
            except Exception:
                pass
        self.app.show("menu")
