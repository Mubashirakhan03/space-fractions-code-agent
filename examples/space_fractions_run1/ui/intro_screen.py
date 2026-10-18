"""Animated intro screen: rocket flying across moving stars + title + Skip."""
from __future__ import annotations

import tkinter as tk

from . import theme
from .widgets import SpaceCanvas


class IntroScreen(tk.Frame):
    name = "intro"

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app
        self._after_cb = None
        self._anim = None

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title = tk.Label(
            self.canvas, text="Space Fractions", bg=theme.BG, fg=theme.YELLOW,
            font=theme.font(44, "bold"),
        )
        self.canvas.create_window(550, 180, window=self.title)

        self.subtitle = tk.Label(
            self.canvas, text="Blast off and master fractions!",
            bg=theme.BG, fg=theme.CYAN, font=theme.font(22),
        )
        self.canvas.create_window(550, 260, window=self.subtitle)

        self.skip_btn = theme.big_button(
            self.canvas, "Skip", command=self._skip, bg=theme.PINK, size=18, pady=8,
        )
        self.canvas.create_window(1000, 60, window=self.skip_btn)

        # Rocket (drawn on canvas, animated)
        self._rocket_x = 100

    def refresh(self) -> None:
        self.canvas.draw_background()
        self.canvas.twinkle()
        self._rocket_x = 100
        self._animate()
        self._after_cb = self.after(6000, self._skip)

    def _animate(self) -> None:
        self._rocket_x += 8
        w = self.canvas.winfo_width() or 1100
        if self._rocket_x > w + 60:
            self._rocket_x = -60
        self.canvas.delete("rocket")
        x = self._rocket_x
        y = 500
        self.canvas.create_polygon(
            x, y, x + 12, y - 30, x + 24, y, fill="#FFFFFF", outline="", tags="rocket"
        )
        self.canvas.create_oval(
            x + 8, y - 10, x + 16, y + 2, fill=theme.CYAN, outline="", tags="rocket"
        )
        self.canvas.create_polygon(
            x + 8, y, x + 16, y, x + 12, y + 22, fill=theme.YELLOW, outline="",
            tags="rocket",
        )
        self._anim = self.after(30, self._animate)

    def _skip(self) -> None:
        self._cancel_pending()
        self.app.show("menu")

    def _cancel_pending(self) -> None:
        for cb in (self._after_cb, self._anim):
            if cb is not None:
                try:
                    self.after_cancel(cb)
                except tk.TclError:
                    pass
        self.canvas.stop()
