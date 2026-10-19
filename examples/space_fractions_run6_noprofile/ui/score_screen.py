"""Score / ending scene with factual feedback."""
import tkinter as tk

from ui import theme
from ui.base_screen import BaseScreen


class ScoreScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.title_label = tk.Label(
            self.body, text="Mission Complete", font=theme.HEADING,
            fg=theme.ACCENT, bg=theme.BG,
        )
        self.title_label.pack(pady=(0, 16))
        self.score_label = tk.Label(
            self.body, text="", font=theme.TITLE, fg=theme.TEXT, bg=theme.BG,
        )
        self.score_label.pack(pady=(0, 16))
        self.rating_label = tk.Label(
            self.body, text="", font=theme.BODY, fg=theme.TEXT_MUTED, bg=theme.BG,
            wraplength=800, justify="center",
        )
        self.rating_label.pack(pady=(0, 24))
        self.again_btn = self.make_button("Play Again", self._again)
        self.again_btn.pack(pady=8)
        self.menu_btn = self.make_button("Main Menu", self._menu, primary=False)
        self.menu_btn.pack(pady=8)

    def show(self):
        game = self.app.controller.game
        if game is None:
            score, total = 0, 0
        else:
            score, total = game.view_score(), game.total
        self.score_label.config(text=f"{score} / {total}")
        self.rating_label.config(text=_rating_message(score, total))

    def _again(self):
        self.app.show("play")

    def _menu(self):
        self.app.show("menu")


def _rating_message(score, total):
    if total == 0:
        return "No questions played yet."
    ratio = score / total
    if ratio == 1.0:
        return "Perfect! You answered every question correctly. Stellar work!"
    if ratio >= 0.75:
        return "Great job! You got most answers right."
    if ratio >= 0.5:
        return "Good effort — keep practising your fractions!"
    if ratio > 0:
        return "Keep trying! Review the help screen and play again."
    return "No correct answers this time. Check Help for tips and try again."
