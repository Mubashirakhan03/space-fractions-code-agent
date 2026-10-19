"""Intro 'movie' screen: animated rocket + title, Skip, auto-advance."""
from __future__ import annotations

import tkinter as tk

from . import theme
from .space_canvas import SpaceCanvas

AUTO_ADVANCE_MS = 12000


class IntroScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self, text="Space Fractions", font=theme.TITLE_FONT,
            bg=theme.BG, fg=theme.PRIMARY)
        self.title_label.place(relx=0.5, rely=0.35, anchor="center")

        self.subtitle = tk.Label(
            self, text="Blast off into fraction practice!",
            font=theme.SUBTITLE_FONT, bg=theme.BG, fg=theme.TEXT)
        self.subtitle.place(relx=0.5, rely=0.5, anchor="center")

        self.skip_button = tk.Button(
            self, text="Skip →", font=theme.BUTTON_FONT,
            bg=theme.SURFACE_ALT, fg=theme.TEXT,
            activebackground=theme.ACCENT_CYAN, activeforeground=theme.BG,
            relief="flat", padx=24, pady=12, command=self._skip)
        self.skip_button.place(relx=0.9, rely=0.9, anchor="center")
        self._bind_hover(self.skip_button, theme.SURFACE_ALT)

        self._after_id = None

    def _bind_hover(self, widget, bg):
        widget.bind("<Enter>", lambda e: widget.config(bg=theme.ACCENT_CYAN, fg=theme.BG))
        widget.bind("<Leave>", lambda e: widget.config(bg=bg, fg=theme.TEXT))

    def _skip(self):
        self._cancel()
        self.app.show("menu")

    def _cancel(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.canvas.reset_rocket()
        self.canvas.animate_rocket(0.6)
        self._cancel()
        self._after_id = self.after(AUTO_ADVANCE_MS, self._skip)

    def cancel(self):
        """Cancels pending after() callbacks (used by tests/teardown)."""
        self._cancel()
