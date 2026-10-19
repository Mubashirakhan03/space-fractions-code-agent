"""Ending scene: score, percentage, stars, feedback, play again."""
from __future__ import annotations

import tkinter as tk

import ui.theme as theme
from ui.screens.base import BaseScreen, make_button


class EndScreen(BaseScreen):
    def _build(self):
        self.title = tk.Label(
            self.content, text="", font=theme.TITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.ACCENT_YELLOW,
        )
        self.title.pack(pady=(0, 10))

        self.score_text = tk.Label(
            self.content, text="", font=theme.SUBTITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.TEXT,
        )
        self.score_text.pack(pady=4)

        self.stars = tk.Label(
            self.content, text="", font=("Verdana", 48, "bold"),
            bg=theme.SPACE_BG, fg=theme.ACCENT_YELLOW,
        )
        self.stars.pack(pady=10)

        self.encourage = tk.Label(
            self.content, text="", font=theme.BODY_FONT,
            bg=theme.SPACE_BG, fg=theme.MUTED_TEXT,
        )
        self.encourage.pack(pady=(0, 20))

        self.play_again = make_button(self.content, "Play again", self._again,
                                      bg=theme.ACCENT_GREEN)
        self.play_again.pack(fill="x", pady=6)
        self.menu_btn = make_button(self.content, "Main menu", self._menu,
                                    bg=theme.PRIMARY)
        self.menu_btn.pack(fill="x", pady=6)

        self._confetti_items = []

    def refresh(self):
        ctl = self.app.controller
        if ctl is None:
            self.title.config(text="Great job!")
            self.score_text.config(text="No game finished yet.")
            self.stars.config(text="")
            self.encourage.config(text="")
            return
        g = ctl.game
        name = self.app.current_user or "Astronaut"
        self.title.config(text=f"Congratulations, {name}!")
        self.score_text.config(
            text=f"Score: {g.score} / {g.total}   ({g.percentage:.0f}%)")
        stars = g.stars()
        self.stars.config(text="★" * stars + "☆" * (3 - stars))
        self.encourage.config(text=self._encourage(stars))
        self._animate_confetti()

    def _encourage(self, stars):
        if stars == 3:
            return "Out of this world! You're a fractions superstar! 🌟"
        if stars == 2:
            return "Great flying! A little more practice and you'll soar! 🚀"
        if stars == 1:
            return "Good effort, captain! Let's try again! 🛰️"
        return "Every astronaut needs practice. Keep going! 🌌"

    def _again(self):
        self.app.start_game(self.app.current_user)
        self.app.show("question")

    def _menu(self):
        self.app.show("menu")

    def _animate_confetti(self):
        self.bg.after_cancel_check = True
        w = max(2, self.bg.winfo_width())
        h = max(2, self.bg.winfo_height())
        self._confetti_items.clear()
        colors = [theme.ACCENT_YELLOW, theme.ACCENT_CYAN,
                  theme.ACCENT_PINK, theme.ACCENT_GREEN]
        import random
        for _ in range(40):
            x = random.randint(0, w)
            y = random.randint(0, h)
            s = random.randint(3, 8)
            c = random.choice(colors)
            self._confetti_items.append(
                self.bg.create_oval(x, y, x + s, y + s, fill=c, outline=""))

    def focus(self):
        self.play_again.focus_set()
