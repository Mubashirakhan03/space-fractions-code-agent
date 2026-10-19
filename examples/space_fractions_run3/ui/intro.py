"""Introductory movie: animated rocket flying across twinkling stars, Skip button,
auto-advance to the menu."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.base import BaseScreen


class IntroScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.title_label = tk.Label(
            self.canvas, text="SPACE FRACTIONS",
            font=self.theme.title(), fg=theme.PRIMARY, bg=theme.BG,
        )
        self.subtitle = tk.Label(
            self.canvas,
            text="Blast off on a fractions adventure! 🚀",
            font=self.theme.body(), fg=theme.TEXT_MUTED, bg=theme.BG,
        )
        self.skip_button = tk.Button(
            self.canvas, text="Skip ▶", command=self._skip,
            font=self.theme.button(), bg=theme.SURFACE, fg=theme.TEXT,
            activebackground=theme.SURFACE_ALT, activeforeground=theme.TEXT,
            relief="flat", padx=24, pady=8,
        )
        self._rocket_x = -0.2  # fraction of width
        self._animating = True
        self._advance_id = None

    def on_show(self):
        self._animating = True
        self._rocket_x = -0.2
        self._place_widgets()
        self._animate()
        if self._advance_id:
            self.after_cancel(self._advance_id)
        self._advance_id = self.after(6000, self._skip)

    def _place_widgets(self):
        w = max(self.canvas.winfo_width(), 400)
        h = max(self.canvas.winfo_height(), 300)
        self.title_label.place(relx=0.5, rely=0.3, anchor="center")
        self.subtitle.place(relx=0.5, rely=0.42, anchor="center")
        self.skip_button.place(relx=0.95, rely=0.9, anchor="se")

    def _animate(self):
        if not self._animating:
            return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w > 1 and h > 1:
            self.canvas.delete("rocket")
            self._rocket_x += 0.01
            if self._rocket_x > 1.2:
                self._rocket_x = -0.2
            x = self._rocket_x * w
            y = h * 0.55
            self.canvas.create_text(
                x, y, text="🚀", font=(self.theme.family, 48), tags="rocket",
            )
        self.after(40, self._animate)

    def _skip(self):
        self._animating = False
        if self._advance_id:
            self.after_cancel(self._advance_id)
            self._advance_id = None
        self.app.show("menu")
