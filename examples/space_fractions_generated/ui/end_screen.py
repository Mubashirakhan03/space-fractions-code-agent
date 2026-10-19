"""End scene: congratulations, score, percentage, stars, confetti, replay buttons."""
from __future__ import annotations

import random
import tkinter as tk

from . import theme
from .space_canvas import SpaceCanvas


class EndScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self, text="Congratulations!", font=theme.TITLE_FONT,
            bg=theme.BG, fg=theme.PRIMARY)
        self.title_label.place(relx=0.5, rely=0.18, anchor="center")

        self.summary_label = tk.Label(
            self, text="", font=theme.BODY_FONT, bg=theme.BG, fg=theme.TEXT)
        self.summary_label.place(relx=0.5, rely=0.34, anchor="center")

        self.stars_label = tk.Label(
            self, text="", font=theme.SUBTITLE_FONT, bg=theme.BG, fg=theme.PRIMARY)
        self.stars_label.place(relx=0.5, rely=0.46, anchor="center")

        self.feedback_label = tk.Label(
            self, text="", font=theme.BODY_FONT, bg=theme.BG, fg=theme.ACCENT_CYAN)
        self.feedback_label.place(relx=0.5, rely=0.56, anchor="center")

        self.play_again_button = tk.Button(
            self, text="Play again", font=theme.BUTTON_FONT,
            bg=theme.SURFACE, fg=theme.TEXT, relief="flat", padx=24, pady=10,
            activebackground=theme.ACCENT_GREEN,
            command=self._play_again)
        self.play_again_button.place(relx=0.4, rely=0.7, anchor="center")
        self.play_again_button.bind("<Enter>", lambda e: self.play_again_button.config(bg=theme.ACCENT_GREEN, fg=theme.BG))
        self.play_again_button.bind("<Leave>", lambda e: self.play_again_button.config(bg=theme.SURFACE, fg=theme.TEXT))

        self.menu_button = tk.Button(
            self, text="Main menu", font=theme.BUTTON_FONT,
            bg=theme.SURFACE, fg=theme.TEXT, relief="flat", padx=24, pady=10,
            activebackground=theme.ACCENT_CYAN,
            command=lambda: app.show("menu"))
        self.menu_button.place(relx=0.6, rely=0.7, anchor="center")
        self.menu_button.bind("<Enter>", lambda e: self.menu_button.config(bg=theme.ACCENT_CYAN, fg=theme.BG))
        self.menu_button.bind("<Leave>", lambda e: self.menu_button.config(bg=theme.SURFACE, fg=theme.TEXT))

        self._after_id = None

    def _play_again(self):
        self.app.show("name")

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        result = self.app.game.result() if self.app.game else {
            "player_name": "", "score": 0, "total": 0, "percentage": 0.0, "stars": 0}
        self.title_label.config(text=f"Congratulations, {result['player_name']}!")
        self.summary_label.config(
            text=f"You scored {result['score']} out of {result['total']} "
                 f"({result['percentage']}%)")
        self.stars_label.config(text="★" * result["stars"] + "☆" * (3 - result["stars"]))
        self.feedback_label.config(text=self._encouragement(result["percentage"]))
        self._spawn_confetti()

    @staticmethod
    def _encouragement(pct):
        if pct >= 90:
            return "Out of this world! You're a fraction superstar! 🚀"
        if pct >= 70:
            return "Great job, cadet! Keep exploring! ✨"
        if pct >= 50:
            return "Nice work! Practice makes perfect! 🌟"
        return "Keep trying — every star makes you stronger! 💪"

    def _spawn_confetti(self):
        self._cancel()
        self._step_confetti(0)

    def _step_confetti(self, n):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w > 1 and h > 1:
            for _ in range(6):
                x = random.randint(0, w)
                y = random.randint(0, h)
                color = random.choice(theme.PLANET_COLORS)
                self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline="")
        if n < 18:
            self._after_id = self.after(120, lambda: self._step_confetti(n + 1))

    def _cancel(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    def cancel(self):
        self._cancel()
