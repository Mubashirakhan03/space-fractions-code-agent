"""Player name entry before playing (UserComponent)."""
from __future__ import annotations

import tkinter as tk

from users import User
from . import theme
from .widgets import SpaceCanvas, SpacePanel


class NameScreen(tk.Frame):
    name = "name"

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.panel = SpacePanel(self.canvas)
        self.panel.place(relx=0.5, rely=0.5, anchor="center")

        self.title = tk.Label(
            self.panel, text="What's your name, astronaut?",
            bg=theme.PANEL, fg=theme.YELLOW, font=theme.font(28, "bold"),
        )
        self.title.pack(pady=(30, 10))

        self.name_var = tk.StringVar()
        self.entry = tk.Entry(
            self.panel, textvariable=self.name_var, font=theme.font(22),
            width=24, justify="center",
        )
        self.entry.pack(pady=10, ipady=8)

        self.feedback = tk.Label(
            self.panel, text="", bg=theme.PANEL, fg=theme.GREEN,
            font=theme.font(18),
        )
        self.feedback.pack(pady=(0, 6))

        self.go_btn = theme.big_button(
            self.panel, "Blast Off!", command=self._submit, bg=theme.CYAN, width=16,
        )
        self.go_btn.pack(pady=6)

        self.back_btn = theme.big_button(
            self.panel, "Back", command=lambda: self.app.show("menu"),
            bg=theme.MUTED, width=16,
        )
        self.back_btn.pack(pady=(6, 30))

        self.entry.bind("<Return>", lambda e: self._submit())

    def refresh(self) -> None:
        self.canvas.draw_background()
        self.canvas.twinkle()
        self.feedback.configure(text="")
        self.entry.focus_set()

    def _submit(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            self.feedback.configure(text="Please enter your name.", fg=theme.RED)
            return
        self.app.username = name
        self.app.user = User(username=name, user_id=name)
        self.name_var.set("")
        self.app.show("question")
