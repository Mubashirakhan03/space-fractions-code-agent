"""Results / ending scene screen: calibrated feedback, no praise for zero."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class ResultsScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BACKGROUND)
        self.app = app
        self.title = tk.Label(self, text="Mission Complete!", bg=theme.BACKGROUND,
                              fg=theme.ACCENT, font=theme.TITLE_FONT)
        self.title.pack(pady=(60, 20))
        self.score_label = tk.Label(self, text="", bg=theme.BACKGROUND,
                                    fg=theme.TEXT, font=theme.CONTENT_FONT)
        self.score_label.pack(pady=10)
        self.rating_label = tk.Label(self, text="", bg=theme.BACKGROUND,
                                     fg=theme.MUTED, font=theme.SUBTITLE_FONT,
                                     wraplength=1000, justify="center")
        self.rating_label.pack(pady=20)
        self.play_again_btn = tk.Button(self, text="Play Again", command=self._again)
        theme.style_button(self.play_again_btn)
        self.play_again_btn.pack(pady=10)
        self.menu_btn = tk.Button(self, text="Main Menu", command=self._menu)
        theme.style_button(self.menu_btn)
        self.menu_btn.pack(pady=10)

    def begin(self):
        service = self.app.service
        game = service.game
        if game is None:
            score, total = 0, 0
        else:
            score = service.view_score()
            total = game.total
        self.score_label.configure(text=f"Score: {score} / {total}")
        if total == 0:
            rating = "No questions answered yet."
        elif score == 0:
            rating = "Let's practice more \u2014 you'll get there!"
        elif score == total:
            rating = "\u2b50 \u2b50 \u2b50 Perfect score! You're a star astronaut!"
        elif score >= total * 0.7:
            rating = "\u2b50 \u2b50 Great job \u2014 keep exploring!"
        elif score >= total * 0.4:
            rating = "\u2b50 Good progress, space cadet!"
        else:
            rating = "Keep practising \u2014 every mission helps you improve."
        self.rating_label.configure(text=rating)
        self.app.repo.record_score("Player", score, total)

    def _again(self):
        self.app.show("game")

    def _menu(self):
        self.app.show("menu")


__all__ = ["ResultsScreen"]
