"""Pause screen (Paused state)."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class PauseScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BACKGROUND)
        self.app = app
        self.title = tk.Label(self, text="Paused", bg=theme.BACKGROUND,
                              fg=theme.ACCENT, font=theme.TITLE_FONT)
        self.title.pack(pady=(80, 20))
        self.resume_btn = tk.Button(self, text="\u25b6 Resume", command=self._resume)
        theme.style_button(self.resume_btn)
        self.resume_btn.pack(pady=10)
        self.menu_btn = tk.Button(self, text="Main Menu", command=self._menu)
        theme.style_button(self.menu_btn)
        self.menu_btn.pack(pady=10)

    def _resume(self):
        self.app.service.resume()
        self.app.show("game")

    def _menu(self):
        self.app.show("menu")


__all__ = ["PauseScreen"]
