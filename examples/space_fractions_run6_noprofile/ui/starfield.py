"""Animated starfield canvas background (binds <Configure>)."""
import random
import tkinter as tk

from ui import theme


class Starfield(tk.Canvas):
    """A dark canvas with drifting stars; redraws on <Configure>.

    Never reads winfo_width/height at construction; positions are recomputed
    from event.width/event.height on every resize.
    """

    def __init__(self, master, **kwargs):
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("bg", theme.BG)
        super().__init__(master, **kwargs)
        self._stars = []  # list of [x, y, speed, size]
        self._w = 0
        self._h = 0
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        self._w = event.width
        self._h = event.height
        if not self._stars:
            self._stars = self._make_stars(120)
        self._draw()

    def _make_stars(self, n):
        return [
            [random.uniform(0, self._w or 800),
             random.uniform(0, self._h or 600),
             random.uniform(0.2, 1.2),
             random.uniform(0.5, 2.2)]
            for _ in range(n)
        ]

    def _draw(self):
        self.delete("all")
        for s in self._stars:
            s[1] += s[2]
            if s[1] > (self._h or 600):
                s[1] = 0
                s[0] = random.uniform(0, self._w or 800)
            self.create_oval(
                s[0], s[1], s[0] + s[3], s[1] + s[3],
                fill=theme.ACCENT, outline="",
            )
        self.after(33, self._draw)
