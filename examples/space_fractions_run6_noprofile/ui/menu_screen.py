"""Main menu."""
import tkinter as tk

from ui import theme
from ui.base_screen import BaseScreen


class MenuScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.title_label = tk.Label(
            self.body, text="Mission Control", font=theme.HEADING,
            fg=theme.ACCENT, bg=theme.BG,
        )
        self.title_label.pack(pady=(0, 24))
        self.play_btn = self.make_button("Play Game", self._play)
        self.play_btn.pack(pady=8)
        self.score_btn = self.make_button("View Score", self._score, primary=False)
        self.score_btn.pack(pady=8)
        self.help_btn = self.make_button("View Help", self._help, primary=False)
        self.help_btn.pack(pady=8)
        self.admin_btn = self.make_button("Update Questions", self._admin, primary=False)
        self.admin_btn.pack(pady=8)

    def show(self):
        if self.app.controller.is_admin:
            self.admin_btn.config(state="normal")
        else:
            self.admin_btn.config(state="disabled")

    def _play(self):
        self.app.show("play")

    def _score(self):
        self.app.show("score")

    def _help(self):
        self.app.show("help")

    def _admin(self):
        self.app.show("admin")
