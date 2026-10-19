"""The main menu."""
from __future__ import annotations

import tkinter as tk

import ui.theme as theme
from ui.screens.base import BaseScreen, make_button


class MenuScreen(BaseScreen):
    def _build(self):
        self.title = tk.Label(
            self.content, text="Space Fractions", font=theme.TITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.ACCENT_YELLOW,
        )
        self.title.pack(pady=(0, 30))

        self.play_btn = make_button(self.content, "Play", self._play)
        self.play_btn.pack(fill="x", pady=8)
        self.scores_btn = make_button(self.content, "High Scores", self._scores,
                                      bg=theme.ACCENT_GREEN)
        self.scores_btn.pack(fill="x", pady=8)
        self.help_btn = make_button(self.content, "Help", self._help,
                                    bg=theme.ACCENT_CYAN)
        self.help_btn.pack(fill="x", pady=8)
        self.admin_btn = make_button(self.content, "Admin", self._admin,
                                     bg=theme.ACCENT_PINK)
        self.admin_btn.pack(fill="x", pady=8)
        self.exit_btn = make_button(self.content, "Exit", self._exit,
                                    bg=theme.ERROR)
        self.exit_btn.pack(fill="x", pady=8)

    def _play(self):
        self.app.show("name_entry")

    def _scores(self):
        self.app.show("high_scores")

    def _help(self):
        self.app.show("help")

    def _admin(self):
        self.app.show("admin")

    def _exit(self):
        self.app.root.destroy()

    def focus(self):
        self.play_btn.focus_set()
