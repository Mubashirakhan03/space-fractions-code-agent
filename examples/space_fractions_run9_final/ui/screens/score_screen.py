"""Score screen (View Score use case)."""
from __future__ import annotations

from ui import theme
from ui.screens.base import BaseScreen


class ScoreScreen(BaseScreen):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "score_screen")
        theme.make_label(self, "Your Scores", theme.TITLE_SIZE, theme.ACCENT,
                         "bold").pack(pady=(40, 16))

        self.best_label = theme.make_label(self, "", theme.CONTENT_SIZE + 4,
                                           theme.SUCCESS, "bold")
        self.best_label.pack(pady=8)
        self.last_label = theme.make_label(self, "", theme.FEEDBACK_SIZE, theme.MUTED)
        self.last_label.pack(pady=8)

        self.back_btn = theme.make_button(self, "⬅  Back to Menu",
                                          lambda: self.app.show("main_menu"))
        self.back_btn.pack(pady=20)

    def on_show(self) -> None:
        best = self.app.service.high_score
        rnd = self.app.service.current_round
        last = rnd.correct if rnd else 0
        self.best_label.config(text=f"★ Best score: {best}")
        self.last_label.config(text=f"Last round score: {last}")
