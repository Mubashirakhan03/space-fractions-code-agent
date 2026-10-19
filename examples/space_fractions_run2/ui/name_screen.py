"""Player name entry screen: input focused, Enter submits, cleared after submit."""
from __future__ import annotations

import tkinter as tk

from . import theme
from .space_canvas import SpaceCanvas


class NameScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self, text="What's your name, cadet?", font=theme.SUBTITLE_FONT,
            bg=theme.BG, fg=theme.TEXT)
        self.title_label.place(relx=0.5, rely=0.35, anchor="center")

        self.name_entry = tk.Entry(
            self, font=theme.INPUT_FONT, bg=theme.SURFACE_ALT, fg=theme.TEXT,
            insertbackground=theme.PRIMARY, relief="flat", justify="center",
            width=24)
        self.name_entry.place(relx=0.5, rely=0.47, anchor="center")
        self.name_entry.bind("<Return>", lambda e: self._submit())

        self.start_button = tk.Button(
            self, text="Start Mission →", font=theme.BUTTON_FONT,
            bg=theme.SURFACE, fg=theme.TEXT,
            activebackground=theme.PRIMARY, activeforeground=theme.BG,
            relief="flat", padx=24, pady=10, command=self._submit)
        self.start_button.place(relx=0.5, rely=0.58, anchor="center")
        self.start_button.bind("<Enter>", lambda e: self.start_button.config(bg=theme.PRIMARY, fg=theme.BG))
        self.start_button.bind("<Leave>", lambda e: self.start_button.config(bg=theme.SURFACE, fg=theme.TEXT))

        self.back_button = tk.Button(
            self, text="← Back", font=theme.SMALL_FONT,
            bg=theme.BG, fg=theme.TEXT_MUTED, relief="flat",
            activebackground=theme.SURFACE, command=lambda: app.show("menu"))
        self.back_button.place(relx=0.08, rely=0.06, anchor="center")

        self.feedback_label = tk.Label(
            self, text="", font=theme.BODY_FONT, bg=theme.BG, fg=theme.ERROR)
        self.feedback_label.place(relx=0.5, rely=0.68, anchor="center")

    def _submit(self):
        name = self.name_entry.get().strip()
        if not name:
            self.feedback_label.config(text="Please enter a name first!", fg=theme.ERROR)
            return
        self.feedback_label.config(text="")
        self.app.set_player_name(name)
        self.name_entry.delete(0, tk.END)
        self.app.start_game()
        self.app.show("question")

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.name_entry.focus_set()
