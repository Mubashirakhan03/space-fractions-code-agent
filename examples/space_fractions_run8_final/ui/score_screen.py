"""View Score use case: history from the store."""
import tkinter as tk

from ui import theme
from ui.base_screen import make_button, title_label


class ScoreScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app

        self.title = title_label(self, "Your Scores", 32)
        self.title.pack(pady=(30, 10))

        self.body = tk.Frame(self, bg=theme.BG)
        self.body.pack(expand=True, fill="both", padx=20, pady=10)

        self.back_btn = make_button(self, "Menu",
                                    lambda: app.show("menu"))
        self.back_btn.pack(pady=(0, 20))

    def on_show(self):
        for w in self.body.winfo_children():
            w.destroy()
        games = self.app.db.all_games()
        if not games:
            lbl = tk.Label(self.body, text="No games played yet.",
                           bg=theme.BG, fg=theme.MUTED, font=theme.body_font(22))
            lbl.pack(pady=20)
            return
        for g in games[:20]:
            line = tk.Label(
                self.body,
                text=f"{g['created_at']}  —  Score {g['score']}/{g['total']}  ·  "
                     f"{g['rating']}",
                bg=theme.BG, fg=theme.TEXT, font=theme.body_font(18), anchor="w")
            line.pack(fill="x", pady=4)
