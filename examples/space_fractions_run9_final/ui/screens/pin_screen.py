"""In-window PIN screen guarding the Admin area (protected role)."""
from __future__ import annotations

from ui import theme
from ui.screens.base import BaseScreen


class PinScreen(BaseScreen):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "pin_screen")
        theme.make_label(self, "Admin Access", theme.TITLE_SIZE, theme.ACCENT,
                         "bold").pack(pady=(60, 10))
        theme.make_label(self, "Enter your PIN to manage questions:",
                         theme.CONTENT_SIZE, theme.MUTED).pack(pady=10)

        row = __import__("tkinter").Frame(self, bg=theme.BG)
        row.pack(pady=16)
        self.pin_entry = theme.make_entry(row, show="*", width=12)
        self.pin_entry.pack(side="left", padx=10)
        self.unlock_btn = theme.make_button(row, "Unlock", self.unlock)
        self.unlock_btn.pack(side="left", padx=10)
        self.pin_entry.bind("<Return>", lambda _e: self.unlock())

        self.error_label = theme.make_label(self, "", theme.FEEDBACK_SIZE,
                                            theme.ERROR, "bold")
        self.error_label.pack(pady=10)

        self.back_btn = theme.make_button(self, "⬅  Back to Menu",
                                          lambda: self.app.show("main_menu"),
                                          bg=theme.SURFACE)
        self.back_btn.pack(pady=10)

    def on_show(self) -> None:
        self.pin_entry.delete(0, "end")
        self.error_label.config(text="")
        self.pin_entry.focus_set()

    def unlock(self) -> None:
        entered = self.pin_entry.get()
        if self.app.settings.check_pin(entered):
            self.error_label.config(text="")
            self.pin_entry.delete(0, "end")
            self.app.show("admin_screen")
        else:
            self.error_label.config(text="❌ Incorrect PIN. Please try again.")
            self.pin_entry.select_range(0, "end")
            self.pin_entry.focus_set()
