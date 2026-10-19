"""Shared screen helpers."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk

import ui.theme as theme
from ui.spacebg import SpaceBackground


class BaseScreen(tk.Frame):
    """A full-window screen: space background + a content frame centred."""

    def __init__(self, master, app):
        super().__init__(master, bg=theme.SPACE_BG)
        self.app = app
        self.bg = SpaceBackground(self)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.content = tk.Frame(self, bg=theme.SPACE_BG)
        # Fill the whole screen (with padding) so content resizes with the
        # window and scrollable areas (admin list) expand correctly.
        self.content.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        self._build()

    def _build(self):
        raise NotImplementedError

    def refresh(self):
        pass

    def focus(self):
        pass


def make_button(parent, text, command, bg=theme.PRIMARY, fg=theme.TEXT,
                font=theme.BUTTON_FONT, padx=30, pady=14):
    btn = tk.Button(
        parent, text=text, command=command, bg=bg, fg=fg, font=font,
        activebackground=theme.HOVER, activeforeground=theme.TEXT,
        relief="flat", padx=padx, pady=pady, cursor="hand2",
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=theme.HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn
