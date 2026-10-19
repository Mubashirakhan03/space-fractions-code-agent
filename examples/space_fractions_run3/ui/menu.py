"""Main menu: Play, High Scores, Help, Admin, Exit."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.base import BaseScreen


class MenuScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        panel = tk.Frame(self, bg=theme.SURFACE, padx=40, pady=40)
        panel.place(relx=0.5, rely=0.5, anchor="center")
        self.title_label = tk.Label(
            panel, text="SPACE FRACTIONS", font=self.theme.title(),
            bg=theme.SURFACE, fg=theme.PRIMARY,
        )
        self.title_label.pack(pady=(0, 30))
        self.play_button = self._make_button(panel, "▶  Play", lambda: self.app.show("name"))
        self.scores_button = self._make_button(panel, "🏆  High Scores", lambda: self.app.show("scores"))
        self.help_button = self._make_button(panel, "❓  Help", lambda: self.app.show("help"))
        self.admin_button = self._make_button(panel, "⚙  Admin", lambda: self.app.show("admin"))
        self.exit_button = self._make_button(panel, "✖  Exit", self.app.root.destroy)

    def _make_button(self, parent, text, command):
        b = tk.Button(
            parent, text=text, command=command, font=self.theme.button(),
            bg=theme.SURFACE_ALT, fg=theme.TEXT, relief="flat",
            activebackground=theme.ACCENT, activeforeground=theme.BG,
            width=22, padx=16, pady=12,
        )
        b.pack(pady=10)
        return b
