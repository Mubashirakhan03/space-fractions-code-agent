"""Admin PIN gate (in-window, masked)."""
import tkinter as tk

from ui import theme
from ui.base_screen import make_button, title_label


class PinScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.title = title_label(self, "Admin Access", 32)
        self.title.pack(pady=(60, 10))
        sub = tk.Label(self, text="Enter your PIN to manage questions.",
                       bg=theme.BG, fg=theme.MUTED, font=theme.body_font(20))
        sub.pack()

        self.entry = tk.Entry(self, show="*", font=theme.body_font(24),
                              bg=theme.INPUT_BG, fg=theme.TEXT,
                              relief="solid", bd=2, width=12,
                              highlightthickness=2,
                              highlightbackground=theme.INPUT_BORDER,
                              highlightcolor=theme.INPUT_BORDER)
        self.entry.pack(pady=20)
        self.entry.bind("<Return>", lambda e: self._unlock())

        self.unlock_btn = make_button(self, "Unlock", self._unlock)
        self.unlock_btn.pack(pady=10)

        self.error = tk.Label(self, text="", bg=theme.BG, fg=theme.ERROR,
                              font=theme.body_font(20))
        self.error.pack(pady=10)

        self.back_btn = make_button(self, "Menu", lambda: app.show("menu"))
        self.back_btn.pack(pady=(30, 0))

    def on_show(self):
        self.entry.delete(0, "end")
        self.error.config(text="")
        self.entry.focus_set()

    def _unlock(self):
        pin = self.entry.get().strip()
        if pin == self.app.get_pin():
            self.app.admin_unlocked = True
            self.entry.delete(0, "end")
            self.error.config(text="")
            self.app.show("admin")
        else:
            self.error.config(text="Incorrect PIN. Try again.")
            self.entry.delete(0, "end")
