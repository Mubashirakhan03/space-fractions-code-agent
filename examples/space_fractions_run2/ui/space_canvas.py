"""Reusable animated space background canvas (stars, planets, rocket).

All drawing is (re)done on <Configure> using event.width/height; positions
are never computed at construction time.
"""
from __future__ import annotations

import random
import tkinter as tk

from . import theme


class SpaceCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("bg", theme.BG)
        super().__init__(master, **kwargs)
        self._stars = [(random.random(), random.random(), 1 + random.random() * 1.5)
                       for _ in range(90)]
        self._planets = [
            (0.82, 0.16, 0.10, theme.PLANET_COLORS[0]),
            (0.15, 0.22, 0.06, theme.PLANET_COLORS[1]),
            (0.90, 0.78, 0.05, theme.PLANET_COLORS[3]),
        ]
        self._rocket_x = -0.1  # fraction of width (intro uses it)
        self._rocket_y = 0.28
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            return
        # starfield
        for sx, sy, sr in self._stars:
            x = sx * w
            y = sy * h
            self.create_oval(x - sr, y - sr, x + sr, y + sr,
                             fill=theme.STAR_COLOR, outline="")
        # planets
        for px, py, pr, color in self._planets:
            cx = px * w
            cy = py * h
            r = pr * min(w, h)
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="")
            # ring on one planet
            if color == theme.PLANET_COLORS[1]:
                self.create_oval(cx - r * 1.6, cy - r * 0.35,
                                 cx + r * 1.6, cy + r * 0.35,
                                 outline=theme.TEXT_MUTED, width=2)
        # rocket (if visible)
        if self._rocket_x >= -0.05:
            self._draw_rocket(w, h)

    def _draw_rocket(self, w, h):
        cx = self._rocket_x * w
        cy = self._rocket_y * h
        body = max(20, int(w * 0.03))
        self.create_polygon(cx, cy - body, cx + body, cy, cx + body, cy + body,
                            cx, cy + body * 2, cx - body, cy + body, cx - body, cy,
                            fill=theme.ACCENT_PINK, outline=theme.TEXT)
        # window
        self.create_oval(cx - body * 0.3, cy - body * 0.2,
                         cx + body * 0.3, cy + body * 0.4,
                         fill=theme.ACCENT_CYAN, outline="")
        # flame
        self.create_polygon(cx - body * 0.4, cy + body * 2,
                            cx + body * 0.4, cy + body * 2,
                            cx, cy + body * 3.2,
                            fill=theme.PRIMARY, outline="")

    def animate_rocket(self, target_x: float, step: float = 0.02, interval: int = 40):
        """Animate the rocket from its current x to target_x (fraction of width)."""
        self._rocket_x += step
        if self._rocket_x >= target_x:
            self._rocket_x = target_x
            self._redraw()
            return
        self._redraw()
        self.after(interval, lambda: self.animate_rocket(target_x, step, interval))

    def reset_rocket(self):
        self._rocket_x = -0.1
        self._redraw()
