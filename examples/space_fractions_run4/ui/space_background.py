"""Space-themed Canvas background: twinkling stars and planets.

The background is drawn from the <Configure> event (winfo_width/height are
only valid once the window is mapped), never at construction time.
"""
import random
import tkinter as tk

import ui.theme as theme


class SpaceBackground(tk.Canvas):
    """A full-window canvas drawing a starfield and planets.

    Usage: place this packed first (fill=both, expand=True) and stack other
    widgets/screens on top of it by using it as their parent or overlaying
    frames via place().
    """

    def __init__(self, master, **kwargs):
        kwargs.setdefault("bg", theme.BG)
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)
        self._seed = random.randint(0, 2 ** 31)
        self._star_items = []

    def _draw(self, event):
        self.delete("all")
        w, h = event.width, event.height
        rng = random.Random(self._seed)

        # static deep space
        self.create_rectangle(0, 0, w, h, fill=theme.BG, outline="")

        # twinkling stars
        n_stars = max(60, min(200, (w * h) // 6000))
        for _ in range(n_stars):
            x = rng.randint(0, w)
            y = rng.randint(0, h)
            r = rng.choice((1, 1, 1, 2))
            colour = rng.choice(("#FFFFFF", "#DDE7FF", "#FFE9A8"))
            self.create_oval(x, y, x + r, y + r, fill=colour, outline="")

        # three colourful planets
        if w > 0 and h > 0:
            self._draw_planet(w * 0.78, h * 0.20, min(60, w // 10), "#7A2E8C", "#B85FD4")
            self._draw_planet(w * 0.16, h * 0.74, min(46, w // 16), "#1E7E5C", "#3DDC84")
            self._draw_planet(w * 0.88, h * 0.80, min(38, w // 20), "#C2410C", "#FF8A50")

    def _draw_planet(self, cx, cy, r, base, ring):
        self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=base, outline="")
        self.create_arc(cx - r, cy - r, cx + r, cy + r, start=30, extent=180,
                        style="arc", outline=ring, width=max(2, r // 8))
        # atmosphere highlight
        self.create_oval(cx - r, cy - r, cx + r, cy + r, outline=ring, width=1)
