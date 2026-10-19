"""Help screen (View Help use case)."""
from __future__ import annotations

import tkinter as tk

from . import theme
from .space_canvas import SpaceCanvas

HELP_TEXT = (
    "How to play Space Fractions\n\n"
    "• Answer 10 fraction questions per mission.\n"
    "• Question types: equivalent fractions, compare, add/subtract, simplify.\n"
    "• Some questions are multiple choice — click your answer.\n"
    "• Others are typed — type a fraction like 3/4 and press Enter.\n"
    "• Equivalent answers count (2/4 = 1/2).\n"
    "• Press Pause to take a break, then Resume.\n"
    "• Earn up to 3 stars based on your score!"
)


class HelpScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self, text="❓ Help", font=theme.SUBTITLE_FONT,
            bg=theme.BG, fg=theme.PRIMARY)
        self.title_label.place(relx=0.5, rely=0.1, anchor="center")

        self.help_label = tk.Label(
            self, text=HELP_TEXT, font=theme.BODY_FONT,
            bg=theme.SURFACE, fg=theme.TEXT, justify="left",
            wraplength=900, padx=40, pady=30)
        self.help_label.place(relx=0.5, rely=0.55, anchor="center")

        self.back_button = tk.Button(
            self, text="← Menu", font=theme.BUTTON_FONT,
            bg=theme.SURFACE, fg=theme.TEXT, relief="flat", padx=20, pady=8,
            activebackground=theme.ACCENT_CYAN,
            command=lambda: app.show("menu"))
        self.back_button.place(relx=0.5, rely=0.9, anchor="center")
        self.back_button.bind("<Enter>", lambda e: self.back_button.config(bg=theme.ACCENT_CYAN, fg=theme.BG))
        self.back_button.bind("<Leave>", lambda e: self.back_button.config(bg=theme.SURFACE, fg=theme.TEXT))
