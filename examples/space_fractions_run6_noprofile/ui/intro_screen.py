"""Intro 'movie' screen: starfield + title + Continue."""
import tkinter as tk

from ui import theme
from ui.base_screen import BaseScreen


class IntroScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.title_label = tk.Label(
            self.body, text="Space Fractions", font=theme.TITLE,
            fg=theme.ACCENT, bg=theme.BG,
        )
        self.title_label.pack(pady=(0, 10))
        self.sub_label = tk.Label(
            self.body,
            text="Blast off on a maths mission across the galaxy!",
            font=theme.BODY, fg=theme.TEXT, bg=theme.BG,
        )
        self.sub_label.pack(pady=(0, 30))
        self.continue_btn = self.make_button("Continue", self._continue)
        self.continue_btn.pack()

    def _continue(self):
        self.app.show("login")
