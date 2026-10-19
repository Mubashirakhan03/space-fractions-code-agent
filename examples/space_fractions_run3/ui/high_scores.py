"""High Scores screen (View Score use case): top scores from SQLite."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.base import BaseScreen


class HighScoresScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        panel = tk.Frame(self, bg=theme.SURFACE, padx=40, pady=24)
        panel.place(relx=0.5, rely=0.5, anchor="center")
        self.title_label = tk.Label(
            panel, text="🏆 High Scores", font=self.theme.title(),
            bg=theme.SURFACE, fg=theme.PRIMARY,
        )
        self.title_label.pack(pady=(0, 12))
        text_frame = tk.Frame(panel, bg=theme.SURFACE)
        text_frame.pack(pady=6)
        scroll = tk.Scrollbar(text_frame, orient="vertical")
        self.scores_text = tk.Text(
            text_frame, height=10, width=46, font=self.theme.body(),
            bg=theme.SURFACE_ALT, fg=theme.TEXT, relief="flat",
            wrap="word", yscrollcommand=scroll.set,
        )
        scroll.config(command=self.scores_text.yview)
        scroll.pack(side="right", fill="y")
        self.scores_text.pack(side="left")
        self.scores_text.config(state="disabled")
        self.menu_button = tk.Button(
            panel, text="🏠 Main Menu", command=lambda: self.app.show("menu"),
            font=self.theme.button(), bg=theme.PRIMARY, fg=theme.BG,
            activebackground=theme.ACCENT, relief="flat", padx=30, pady=10,
        )
        self.menu_button.pack(pady=14)

    def on_show(self):
        rows = self.app.score_repo.top_scores(10)
        self.scores_text.config(state="normal")
        self.scores_text.delete("1.0", "end")
        if not rows:
            self.scores_text.insert("end", "No scores yet — be the first to play! 🚀")
        else:
            for i, (name, score, total, pct, stars, played_at) in enumerate(rows, 1):
                self.scores_text.insert(
                    "end",
                    f"{i:>2}. {name:<16} {score:>4} pts  {pct:>5.1f}%  "
                    f"{'★'*stars}{'☆'*(3-stars)}  ({played_at[:10]})\n",
                )
        self.scores_text.config(state="disabled")
