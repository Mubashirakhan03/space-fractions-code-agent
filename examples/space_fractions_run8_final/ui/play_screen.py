"""Series of fraction questions: the Play Game use case.

Choice buttons for option questions and a typed Entry for decimal questions;
feedback names the expected value of the item just submitted; pause/resume for
the Playing/Paused states.
"""
import tkinter as tk

from ui import theme
from ui.base_screen import make_button, title_label


class PlayScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app
        self._pending_feedback = None

        top = tk.Frame(self, bg=theme.BG)
        top.pack(fill="x", padx=20, pady=(20, 10))
        self.title = title_label(top, "Question", 28)
        self.title.pack(side="left")
        self.progress = tk.Label(top, text="", bg=theme.BG, fg=theme.MUTED,
                                 font=theme.body_font(18))
        self.progress.pack(side="right")

        self.prompt_label = tk.Label(self, text="", bg=theme.BG, fg=theme.ACCENT,
                                     font=theme.title_font(26), wraplength=1000)
        self.prompt_label.pack(pady=(10, 20))

        self.content = tk.Frame(self, bg=theme.BG)
        self.content.pack(expand=True, fill="both", padx=20)

        self.entry = tk.Entry(self.content, font=theme.body_font(22),
                              bg=theme.INPUT_BG, fg=theme.TEXT,
                              relief="solid", bd=2,
                              highlightthickness=2,
                              highlightbackground=theme.INPUT_BORDER,
                              highlightcolor=theme.INPUT_BORDER, width=10)
        self.entry.bind("<Return>", lambda e: self._submit_text())
        self.entry_submit = make_button(self.content, "Check", self._submit_text)

        self.feedback = tk.Label(self, text="", bg=theme.BG, fg=theme.SUCCESS,
                                 font=theme.body_font(20))
        self.feedback.pack(pady=10)

        bottom = tk.Frame(self, bg=theme.BG)
        bottom.pack(fill="x", padx=20, pady=20)
        self.pause_btn = make_button(bottom, "⏸ Pause", self._toggle_pause)
        self.pause_btn.pack(side="left")
        self.menu_btn = make_button(bottom, "Menu", lambda: app.show("menu"))
        self.menu_btn.pack(side="right")

    def on_show(self):
        game = self.app.current_game
        if game is None or game.is_over:
            if game is None:
                game = self.app.service.build_round()
                self.app.current_game = game
            else:
                self.app.show("results")
                return
        self.game = game
        self._render()

    def _render(self):
        self._clear_content()
        q = self.game.current_question
        if q is None:
            self.app.show("results")
            return
        self.prompt_label.config(text=q.prompt)
        self.progress.config(
            text=f"{self.game.current_index + 1} / {self.game.total}   "
                 f"Score: {self.game.score}")
        if q.kind.value == "decimal":
            self._render_text_input()
        else:
            self._render_choices(q)
        self._set_input_focus()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _render_choices(self, q):
        for opt in q.getOptions():
            b = make_button(self.content, opt, lambda o=opt: self._submit(o),
                            bg=theme.SURFACE, activebackground=theme.PRIMARY)
            b.pack(pady=8, fill="x", ipady=6)

    def _render_text_input(self):
        self.entry = tk.Entry(self.content, font=theme.body_font(22),
                              bg=theme.INPUT_BG, fg=theme.TEXT,
                              relief="solid", bd=2, highlightthickness=2,
                              highlightbackground=theme.INPUT_BORDER,
                              highlightcolor=theme.INPUT_BORDER, width=10)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda e: self._submit_text())
        self.entry_submit = make_button(self.content, "Check", self._submit_text)
        self.entry_submit.pack(pady=10)

    def _set_input_focus(self):
        if self.game.current_question and \
                self.game.current_question.kind.value == "decimal":
            self.entry.focus_set()

    def _submit(self, option_text):
        game = self.game
        q = game.current_question
        if q is None:
            return
        expected = q.correct_answer
        correct = game.submit(option_text)
        # message names the expected value of the item JUST submitted
        msg = f"Correct! The answer is {expected}." if correct else \
              f"Wrong — the correct answer is {expected}."
        self.feedback.config(text=msg, fg=theme.SUCCESS if correct else theme.ERROR)
        if game.is_over:
            self.app.db.record_game(game)
            self.after(600, lambda: self.app.show("results"))
        else:
            self._render()

    def _submit_text(self):
        val = self.entry.get().strip()
        if not val:
            return
        self.entry.delete(0, "end")
        self._submit(val)

    def _toggle_pause(self):
        sm = self.game.state_machine
        if sm.state.value == "Paused":
            sm.resume()
            self.pause_btn.config(text="⏸ Pause")
            self.feedback.config(text="Resumed.", fg=theme.SUCCESS)
        else:
            sm.pause()
            self.pause_btn.config(text="▶ Resume")
            self.feedback.config(text="Paused.", fg=theme.ACCENT)
