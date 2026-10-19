"""Ending scene with feedback driven by the real result."""
import tkinter as tk

from ui import theme
from ui.base_screen import make_button, title_label


class ResultsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.title = title_label(self, "Mission Complete!", 34)
        self.title.pack(pady=(40, 10))

        self.score_label = tk.Label(self, text="", bg=theme.BG, fg=theme.TEXT,
                                    font=theme.title_font(28))
        self.score_label.pack()
        self.rating_label = tk.Label(self, text="", bg=theme.BG, fg=theme.ACCENT,
                                     font=theme.body_font(24), wraplength=1000)
        self.rating_label.pack(pady=10)

        self.review = tk.Frame(self, bg=theme.BG)
        self.review.pack(expand=True, fill="both", padx=20, pady=10)

        bottom = tk.Frame(self, bg=theme.BG)
        bottom.pack(fill="x", padx=20, pady=20)
        self.again_btn = make_button(bottom, "Play Again", self._again)
        self.again_btn.pack(side="left")
        self.menu_btn = make_button(bottom, "Menu", lambda: app.show("menu"))
        self.menu_btn.pack(side="right")

    def on_show(self):
        game = self.app.current_game
        if game is None:
            self.score_label.config(text="Score: 0 / 0")
            self.rating_label.config(text="No game played yet. Start from the menu!")
            self._clear_review()
            return
        self.score_label.config(text=f"Score: {game.score} / {game.total}")
        self.rating_label.config(text=game.rating())
        self._render_review(game)

    def _clear_review(self):
        for w in self.review.winfo_children():
            w.destroy()

    def _render_review(self, game):
        self._clear_review()
        for q, correct in game.reviewed_questions():
            mark = "✔" if correct else "✘"
            color = theme.SUCCESS if correct else theme.ERROR
            line = tk.Label(self.review, text=f"{mark}  {q.prompt}  →  {q.correct_answer}",
                            bg=theme.BG, fg=color, font=theme.body_font(16),
                            anchor="w", wraplength=1000)
            line.pack(fill="x", pady=2)

    def _again(self):
        self.app.current_game = self.app.service.build_round()
        self.app.show("play")
