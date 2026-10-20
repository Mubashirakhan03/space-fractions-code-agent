"""Introductory movie: a 5-10s Canvas animation with moving objects."""
from __future__ import annotations

import math
import random
import tkinter as tk

from ui import theme
from ui.screens.base import BaseScreen

DURATION_MS = 8000  # 8 seconds


class IntroMovieScreen(BaseScreen):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "intro_movie")
        self._after_ids = []
        self._start_time = None

        title = theme.make_label(self, "SPACE FRACTIONS", theme.TITLE_SIZE,
                                 theme.ACCENT, "bold")
        title.pack(pady=(20, 8))
        sub = theme.make_label(self, "An adventure with fractions among the stars",
                               theme.FEEDBACK_SIZE, theme.MUTED)
        sub.pack()

        self.canvas = tk.Canvas(self, bg=theme.BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=10)

        self.skip_btn = theme.make_button(self, "Skip ▶", self.skip)
        self.skip_btn.pack(pady=(0, 20))

        self.canvas.bind("<Configure>", self._draw_static)

    def _draw_static(self, event=None) -> None:
        c = self.canvas
        c.delete("stars", "static")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            return
        # background stars
        rng = random.Random(7)
        for _ in range(80):
            x = rng.randint(0, max(w, 1))
            y = rng.randint(0, max(h, 1))
            c.create_oval(x, y, x + 2, y + 2, fill=theme.TEXT, tags="stars", outline="")

    def on_show(self) -> None:
        self._start_time = None
        self._create_movers()
        self._step()

    def on_hide(self) -> None:
        self._cancel()

    def _cancel(self) -> None:
        for aid in self._after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        self._after_ids = []

    def _create_movers(self) -> None:
        c = self.canvas
        c.delete("mover")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10:
            w, h = 1000, 400
        # rocket
        self.rocket = c.create_oval(0, 0, 60, 30, fill=theme.ACCENT, outline="", tags="mover")
        # two planets
        self.planet1 = c.create_oval(0, 0, 80, 80, fill=theme.PRIMARY, outline="", tags="mover")
        self.planet2 = c.create_oval(0, 0, 90, 90, fill=theme.ACCENT_2, outline="", tags="mover")
        # three fraction stars (text that will move)
        self.star_labels = []
        for label in ("1/2", "3/4", "2/3"):
            self.star_labels.append(
                c.create_text(0, 0, text=label, fill=theme.SUCCESS,
                              font=theme.font(26, "bold"), tags="mover")
            )

    def _step(self) -> None:
        self._after_ids.append(self.after(33, self._tick))

    def _tick(self) -> None:
        c = self.canvas
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            self._step()
            return
        now = self._now_ms()
        if self._start_time is None:
            self._start_time = now
        t = now - self._start_time
        progress = t / DURATION_MS

        # rocket flies left -> right across the top third
        rx = progress * (w + 60) - 60
        ry = h * 0.22 + math.sin(progress * 12) * 14
        c.coords(self.rocket, rx, ry, rx + 60, ry + 30)

        # planet1 orbits in a circle
        cx, cy = w * 0.3, h * 0.65
        rad = min(w, h) * 0.12
        ang = progress * 2 * math.pi
        px = cx + math.cos(ang) * rad - 40
        py = cy + math.sin(ang) * rad - 40
        c.coords(self.planet1, px, py, px + 80, py + 80)

        # planet2 moves down slowly
        cx2 = w * 0.7
        py2 = (progress * (h + 90)) % (h + 90) - 90
        c.coords(self.planet2, cx2 - 45, py2, cx2 + 45, py2 + 90)

        # stars drift
        for i, sid in enumerate(self.star_labels):
            sx = (w * 0.5 + math.sin(progress * 6 + i * 2) * w * 0.3) % w
            sy = h * 0.15 + + (i * 30)
            c.coords(sid, sx, sy)

        if progress >= 1.0:
            self.skip()
            return
        self._step()

    def _now_ms(self) -> int:
        return self.app.root.tk.call("clock", "milliseconds")

    def skip(self) -> None:
        self._cancel()
        self.app.show("main_menu")
