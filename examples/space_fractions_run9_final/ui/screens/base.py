"""Base screen class shared by all screens."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class BaseScreen(tk.Frame):
    """A screen frame with a common dark background and app reference."""

    def __init__(self, parent, app, name: str) -> None:
        super().__init__(parent, bg=theme.BG)
        self.app = app
        self.name = name

    def on_show(self) -> None:
        """Called by App.show() before/after making the screen visible."""

    def on_hide(self) -> None:
        """Called by App.show() when leaving the screen."""
