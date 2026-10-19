"""Main menu screen."""
import tkinter as tk

from ui import theme
from ui.base_screen import make_button, title_label


class MenuScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.title = title_label(self, "Space Fractions", 36)
        self.title.pack(pady=(60, 20))

        body = tk.Frame(self, bg=theme.BG)
        body.pack(expand=True)

        self.play_btn = make_button(body, "🚀 Play Game", self._play)
        self.play_btn.pack(pady=12, ipadx=40)
        self.score_btn = make_button(body, "🏆 View Score",
                                     lambda: app.show("score"))
        self.score_btn.pack(pady=12, ipadx=40)
        self.help_btn = make_button(body, "❓ View Help",
                                    lambda: app.show("help"))
        self.help_btn.pack(pady=12, ipadx=40)
        self.admin_btn = make_button(body, "🔒 Admin", lambda: app.show("pin"))
        self.admin_btn.pack(pady=12, ipadx=40)
        self.exit_btn = make_button(body, "Exit", self._exit)
        self.exit_btn.pack(pady=12, ipadx=40)

    def _play(self):
        self.app.current_game = self.app.service.build_round()
        self.app.show("play")

    def _exit(self):
        self.app.root.destroy()

    def on_show(self):
        pass
