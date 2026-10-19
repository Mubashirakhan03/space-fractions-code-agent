"""Login / profile selection screen."""
import tkinter as tk
from tkinter import simpledialog

from ui import theme
from ui.base_screen import BaseScreen


class LoginScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.title_label = tk.Label(
            self.body, text="Who is playing?", font=theme.HEADING,
            fg=theme.ACCENT, bg=theme.BG,
        )
        self.title_label.pack(pady=(0, 30))
        self.user_btn = self.make_button("End User (Play)",
                                         lambda: self._login("user"))
        self.user_btn.pack(pady=8)
        self.admin_btn = self.make_button("Admin (Manage Questions)",
                                          lambda: self._login("admin"), primary=False)
        self.admin_btn.pack(pady=8)

    def _login(self, role):
        name = simpledialog.askstring(
            "Space Fractions", "Enter your name:", parent=self,
        )
        if not name:
            return
        self.app.controller.login(name.strip() or "Player", role)
        self.app.show("menu")
