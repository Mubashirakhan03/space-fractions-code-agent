"""High Scores screen (View Score use case)."""
from __future__ import annotations

import tkinter as tk

from . import theme
from .widgets import SpaceCanvas, SpacePanel


class HighScoresScreen(tk.Frame):
    name = "highscores"

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.panel = SpacePanel(self.canvas)
        self.panel.place(relx=0.5, rely=0.55, anchor="center")

        self.title = tk.Label(
            self.canvas, text="High Scores", bg=theme.BG, fg=theme.YELLOW,
            font=theme.font(36, "bold"),
        )
        self.canvas.create_window(550, 80, window=self.title)

        self.list_label = tk.Label(
            self.panel, text="", bg=theme.PANEL, fg=theme.TEXT,
            font=theme.font(20), justify="center",
        )
        self.list_label.pack(pady=20)

        self.back_btn = theme.big_button(
            self.canvas, "Back", command=lambda: self.app.show("menu"),
            bg=theme.MUTED, width=12,
        )
        self.canvas.create_window(550, 680, window=self.back_btn)

    def refresh(self) -> None:
        self.canvas.draw_background()
        self.canvas.twinkle()
        rows = self.app.scores.high_scores(10)
        if not rows:
            self.list_label.configure(text="No scores yet — play a game!")
            return
        lines = []
        for i, r in enumerate(rows, 1):
            pct = f"{r['percentage']:.0f}%"
            stars = "★" * r["stars"]
            lines.append(
                f"{i:>2}. {r['username']:<18}  {r['score']}/{r['total']}  {pct}  {stars}"
            )
        self.list_label.configure(text="\n".join(lines))
