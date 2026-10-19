"""Player-name entry screen (UserComponent)."""
from __future__ import annotations

import tkinter as tk

import ui.theme as theme
from ui.screens.base import BaseScreen, make_button


class NameEntryScreen(BaseScreen):
    def _build(self):
        self.tk_title = tk.Label(
            self.content, text="Who's flying today?", font=theme.TITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.ACCENT_YELLOW,
        )
        self.tk_title.pack(pady=(0, 20))

        self.name_var = tk.StringVar()
        self.entry = tk.Entry(
            self.content, textvariable=self.name_var, font=theme.INPUT_FONT,
            bg=theme.PANEL, fg=theme.TEXT, insertbackground=theme.TEXT,
            relief="flat", justify="center", width=20,
        )
        self.entry.pack(ipady=10, pady=10)

        self.submit_btn = make_button(self.content, "Launch!", self._submit)
        self.submit_btn.pack(pady=10)
        self.back_btn = make_button(self.content, "Back", self._back,
                                    bg=theme.ACCENT_CYAN)
        self.back_btn.pack(pady=6)

        self.feedback = tk.Label(
            self.content, text="", font=theme.BODY_FONT,
            bg=theme.SPACE_BG, fg=theme.ERROR,
        )
        self.feedback.pack(pady=(8, 0))

        self.content.bind("<Return>", lambda e: self._submit())

    def refresh(self):
        self.name_var.set("")
        self.feedback.config(text="")

    def focus(self):
        self.entry.focus_set()

    def _submit(self):
        name = self.name_var.get().strip()
        if not name:
            self.feedback.config(text="Please type your name first.")
            return
        self.app.start_game(name)
        self.app.show("question")

    def _back(self):
        self.app.show("menu")
