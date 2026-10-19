"""Animated intro screen (the 'introductory movie')."""
from __future__ import annotations

import tkinter as tk

import ui.theme as theme
from ui.screens.base import BaseScreen, make_button


class IntroScreen(BaseScreen):
    """Space intro: rocket flying across moving stars, title, Skip button.

    Auto-advances to the main menu after ~8 seconds.
    """

    def _build(self):
        self.title = tk.Label(
            self.content, text="Space Fractions", font=theme.TITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.ACCENT_YELLOW,
        )
        self.title.pack(pady=(0, 10))
        self.subtitle = tk.Label(
            self.content, text="A fraction adventure for 6th-grade astronauts!",
            font=theme.SUBTITLE_FONT, bg=theme.SPACE_BG, fg=theme.MUTED_TEXT,
        )
        self.subtitle.pack(pady=(0, 30))

        self.skip = make_button(self.content, "Skip", self._skip,
                                bg=theme.ACCENT_CYAN)
        self.skip.pack()

        self._rocket_x = -120
        self._rocket_y = -1
        self._started = False
        self._anim()

    def refresh(self):
        super().refresh()
        self._rocket_x = -120
        if not self._started:
            self._started = True
            self.after(8000, self._auto_advance)

    def _auto_advance(self):
        self.app.show("menu")

    def _skip(self):
        self.app.show("menu")

    def _anim(self):
        w = max(2, self.bg.winfo_width())
        h = max(2, self.bg.winfo_height())
        self._rocket_x += 14
        if self._rocket_x > w + 200:
            self._rocket_x = -200
        if self._rocket_y < 0:
            self._rocket_y = int(h * 0.4)
        self.bg._draw_screen()
        # draw rocket streak
        rx = self._rocket_x
        ry = self._rocket_y
        self.bg.create_oval(rx - 60, ry - 4, rx, ry + 4,
                            fill=theme.ACCENT_YELLOW, outline="")
        # rocket body
        self.bg.create_polygon(
            rx, ry - 26, rx - 40, ry, rx, ry + 26, rx + 70, ry,
            fill="#D6E4FF", outline="",
        )
        self.bg.create_polygon(
            rx + 30, ry - 20, rx + 70, ry, rx + 30, ry + 20,
            fill=theme.ACCENT_PINK, outline="",
        )
        self.bg.create_polygon(
            rx - 40, ry, rx - 60, ry - 14, rx - 60, ry + 14,
            fill=theme.ACCENT_CYAN, outline="",
        )
        self.after(40, self._anim)
