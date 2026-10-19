"""Help screen (scrollable instructions)."""
import tkinter as tk

from ui import theme
from ui.base_screen import BaseScreen


class HelpScreen(BaseScreen):
    HELP_TEXT = (
        "How to play Space Fractions\n\n"
        "A question shows a fraction problem.\n"
        "\u2022 If it offers choices, click the correct one.\n"
        "\u2022 If it asks you to type, write the fraction (e.g. 3/4)\n"
        "  and press Check or Enter.\n\n"
        "The denominator (bottom number) is how many equal parts\n"
        "make a whole. The numerator (top number) is how many parts\n"
        "you have. Equivalent fractions like 1/2 and 2/4 are equal.\n\n"
        "You score one point for each correct first answer.\n"
        "Pause any time; your progress is kept until the round ends."
    )

    def __init__(self, master, app):
        super().__init__(master, app)
        self.title_label = tk.Label(
            self.body, text="Help", font=theme.HEADING,
            fg=theme.ACCENT, bg=theme.BG,
        )
        self.title_label.pack(pady=(0, 12))
        self.text = tk.Text(
            self.body, font=theme.BODY, bg=theme.SURFACE, fg=theme.TEXT,
            relief="flat", wrap="word", height=14, width=60,
        )
        self.text.insert("1.0", self.HELP_TEXT)
        self.text.config(state="disabled")
        self.text.pack(pady=(0, 16))
        self.back_btn = self.make_button("Back to Menu", self._back)
        self.back_btn.pack()

    def _back(self):
        self.app.show("menu")
