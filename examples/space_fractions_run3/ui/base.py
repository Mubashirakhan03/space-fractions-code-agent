"""Base screen: a Tk Frame with a starfield Canvas background.

All canvas drawing happens on <Configure> (never at construction) so widgets
and canvas items stay inside the visible area.
"""
from __future__ import annotations

import random
import tkinter as tk

from ui import theme


class BaseScreen(tk.Frame):
    """A screen with a dark space background and twinkling stars."""

    def __init__(self, app, *args, **kwargs):
        super().__init__(app.root, bg=theme.BG, *args, **kwargs)
        self.app = app
        self.theme = app.theme
        self.canvas = tk.Canvas(self, bg=theme.BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.stars = self._make_stars()
        self.planets = [
            {"color": theme.ACCENT, "x": 0.12, "y": 0.18, "r": 46},
            {"color": theme.ACCENT_2, "x": 0.86, "y": 0.23, "r": 62},
            {"color": theme.ACCENT_3, "x": 0.9, "y": 0.8, "r": 34},
        ]

    def _make_stars(self):
        rng = random.Random(42)
        return [
            {"rx": rng.random(), "ry": rng.random(), "r": rng.choice((1, 1, 2)), "t": rng.random()}
            for _ in range(140)
        ]

    def _on_resize(self, event):
        self.draw_background(event.width, event.height)

    def draw_background(self, w, h):
        """(Re)draw stars and planets sized to the canvas."""
        c = self.canvas
        c.delete("bg")
        c.create_rectangle(0, 0, w, h, fill=theme.BG, outline="", tags="bg")
        for s in self.stars:
            x = s["rx"] * w
            y = s["ry"] * h
            r = s["r"]
            c.create_oval(x - r, y - r, x + r, y + r, fill=theme.TEXT, outline="", tags="bg")
        for p in self.planets:
            x = p["x"] * w
            y = p["y"] * h
            r = p["r"]
            c.create_oval(x - r, y - r, x + r, y + r, fill=p["color"], outline="", tags="bg")
            # a small ring/arc decoration for the middle planet
            if p["color"] == theme.ACCENT_2:
                c.create_oval(x - r - 12, y - r - 8, x + r + 12, y + r + 8,
                              outline=theme.PRIMARY, width=3, tags="bg")
        c.tag_lower("bg")

    def on_show(self):
        """Hook called when this screen becomes visible."""
        pass
