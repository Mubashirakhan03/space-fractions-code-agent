"""Player name entry (UserComponent): enter a name before playing."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.base import BaseScreen


class NameEntryScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        panel = tk.Frame(self, bg=theme.SURFACE, padx=40, pady=40)
        panel.place(relx=0.5, rely=0.5, anchor="center")
        self.title_label = tk.Label(
            panel, text="What's your name, astronaut?", font=self.theme.heading(),
            bg=theme.SURFACE, fg=theme.TEXT,
        )
        self.title_label.pack(pady=(0, 20))
        self.name_entry = tk.Entry(
            panel, font=self.theme.question(), bg=theme.SURFACE_ALT,
            fg=theme.TEXT, insertbackground=theme.TEXT, relief="flat", width=18,
        )
        self.name_entry.pack(pady=10, ipady=6)
        self.feedback = tk.Label(
            panel, text="", font=self.theme.label(), bg=theme.SURFACE, fg=theme.ERROR,
        )
        self.feedback.pack(pady=(4, 10))
        self.start_button = tk.Button(
            panel, text="Launch 🚀", command=self._start,
            font=self.theme.button(), bg=theme.PRIMARY, fg=theme.BG,
            activebackground=theme.ACCENT, relief="flat", padx=30, pady=10,
        )
        self.start_button.pack(pady=6)
        self.name_entry.bind("<Return>", lambda e: self._start())

    def on_show(self):
        self.name_entry.delete(0, "end")
        self.name_entry.focus_set()
        self.feedback.config(text="")

    def _start(self):
        name = self.name_entry.get().strip()
        if not name:
            self.feedback.config(text="Please enter a name to play.")
            return
        self.feedback.config(text="")
        self.name_entry.delete(0, "end")
        self.app.start_round(name)
