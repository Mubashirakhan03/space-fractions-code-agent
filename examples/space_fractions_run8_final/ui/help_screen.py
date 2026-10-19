"""View Help use case."""
import tkinter as tk

from ui import theme
from ui.base_screen import make_button, title_label


HELP_TEXT = (
    "Welcome to Space Fractions!\n\n"
    "In each mission you will face a series of fraction questions.\n"
    "Pick the correct answer from the choices, or type your answer for\n"
    "decimal questions and press Enter / Check.\n\n"
    "Question types:\n"
    "  • Equivalent — pick the fraction with the same value.\n"
    "  • Simplify — reduce a fraction to lowest terms.\n"
    "  • Decimal — write the fraction as a decimal.\n"
    "  • Larger — which of two fractions is bigger?\n\n"
    "Use Pause to take a break and resume when ready.\n"
    "Your score is shown at the end of each mission. Good luck, astronaut!"
)


class HelpScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.title = title_label(self, "How to Play", 32)
        self.title.pack(pady=(30, 10))

        self.text = tk.Text(self, bg=theme.SURFACE, fg=theme.TEXT,
                            font=theme.body_font(18), wrap="word",
                            relief="flat", padx=20, pady=14, height=16)
        self.text.insert("1.0", HELP_TEXT)
        self.text.config(state="disabled")
        self.text.pack(expand=True, fill="both", padx=20, pady=10)

        self.back_btn = make_button(self, "Menu",
                                    lambda: app.show("menu"))
        self.back_btn.pack(pady=(0, 20))

    def on_show(self):
        pass
