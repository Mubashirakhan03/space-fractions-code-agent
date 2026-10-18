"""Reusable widgets: starry space canvas, space panel."""
from __future__ import annotations

import random
import tkinter as tk

from . import theme


class SpaceCanvas(tk.Canvas):
    """Dark space background with twinkling stars and planets."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=theme.BG, highlightthickness=0, **kwargs)
        self._stars: list[tuple[int, int, int, str, int]] = []
        self._after_id = None

    def draw_background(self) -> None:
        self.delete("all")
        w = self.winfo_width() or 1100
        h = self.winfo_height() or 750
        # Planets (arcs/ovals)
        self.create_oval(w - 260, 60, w - 60, 260, fill=theme.PINK, outline="")
        self.create_arc(
            w - 260, 60, w - 60, 260, start=30, extent=60, style="arc",
            outline=theme.YELLOW, width=4,
        )
        self.create_oval(80, h - 240, 240, h - 80, fill=theme.GREEN, outline="")
        self.create_oval(w // 2 - 70, h // 2 - 70, w // 2 + 70, h // 2 + 70,
                         fill=theme.CYAN, outline="")
        # Stars
        self._stars = []
        for _ in range(80):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.choice([1, 1, 2, 2, 3])
            self._stars.append((x, y, size, "white", 0))
        for (x, y, size, colour, _) in self._stars:
            self.create_oval(x, y, x + size, y + size, fill=colour, outline="",
                             tags="star")

    def twinkle(self) -> None:
        for i, (x, y, size, _, phase) in enumerate(self._stars):
            shade = theme.YELLOW if phase % 2 == 0 else "white"
            self._stars[i] = (x, y, size, shade, phase + 1)
        for i, (x, y, size, colour, _) in enumerate(self._stars):
            self.delete(f"s{i}")
            self.create_oval(x, y, x + size, y + size, fill=colour, outline="",
                             tags=f"s{i}")
        self._after_id = self.after(500, self.twinkle)

    def stop(self) -> None:
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None


class SpacePanel(tk.Frame):
    """Rounded-ish dark panel used to hold content over the canvas."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=theme.PANEL, **kwargs)
