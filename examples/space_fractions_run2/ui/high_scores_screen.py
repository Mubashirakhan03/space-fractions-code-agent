"""High Scores screen (View Score use case) — top scores from SQLite."""
from __future__ import annotations

import sqlite3
import tkinter as tk

from . import theme
from .space_canvas import SpaceCanvas


class HighScoresScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self, text="🏆 High Scores", font=theme.SUBTITLE_FONT,
            bg=theme.BG, fg=theme.PRIMARY)
        self.title_label.place(relx=0.5, rely=0.1, anchor="center")

        self.scores_frame = tk.Frame(self, bg=theme.SURFACE)
        self.scores_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.7, relheight=0.7)

        self.back_button = tk.Button(
            self, text="← Menu", font=theme.BUTTON_FONT,
            bg=theme.SURFACE, fg=theme.TEXT, relief="flat", padx=20, pady=8,
            activebackground=theme.ACCENT_CYAN,
            command=lambda: app.show("menu"))
        self.back_button.place(relx=0.5, rely=0.9, anchor="center")
        self.back_button.bind("<Enter>", lambda e: self.back_button.config(bg=theme.ACCENT_CYAN, fg=theme.BG))
        self.back_button.bind("<Leave>", lambda e: self.back_button.config(bg=theme.SURFACE, fg=theme.TEXT))

        self.empty_label = tk.Label(
            self.scores_frame, text="No scores yet — play a game!",
            font=theme.BODY_FONT, bg=theme.SURFACE, fg=theme.TEXT_MUTED)

    def _load_scores(self):
        db = self.app.db_path
        rows = []
        try:
            conn = sqlite3.connect(db)
            conn.row_factory = sqlite3.Row
            try:
                rows = conn.execute(
                    "SELECT player_name, score, total, percentage, stars, played_at "
                    "FROM scores ORDER BY percentage DESC, played_at DESC LIMIT 10"
                ).fetchall()
            finally:
                conn.close()
        except sqlite3.Error:
            rows = []
        return rows

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        for w in self.scores_frame.winfo_children():
            w.destroy()
        rows = self._load_scores()
        if not rows:
            self.empty_label = tk.Label(
                self.scores_frame, text="No scores yet — play a game!",
                font=theme.BODY_FONT, bg=theme.SURFACE, fg=theme.TEXT_MUTED)
            self.empty_label.pack(expand=True)
            return
        for i, r in enumerate(rows):
            text = (f"{i + 1}. {r['player_name']}  —  {r['score']}/{r['total']} "
                    f"({r['percentage']}%)  {'★' * r['stars']}")
            lbl = tk.Label(self.scores_frame, text=text, font=theme.BODY_FONT,
                           bg=theme.SURFACE, fg=theme.TEXT if i else theme.PRIMARY)
            lbl.pack(pady=4)
