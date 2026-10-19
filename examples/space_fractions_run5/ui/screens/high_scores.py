"""High Scores screen (View Score use case)."""
from __future__ import annotations

import tkinter as tk

import ui.theme as theme
from ui.screens.base import BaseScreen, make_button


class HighScoresScreen(BaseScreen):
    def _build(self):
        self.tk_title = tk.Label(
            self.content, text="High Scores", font=theme.TITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.ACCENT_YELLOW,
        )
        self.tk_title.pack(pady=(0, 20))

        self.list_frame = tk.Frame(self.content, bg=theme.SPACE_BG)
        self.list_frame.pack(pady=(0, 20))

        self.back_btn = make_button(self.content, "Back to menu", self._back,
                                    bg=theme.PRIMARY)
        self.back_btn.pack()

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        rows = self.app.score_repo.top(10)
        if not rows:
            tk.Label(self.list_frame, text="No scores yet — go play!",
                     font=theme.BODY_FONT, bg=theme.SPACE_BG,
                     fg=theme.MUTED_TEXT).pack(pady=10)
            return
        tk.Label(self.list_frame, text=f"{'Name':<20}{'Score':>8}{'%':>8}",
                 font=theme.BODY_FONT, bg=theme.SPACE_BG,
                 fg=theme.MUTED_TEXT).pack(anchor="w")
        for username, score, total, pct in rows:
            tk.Label(
                self.list_frame,
                text=f"{username:<20}{score:>6}/{total:<3}{pct:>7.0f}%",
                font=theme.BODY_FONT, bg=theme.SPACE_BG, fg=theme.TEXT,
            ).pack(anchor="w", pady=2)

    def _back(self):
        self.app.show("menu")
