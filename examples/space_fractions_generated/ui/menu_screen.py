"""Main menu screen: Play, High Scores, Help, Admin, Exit."""
from __future__ import annotations

import tkinter as tk

from . import theme
from .space_canvas import SpaceCanvas


class MenuScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self, text="Space Fractions", font=theme.TITLE_FONT,
            bg=theme.BG, fg=theme.PRIMARY)
        self.title_label.place(relx=0.5, rely=0.18, anchor="center")

        self.play_button = self._make_button("🚀 Play", 0.34, lambda: app.show("name"))
        self.scores_button = self._make_button("🏆 High Scores", 0.44, lambda: app.show("high_scores"))
        self.help_button = self._make_button("❓ Help", 0.54, lambda: app.show("help"))
        self.admin_button = self._make_button("⚙️ Admin", 0.64, lambda: app.show("admin"))
        self.exit_button = self._make_button("Exit", 0.74, self.app.root.destroy)

    def _make_button(self, text, rely, command):
        btn = tk.Button(
            self, text=text, font=theme.BUTTON_FONT,
            bg=theme.SURFACE, fg=theme.TEXT,
            activebackground=theme.PRIMARY, activeforeground=theme.BG,
            relief="flat", width=20, pady=10, command=command)
        btn.place(relx=0.5, rely=rely, anchor="center")
        btn.bind("<Enter>", lambda e: btn.config(bg=theme.PRIMARY, fg=theme.BG))
        btn.bind("<Leave>", lambda e: btn.config(bg=theme.SURFACE, fg=theme.TEXT))
        return btn
