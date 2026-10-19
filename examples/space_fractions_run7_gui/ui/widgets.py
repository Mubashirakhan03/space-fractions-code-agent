"""Reusable Tkinter widgets."""
from __future__ import annotations

import random
import tkinter as tk

from ui import theme


class StarCanvas(tk.Canvas):
    """Animated space starfield; draws on <Configure> so it is resizable-safe."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("bg", theme.BACKGROUND)
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)
        self._rng = random.Random(1234)
        self._stars: list[tuple[float, float, float, int]] = []
        self._after_id = None
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        w, h = event.width, event.height
        if w <= 1 or h <= 1:
            return
        self.delete("all")
        self._stars = [
            (self._rng.random(), self._rng.random(), self._rng.random(), w + h)
            for _ in range(140)
        ]
        self._draw(w, h)

    def _draw(self, w: int, h: int):
        if w <= 1 or h <= 1:
            return
        self.delete("all")
        phase = getattr(self, "_phase", 0.0)
        for sx, sy, size, _ in self._stars:
            x = sx * w
            y = (sy * h + phase * 240) % h
            r = 1 + size % 2
            self.create_oval(x - r, y - r, x + r, y + r, fill=theme.TEXT, outline="")
        self._phase = phase + 0.02
        self._after_id = self.after(50, lambda: self._draw(w, h))

    def destroy(self):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        super().destroy()


__all__ = ["StarCanvas"]
