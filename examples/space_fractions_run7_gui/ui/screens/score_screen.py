"""Score history screen (View Score use case)."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class ScoreScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BACKGROUND)
        self.app = app
        self.back_btn = tk.Button(self, text="Back to Menu",
                                  command=lambda: self.app.show("menu"))
        theme.style_button(self.back_btn)
        self.back_btn.pack(side="bottom", pady=12)

        self.title = tk.Label(self, text="Score History", bg=theme.BACKGROUND,
                              fg=theme.ACCENT, font=theme.SUBTITLE_FONT)
        self.title.pack(pady=(20, 8))
        self.body = tk.Text(self, bg=theme.SURFACE, fg=theme.TEXT,
                            font=theme.SMALL_FONT, relief="flat", bd=0,
                            padx=16, pady=10)
        self.body.pack(pady=8, fill="both", expand=True, padx=30)
        self.body.configure(state="disabled")

    def begin(self):
        scores = self.app.repo.list_scores()
        self.body.configure(state="normal")
        self.body.delete("1.0", "end")
        if not scores:
            self.body.insert("1.0", "No games played yet \u2014 play a mission!")
        else:
            for s in scores:
                self.body.insert(
                    "end",
                    f"{s['score']}/{s['total']}  \u2014  {s['played_at']}\n",
                )
        self.body.configure(state="disabled")


__all__ = ["ScoreScreen"]
