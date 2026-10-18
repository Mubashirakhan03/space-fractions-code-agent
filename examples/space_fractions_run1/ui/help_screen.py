"""Help screen (View Help use case)."""
from __future__ import annotations

import tkinter as tk

from . import theme
from .widgets import SpaceCanvas, SpacePanel


HELP_TEXT = (
    "Welcome to Space Fractions!\n\n"
    "• Answer fraction questions to earn points.\n"
    "• Types: equivalent fractions, comparing, adding/subtracting, and simplifying.\n"
    "• Equivalent answers count (2/4 is the same as 1/2).\n"
    "• Type your answer like 1/2, or pick a multiple-choice option.\n"
    "• Earn 1-3 stars based on your final percentage.\n\n"
    "Use the Pause button to take a break, then Resume.\n"
    "Blast off and have fun! 🚀"
)


class HelpScreen(tk.Frame):
    name = "help"

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title = tk.Label(
            self.canvas, text="Help", bg=theme.BG, fg=theme.YELLOW,
            font=theme.font(36, "bold"),
        )
        self.canvas.create_window(550, 80, window=self.title)

        self.panel = SpacePanel(self.canvas)
        self.panel.place(relx=0.5, rely=0.5, anchor="center")

        self.body = tk.Label(
            self.panel, text=HELP_TEXT, bg=theme.PANEL, fg=theme.TEXT,
            font=theme.font(18), justify="left",
        )
        self.body.pack(padx=30, pady=30)

        self.back_btn = theme.big_button(
            self.canvas, "Back", command=lambda: self.app.show("menu"),
            bg=theme.MUTED, width=12,
        )
        self.canvas.create_window(550, 660, window=self.back_btn)

    def refresh(self) -> None:
        self.canvas.draw_background()
        self.canvas.twinkle()
