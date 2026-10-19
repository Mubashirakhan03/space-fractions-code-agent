"""Shared base class and helpers for screens."""
import tkinter as tk

from ui import theme
from ui.starfield import Starfield


class BaseScreen(tk.Frame):
    """Common screen: starfield background + content frame."""

    def __init__(self, master, app):
        super().__init__(master, bg=theme.BG)
        self.app = app
        self.starfield = Starfield(self)
        self.starfield.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.body = tk.Frame(self, bg=theme.BG)
        self.body.place(relx=0.5, rely=0.5, anchor="center")

    def show(self):
        """Called when this screen becomes visible; refresh dynamic content."""

    def make_button(self, text, command, primary=True):
        bg = theme.PRIMARY if primary else theme.VIOLET
        btn = tk.Button(
            self.body, text=text, font=theme.BUTTON, command=command,
            bg=bg, fg=theme.TEXT, activebackground=theme.ACCENT,
            activeforeground=theme.BG, relief="flat", bd=0,
            padx=24, pady=12, cursor="hand2",
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=theme.ACCENT, fg=theme.BG))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg, fg=theme.TEXT))
        return btn
