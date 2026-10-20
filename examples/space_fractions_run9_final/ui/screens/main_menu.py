"""Main menu screen."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.screens.base import BaseScreen


class MainMenuScreen(BaseScreen):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "main_menu")

        theme.make_label(self, "SPACE FRACTIONS", theme.TITLE_SIZE,
                         theme.ACCENT, "bold").pack(pady=(60, 10))
        theme.make_label(self, "Choose your mission:", theme.CONTENT_SIZE,
                         theme.MUTED).pack(pady=(0, 30))

        self.play_btn = theme.make_button(self, "▶  Play Game", self.start_game)
        self.play_btn.pack(pady=10)

        self.help_btn = theme.make_button(self, "❓  View Help", lambda: self.app.show("help_screen"))
        self.help_btn.pack(pady=10)

        self.score_btn = theme.make_button(self, "★  View Score", lambda: self.app.show("score_screen"))
        self.score_btn.pack(pady=10)

        self.admin_btn = theme.make_button(self, "🔒  Admin", lambda: self.app.show("pin_screen"),
                                           bg=theme.SURFACE)
        self.admin_btn.pack(pady=10)

    def start_game(self) -> None:
        self.app.start_round()
        self.app.show("question_screen")
