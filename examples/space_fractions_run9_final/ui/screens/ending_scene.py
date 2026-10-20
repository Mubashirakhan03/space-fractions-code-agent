"""Ending scene with feedback (result screen)."""
from __future__ import annotations

from ui import theme
from ui.screens.base import BaseScreen


class EndingSceneScreen(BaseScreen):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "ending_scene")
        self.title = theme.make_label(self, "Mission Complete", theme.TITLE_SIZE,
                                      theme.ACCENT, "bold")
        self.title.pack(pady=(50, 10))

        self.score_label = theme.make_label(self, "", theme.CONTENT_SIZE + 4,
                                            theme.TEXT, "bold")
        self.score_label.pack(pady=8)

        self.detail_label = theme.make_label(self, "", theme.FEEDBACK_SIZE, theme.MUTED)
        self.detail_label.pack(pady=4)

        self.message_label = theme.make_label(self, "", theme.FEEDBACK_SIZE,
                                              theme.TEXT, "bold")
        self.message_label.pack(pady=16)

        row = __import__("tkinter").Frame(self, bg=theme.BG)
        row.pack(pady=20)
        self.again_btn = theme.make_button(row, "▶  Play Again", self.play_again)
        self.again_btn.pack(side="left", padx=10)
        self.menu_btn = theme.make_button(row, "🏠  Main Menu", lambda: self.app.show("main_menu"),
                                          bg=theme.SURFACE)
        self.menu_btn.pack(side="left", padx=10)

    def on_show(self) -> None:
        rnd = self.app.service.current_round
        score = rnd.correct if rnd else 0
        total = rnd.total if rnd else 0
        wrong = rnd.wrong if rnd else 0

        self.score_label.config(text=f"Score: {score} / {total}")
        self.detail_label.config(text=f"Correct: {score}   ·   Wrong: {wrong}")
        self.message_label.config(text=self._message(score, total),
                                  fg=self._colour(score, total))

    def _message(self, score: int, total: int) -> str:
        if total == 0:
            return "No questions answered."
        ratio = score / total
        if ratio >= 0.8:
            return f"Outstanding! You are a fraction superstar! ⭐⭐⭐"
        if ratio >= 0.5:
            return f"Good work, space explorer! ⭐⭐"
        if ratio >= 0.25:
            return f"Getting there — keep practising! ⭐"
        return "Keep trying — every astronaut practises to reach the stars."

    def _colour(self, score: int, total: int) -> str:
        if total == 0:
            return theme.MUTED
        ratio = score / total
        if ratio >= 0.8:
            return theme.SUCCESS
        if ratio >= 0.25:
            return theme.ACCENT
        return theme.ERROR

    def play_again(self) -> None:
        self.app.start_round()
        self.app.show("question_screen")
