"""Main menu: Play, High Scores, Help, Admin, Exit."""
from __future__ import annotations

import tkinter as tk

from . import theme
from .widgets import SpaceCanvas, SpacePanel


class MenuScreen(tk.Frame):
    name = "menu"

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.panel = SpacePanel(self.canvas)
        self.panel.place(relx=0.5, rely=0.5, anchor="center")

        self.title = tk.Label(
            self.panel, text="Space Fractions", bg=theme.PANEL, fg=theme.YELLOW,
            font=theme.font(40, "bold"),
        )
        self.title.pack(pady=(30, 10))

        self.play_btn = theme.big_button(
            self.panel, "Play", command=self._play, bg=theme.CYAN, width=20,
        )
        self.play_btn.pack(pady=8)

        self.scores_btn = theme.big_button(
            self.panel, "High Scores", command=lambda: self.app.show("highscores"),
            bg=theme.GREEN, width=20,
        )
        self.scores_btn.pack(pady=8)

        self.help_btn = theme.big_button(
            self.panel, "Help", command=lambda: self.app.show("help"),
            bg=theme.PINK, width=20,
        )
        self.help_btn.pack(pady=8)

        self.admin_btn = theme.big_button(
            self.panel, "Admin", command=lambda: self.app.show("admin"),
            bg=theme.YELLOW, width=20,
        )
        self.admin_btn.pack(pady=8)

        self.exit_btn = theme.big_button(
            self.panel, "Exit", command=self._exit, bg=theme.RED, fg=theme.TEXT, width=20,
        )
        self.exit_btn.pack(pady=(8, 30))

    def refresh(self) -> None:
        self.canvas.draw_background()
        self.canvas.twinkle()

    def _play(self) -> None:
        self.app.show("name")

    def _exit(self) -> None:
        self.app.root.destroy()
