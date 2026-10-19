"""Pause screen."""
import tkinter as tk

from ui import theme
from ui.base_screen import BaseScreen


class PauseScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.title_label = tk.Label(
            self.body, text="Paused", font=theme.HEADING,
            fg=theme.ACCENT, bg=theme.BG,
        )
        self.title_label.pack(pady=(0, 24))
        self.resume_btn = self.make_button("Resume", self._resume)
        self.resume_btn.pack(pady=8)
        self.quit_btn = self.make_button("Quit to Menu", self._quit, primary=False)
        self.quit_btn.pack(pady=8)

    def _resume(self):
        game = self.app.controller.game
        if game is not None:
            try:
                game.resume()
            except Exception:
                pass
        self.app.show("play")
        self.app.screens["play"].resume_game()

    def _quit(self):
        self.app.controller.game = None
        self.app.show("menu")
