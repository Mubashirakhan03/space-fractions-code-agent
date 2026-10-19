"""Animated starfield canvas background (binds <Configure>)."""
import random
import tkinter as tk

from ui import theme


class Starfield(tk.Canvas):
    """A dark canvas with drifting stars; redraws on <Configure>.

    Never reads winfo_width/height at construction; positions are recomputed
    from event.width/event.height on every resize. The animation loop stops
    itself when the widget is destroyed (so pending ``after`` callbacks do not
    fire against a dead widget).
    """

    def __init__(self, master, **kwargs):
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("bg", theme.BG)
        super().__init__(master, **kwargs)
        self._stars = []
        self._width = 0
        self._height = 0
        self._running = False
        self.bind("<Configure>", self._on_configure)
        self.bind("<Destroy>", self._on_destroy)

    def _on_configure(self, event):
        self._width = event.width
        self._height = event.height
        if not self._stars:
            self._stars = self._make_stars(120)
        self._draw()
        if not self._running:
            self._running = True
            self.after(33, self._animate)

    def _on_destroy(self, _event):
        self._running = False

    def stop(self):
        self._running = False

    def _animate(self):
        if not self._running or not self.winfo_exists():
            return
        self._draw()
        if self._running:
            self.after(33, self._animate)

    def _make_stars(self, n):
        return [
            [random.uniform(0, self._width or 800),
             random.uniform(0, self._height or 600),
             random.uniform(0.2, 1.2),
             random.uniform(0.5, 2.2)]
            for _ in range(n)
        ]

    def _draw(self):
        if not self.winfo_exists():
            return
        self.delete("all")
        for s in self._stars:
            s[1] += s[2]
            if s[1] > (self._height or 600):
                s[1] = 0
                s[0] = random.uniform(0, self._width or 800)
            self.create_oval(
                s[0], s[1], s[0] + s[3], s[1] + s[3],
                fill=theme.ACCENT, outline="",
            )
