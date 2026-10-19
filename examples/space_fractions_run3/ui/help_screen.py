"""Help screen (View Help use case): how to play."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.base import BaseScreen


HELP_TEXT = (
    "How to Play Space Fractions 🚀\n\n"
    "• You'll answer a round of 10 fraction questions.\n"
    "• Question types: equivalent fractions, comparing fractions,\n"
    "  adding/subtracting fractions, and simplifying fractions.\n"
    "• Pick an answer from the colored buttons, or type your answer\n"
    "  (like 3/4) and press Enter. Equivalent answers count —\n"
    "  2/4 is the same as 1/2!\n"
    "• Each correct answer is worth 100 points.\n"
    "• Earn stars by your percentage: 90%+ = 3 stars, 75%+ = 2 stars,\n"
    "  50%+ = 1 star.\n"
    "• Press Pause to take a break, and Resume to keep playing.\n\n"
    "Keys: F11 = full screen, Esc = leave full screen.\n"
    "Have fun exploring the galaxy of fractions! 🌌"
)


class HelpScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        panel = tk.Frame(self, bg=theme.SURFACE, padx=40, pady=24)
        panel.place(relx=0.5, rely=0.5, anchor="center")
        self.title_label = tk.Label(
            panel, text="❓ Help", font=self.theme.title(),
            bg=theme.SURFACE, fg=theme.PRIMARY,
        )
        self.title_label.pack(pady=(0, 10))
        text_frame = tk.Frame(panel, bg=theme.SURFACE)
        text_frame.pack(pady=6)
        scroll = tk.Scrollbar(text_frame, orient="vertical")
        self.help_text = tk.Text(
            text_frame, height=13, width=56, font=self.theme.body(),
            bg=theme.SURFACE_ALT, fg=theme.TEXT, relief="flat", wrap="word",
            yscrollcommand=scroll.set,
        )
        scroll.config(command=self.help_text.yview)
        scroll.pack(side="right", fill="y")
        self.help_text.pack(side="left")
        self.help_text.insert("end", HELP_TEXT)
        self.help_text.config(state="disabled")
        self.menu_button = tk.Button(
            panel, text="🏠 Main Menu", command=lambda: self.app.show("menu"),
            font=self.theme.button(), bg=theme.PRIMARY, fg=theme.BG,
            activebackground=theme.ACCENT, relief="flat", padx=30, pady=10,
        )
        self.menu_button.pack(pady=14)
