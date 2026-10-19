"""Introductory movie: animated Canvas with moving stars and a rocket.

5-10 second animation, several objects move via after() every ~33 ms; a visible
Skip button; auto-advances to the menu when done. All after ids are tracked and
cancelled on Skip / leaving.
"""
import tkinter as tk
import random

from ui import theme
from ui.base_screen import make_button, title_label


class IntroScreen(tk.Frame):
    FALLBACK_W = 1200
    FALLBACK_H = 600

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app
        self._after_ids = []
        self._active = False
        self._configured = False

        self.title = title_label(self, "Space Fractions", 36)
        self.title.pack(pady=(30, 10))
        sub = tk.Label(self, text="Blast off on a fraction adventure!",
                       bg=theme.BG, fg=theme.ACCENT, font=theme.body_font(22))
        sub.pack()

        self.canvas = tk.Canvas(self, bg=theme.BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        self.canvas.bind("<Configure>", self._on_configure)

        self.skip_btn = make_button(self, "Skip", self._skip)
        self.skip_btn.pack(pady=(0, 30))

        self._stars = []
        self._rocket = None
        self._rocket_vx = 0.0

    def _dims(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            w, h = self.FALLBACK_W, self.FALLBACK_H
        return w, h

    def _on_configure(self, event):
        if event.width < 10 or event.height < 10:
            return
        self._configured = True
        if not self._stars:
            self._init_canvas(event.width, event.height)

    def _ensure_canvas(self):
        if not self._stars:
            self.canvas.update_idletasks()
            w, h = self._dims()
            self._init_canvas(w, h)

    def _init_canvas(self, w, h):
        rng = random.Random(42)
        if self._stars:
            # reposition existing items on resize
            self.canvas.delete("all")
            self._stars = []
            self._rocket = None
        for _ in range(40):
            x = rng.randint(0, w)
            y = rng.randint(0, h)
            r = rng.choice([2, 3, 4])
            item = self.canvas.create_oval(x, y, x + r, y + r,
                                           fill=theme.ACCENT, outline="")
            self._stars.append({"item": item, "vy": rng.uniform(1.5, 4.0)})
        self._rocket = self.canvas.create_text(w // 2, h // 2, text="🚀",
                                               font=theme.title_font(30))
        self._rocket_vx = 2.0

    def on_show(self):
        if self._active:
            return
        self._ensure_canvas()
        self._active = True
        self._reset()
        self._start_frames()
        # auto-advance after ~5 seconds
        aid = self.after(5000, self._finish)
        self._after_ids.append(aid)

    def _reset(self):
        w, h = self._dims()
        self.canvas.coords(self._rocket, w // 2, h // 2)
        self._rocket_vx = 2.0

    def _start_frames(self):
        def tick():
            if not self._active:
                return
            self._move()
            aid = self.after(33, tick)
            self._after_ids.append(aid)

        aid = self.after(33, tick)
        self._after_ids.append(aid)

    def _move(self):
        w, h = self._dims()
        # stars fall
        for s in self._stars:
            x0, y0, x1, y1 = self.canvas.coords(s["item"])
            ny = y0 + s["vy"]
            if ny > h:
                ny = -4
            self.canvas.coords(s["item"], x0, ny, x1, ny + (y1 - y0))
        # rocket drifts horizontally and bounces
        x, y = self.canvas.coords(self._rocket)
        x += self._rocket_vx
        if x > w - 30 or x < 30:
            self._rocket_vx = -self._rocket_vx
            x = max(30, min(x, w - 30))
        self.canvas.coords(self._rocket, x, y)

    def _finish(self):
        self._cancel_after()
        self._active = False
        self.app.show("menu")

    def _skip(self):
        self._cancel_after()
        self._active = False
        self.app.show("menu")

    def _cancel_after(self):
        for aid in self._after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        self._after_ids = []

    def leave(self):
        self._cancel_after()
        self._active = False
