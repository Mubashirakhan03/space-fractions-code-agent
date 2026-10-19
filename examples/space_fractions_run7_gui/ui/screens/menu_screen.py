"""Main menu screen."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class MenuScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BACKGROUND)
        self.app = app

        title = tk.Label(self, text="Space Fractions", bg=theme.BACKGROUND,
                         fg=theme.ACCENT, font=theme.TITLE_FONT)
        title.pack(pady=(60, 10))
        sub = tk.Label(self, text="Main Menu", bg=theme.BACKGROUND,
                       fg=theme.MUTED, font=theme.SUBTITLE_FONT)
        sub.pack(pady=(0, 30))

        self.play_btn = self._btn("Play Game", self._play)
        self.score_btn = self._btn("View Score", lambda: self.app.show("score"))
        self.help_btn = self._btn("View Help", lambda: self.app.show("help"))
        self.admin_btn = self._btn("Admin: Update Questions",
                                   lambda: self.app.show("admin"))
        self.quit_btn = self._btn("Quit", self._quit, accent=True)

        for b in (self.play_btn, self.score_btn, self.help_btn,
                  self.admin_btn, self.quit_btn):
            b.pack(pady=8)

    def _btn(self, text, cmd, accent=False):
        b = tk.Button(self, text=text, command=cmd)
        theme.style_button(b)
        if accent:
            b.configure(bg=theme.SECONDARY, activebackground=theme.SECONDARY)
        return b

    def _play(self):
        self.app.show("game")

    def _quit(self):
        self.app.quit()


__all__ = ["MenuScreen"]
