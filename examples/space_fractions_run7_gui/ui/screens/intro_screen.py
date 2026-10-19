"""Intro screen (introductory movie): starfield + title + Start."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.widgets import StarCanvas


class IntroScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BACKGROUND)
        self.app = app
        self.canvas = StarCanvas(self)
        self.canvas.pack(fill="both", expand=True)
        self.title = self.canvas.create_text(
            1, 1, text="Space Fractions", fill=theme.ACCENT, font=theme.TITLE_FONT
        )
        self.subtitle = self.canvas.create_text(
            1, 1, text="Travel the galaxy and learn fractions!",
            fill=theme.TEXT, font=theme.SUBTITLE_FONT,
        )
        self.start_btn = tk.Button(
            self.canvas, text="\u25b6  Start Adventure", command=self._start
        )
        theme.style_button(self.start_btn)
        self._wbtn = self.canvas.create_window(1, 1, window=self.start_btn)
        self.canvas.bind("<Configure>", self._layout)

    def _layout(self, event):
        w, h = event.width, event.height
        if w <= 1 or h <= 1:
            return
        self.canvas.coords(self.title, w // 2, h * 0.35)
        self.canvas.coords(self.subtitle, w // 2, h * 0.45)
        self.canvas.coords(self._wbtn, w // 2, h * 0.60)

    def _start(self):
        self.app.show("menu")


__all__ = ["IntroScreen"]
