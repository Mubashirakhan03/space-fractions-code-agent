"""Ending scene: final score, percentage, 1-3 stars, confetti animation,
Play again / Main menu."""
from __future__ import annotations

import random
import tkinter as tk

from ui import theme
from ui.base import BaseScreen


class EndScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.congrats_label = tk.Label(
            self.canvas, text="", font=self.theme.title(), bg=theme.BG, fg=theme.PRIMARY,
        )
        self.score_label = tk.Label(
            self.canvas, text="", font=self.theme.heading(), bg=theme.BG, fg=theme.TEXT,
        )
        self.stars_label = tk.Label(
            self.canvas, text="", font=self.theme.heading(), bg=theme.BG, fg=theme.STAR_FILL,
        )
        self.message_label = tk.Label(
            self.canvas, text="", font=self.theme.body(), bg=theme.BG, fg=theme.TEXT_MUTED,
            wraplength=900, justify="center",
        )
        self.again_button = tk.Button(
            self.canvas, text="🔄 Play Again", command=lambda: self.app.show("name"),
            font=self.theme.button(), bg=theme.PRIMARY, fg=theme.BG,
            activebackground=theme.ACCENT, relief="flat", padx=30, pady=12,
        )
        self.menu_button = tk.Button(
            self.canvas, text="🏠 Main Menu", command=lambda: self.app.show("menu"),
            font=self.theme.button(), bg=theme.SURFACE_ALT, fg=theme.TEXT,
            activebackground=theme.SURFACE, relief="flat", padx=30, pady=12,
        )
        self._confetti_after = None

    def on_show(self):
        svc = getattr(self.app, "game_service", None)
        name = getattr(self.app, "player_name", "Astronaut")
        self.congrats_label.config(text=f"Congratulations, {name}!")
        if svc and svc.game:
            g = svc.game
            self.score_label.config(
                text=f"Score: {g.score}  ({g.percent:.1f}%)"
            )
            self.stars_label.config(text="★" * g.stars + "☆" * (3 - g.stars))
            self.message_label.config(text=self._message(g.stars))
            self.app.record_score(name, g.score, g.answered, g.percent, g.stars)
        else:
            self.score_label.config(text="Score: 0  (0.0%)")
            self.stars_label.config(text="☆☆☆")
            self.message_label.config(text="Play a game to earn stars!")
        self._place()
        self._animate_confetti()

    def _message(self, stars):
        if stars == 3:
            return "Out of this world! You're a fractions superstar! 🌟🌟🌟"
        if stars == 2:
            return "Great job! Keep practising and reach for the stars! 🌟🌟"
        if stars == 1:
            return "Good effort! A little more practice and you'll soar! 🌟"
        return "Keep going — every attempt helps you level up! 🚀"

    def _place(self):
        self.congrats_label.place(relx=0.5, rely=0.16, anchor="center")
        self.stars_label.place(relx=0.5, rely=0.3, anchor="center")
        self.score_label.place(relx=0.5, rely=0.42, anchor="center")
        self.message_label.place(relx=0.5, rely=0.54, anchor="center")
        self.again_button.place(relx=0.38, rely=0.78, anchor="center")
        self.menu_button.place(relx=0.62, rely=0.78, anchor="center")

    def _animate_confetti(self):
        if self._confetti_after:
            self.after_cancel(self._confetti_after)
        rng = random.Random(7)
        colors = [theme.PRIMARY, theme.ACCENT, theme.ACCENT_2, theme.ACCENT_3]
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            self._confetti_after = self.after(200, self._animate_confetti)
            return
        for _ in range(60):
            x = rng.uniform(0, w)
            y = rng.uniform(0, h)
            color = rng.choice(colors)
            size = rng.randint(4, 10)
            self.canvas.create_oval(
                x, y, x + size, y + size, fill=color, outline="", tags="confetti",
            )

    def draw_background(self, w, h):
        super().draw_background(w, h)
        self._place()
