"""End screen: final score, percentage, stars, confetti, play again / menu."""
from __future__ import annotations

import random
import tkinter as tk

from . import theme
from .widgets import SpaceCanvas


class EndScreen(tk.Frame):
    name = "end"

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app
        self._confetti_cb = None

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title = tk.Label(
            self.canvas, text="", bg=theme.BG, fg=theme.YELLOW,
            font=theme.font(36, "bold"),
        )
        self.canvas.create_window(550, 130, window=self.title)

        self.score_label = tk.Label(
            self.canvas, text="", bg=theme.BG, fg=theme.TEXT,
            font=theme.font(26, "bold"),
        )
        self.canvas.create_window(550, 230, window=self.score_label)

        self.stars_label = tk.Label(
            self.canvas, text="", bg=theme.BG, fg=theme.YELLOW,
            font=theme.font(40, "bold"),
        )
        self.canvas.create_window(550, 320, window=self.stars_label)

        self.encourage = tk.Label(
            self.canvas, text="", bg=theme.BG, fg=theme.CYAN,
            font=theme.font(20),
        )
        self.canvas.create_window(550, 400, window=self.encourage)

        self.again_btn = theme.big_button(
            self.canvas, "Play again", command=self._again, bg=theme.CYAN, width=16,
        )
        self.canvas.create_window(550, 500, window=self.again_btn)

        self.menu_btn = theme.big_button(
            self.canvas, "Main menu", command=self._menu, bg=theme.MUTED, width=16,
        )
        self.canvas.create_window(550, 580, window=self.menu_btn)

    def refresh(self) -> None:
        self.canvas.draw_background()
        self.canvas.twinkle()
        game = self.app.game
        name = self.app.username or "Astronaut"
        self.title.configure(text=f"Congratulations, {name}!")
        if game is not None:
            self.score_label.configure(
                text=f"Score: {game.score} / {game.total}  ({game.percentage():.0f}%)"
            )
            stars = game.stars()
            self.stars_label.configure(text="★" * stars + "☆" * (3 - stars) or "No stars")
            if stars >= 3:
                self.encourage.configure(text="Out of this world! You're a fraction master! 🚀")
            elif stars >= 2:
                self.encourage.configure(text="Great job! Keep reaching for the stars!")
            elif stars >= 1:
                self.encourage.configure(text="Good effort! Practice makes perfect!")
            else:
                self.encourage.configure(text="Don't give up — try again, you'll get there!")
        self._confetti()

    def _confetti(self) -> None:
        self._stop_confetti()
        self._confetti_step()

    def _confetti_step(self, iteration: int = 0) -> None:
        if iteration > 60:
            self.canvas.delete("confetti")
            self._confetti_cb = None
            return
        self.canvas.delete("confetti")
        w = self.canvas.winfo_width() or 1100
        h = self.canvas.winfo_height() or 750
        for _ in range(40):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.randint(4, 10)
            colour = random.choice(theme.ACCENTS)
            self.canvas.create_oval(x, y, x + size, y + size, fill=colour, outline="",
                                    tags="confetti")
        self._confetti_cb = self.after(120, lambda: self._confetti_step(iteration + 1))

    def _stop_confetti(self) -> None:
        if self._confetti_cb is not None:
            try:
                self.after_cancel(self._confetti_cb)
            except tk.TclError:
                pass
            self._confetti_cb = None

    def _again(self) -> None:
        self._stop_confetti()
        self.app.show("question")

    def _menu(self) -> None:
        self._stop_confetti()
        self.app.show("menu")
