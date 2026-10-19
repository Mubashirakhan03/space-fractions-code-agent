"""Help screen (View Help use case)."""
from __future__ import annotations

import tkinter as tk

import ui.theme as theme
from ui.screens.base import BaseScreen, make_button


class HelpScreen(BaseScreen):
    HELP_TEXT = (
        "How to play Space Fractions:\n\n"
        "1. Pick a name and press Launch!\n"
        "2. Answer 10 fraction questions.\n"
        "   • Some are multiple choice — tap the right fraction.\n"
        "   • Some are typed — type your answer like 3/4.\n"
        "3. Equivalent forms count (2/4 = 1/2).\n"
        "4. Press Pause to take a break, Resume to continue.\n"
        "5. At the end, earn stars for your score!\n\n"
        "Question types: equivalent fractions, comparing,\n"
        "adding/subtracting, and simplifying."
    )

    def _build(self):
        self.tk_title = tk.Label(
            self.content, text="Help", font=theme.TITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.ACCENT_YELLOW,
        )
        self.tk_title.pack(pady=(0, 20))

        self.text = tk.Label(
            self.content, text=self.HELP_TEXT, font=theme.BODY_FONT,
            bg=theme.SPACE_BG, fg=theme.TEXT, justify="left",
        )
        self.text.pack(pady=(0, 20))

        self.back_btn = make_button(self.content, "Back to menu", self._back,
                                    bg=theme.PRIMARY)
        self.back_btn.pack()

    def _back(self):
        self.app.show("menu")
