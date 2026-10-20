"""Help screen."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.screens.base import BaseScreen

HELP_TEXT = (
    "Welcome to Space Fractions!\n\n"
    "🪐 Your mission: answer fraction questions to earn stars.\n\n"
    "• Some questions ask you to pick an answer from the choices shown.\n"
    "• Others ask you to type the answer (for example, 1/2 or 3/4).\n\n"
    "A fraction like 2/4 means 2 parts out of 4.\n"
    "To reduce a fraction, divide top and bottom by the same number:\n"
    "2/4 = 1/2.\n\n"
    "You can pause and resume at any time. Good luck, astronaut!"
)


class HelpScreen(BaseScreen):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "help_screen")
        theme.make_label(self, "How to Play", theme.TITLE_SIZE, theme.ACCENT,
                         "bold").pack(pady=(20, 8))

        text = tk.Text(self, bg=theme.SURFACE, fg=theme.TEXT,
                       font=theme.font(theme.FEEDBACK_SIZE - 2),
                       relief="flat", wrap="word", bd=0,
                       highlightthickness=0,
                       padx=24, pady=16, height=10)
        text.insert("1.0", HELP_TEXT)
        text.config(state="disabled")
        text.pack(fill="both", expand=True, padx=60, pady=8)

        self.back_btn = theme.make_button(self, "⬅  Back to Menu",
                                          lambda: self.app.show("main_menu"))
        self.back_btn.pack(pady=12)
