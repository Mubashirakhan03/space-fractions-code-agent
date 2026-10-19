"""Help screen (View Help use case)."""
from __future__ import annotations

import tkinter as tk

from ui import theme

HELP_TEXT = (
    "How to play Space Fractions:\n\n"
    "1. Press Play Game to start a mission.\n"
    "2. Answer each fraction question by typing your answer\n"
    "   (like 1/2) or picking a button.\n"
    "3. Press Enter or the Submit button after typing.\n"
    "4. Watch for green (correct) or red (try again) feedback.\n"
    "5. Finish all questions to see your score!\n\n"
    "Fractions are written as numerator/denominator, e.g. 3/4.\n"
    "The Pause button lets you take a break; Resume continues the mission."
)


class HelpScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BACKGROUND)
        self.app = app
        self.title = tk.Label(self, text="Help", bg=theme.BACKGROUND,
                              fg=theme.ACCENT, font=theme.SUBTITLE_FONT)
        self.title.pack(pady=(20, 8))
        body = tk.Label(self, text=HELP_TEXT, bg=theme.BACKGROUND,
                        fg=theme.TEXT, font=theme.SMALL_FONT, justify="left")
        body.pack(pady=8)
        self.back_btn = tk.Button(self, text="Back to Menu",
                                  command=lambda: self.app.show("menu"))
        theme.style_button(self.back_btn)
        self.back_btn.pack(pady=10)


__all__ = ["HelpScreen"]
