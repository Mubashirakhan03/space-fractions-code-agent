"""A reusable space-themed canvas background with twinkling stars and planets."""
from __future__ import annotations

import random
import tkinter as tk

import ui.theme as theme


class SpaceBackground(tk.Canvas):
    """Dark space canvas with twinkling stars and a couple of colourful planets.

    All drawing happens in a <Configure> handler using event dimensions, so it
    is safe at any window size (winfo_width/height are 1 until shown).
    """

    def __init__(self, master, **kwargs):
        kwargs.setdefault("bg", theme.SPACE_BG)
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)
        self._stars: list[tuple[int, int, int]] = []
        self._rng = random.Random(7)
        self._blink = 0
        self.bind("<Configure>", self._redraw)
        self._animate_stars()

    def _animate_stars(self):
        self._blink += 1
        self._draw_screen()
        self.after(120, self._animate_stars)

    def _ensure_stars(self, w: int, h: int) -> None:
        target = max(20, (w * h) // 4000)
        if len(self._stars) < target:
            while len(self._stars) < target:
                self._stars.append(
                    (self._rng.randint(0, 2000), self._rng.randint(0, 1200),
                     self._rng.randint(1, 3))
                )

    def _redraw(self, event=None):
        self._draw_screen()

    def _draw_screen(self):
        w = max(2, self.winfo_width())
        h = max(2, self.winfo_height())
        self.delete("all")
        self.create_rectangle(0, 0, w, h, fill=theme.SPACE_BG, outline="")
        self._ensure_stars(w, h)
        # stars (twinkle by toggling subset brightness)
        for i, (sx, sy, size) in enumerate(self._stars):
            bright = int(((self._blink + i) % 6) == 0) if i % 2 == 0 else 1
            color = "#FFFFFF" if bright else "#7EA6D8"
            x = (sx * w) // 2000
            y = (sy * h) // 1200
            self.create_oval(x, y, x + size, y + size, fill=color, outline="")

        # planets
        self._planet(w, h)

    def _planet(self, w: int, h: int):
        # cyan ringed planet, top-left
        cx = int(w * 0.18)
        cy = int(h * 0.26)
        r = max(30, min(70, w // 18))
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill="#1E7F8C", outline=theme.ACCENT_CYAN, width=3)
        self.create_oval(cx - int(r * 1.5), cy - int(r * 0.35),
                         cx + int(r * 1.5), cy + int(r * 0.35),
                         fill="", outline=theme.ACCENT_CYAN, width=4)

        # pink planet, bottom-right
        cx2 = int(w * 0.86)
        cy2 = int(h * 0.78)
        r2 = max(24, min(55, w // 22))
        self.create_oval(cx2 - r2, cy2 - r2, cx2 + r2, cy2 + r2,
                         fill="#B03A6E", outline=theme.ACCENT_PINK, width=3)

        # green planet, mid-left
        cx3 = int(w * 0.10)
        cy3 = int(h * 0.82)
        r3 = max(18, min(40, w // 28))
        self.create_oval(cx3 - r3, cy3 - r3, cx3 + r3, cy3 + r3,
                         fill="#1E6B3A", outline=theme.ACCENT_GREEN, width=3)
