"""Game screen: prompt + typed or choice input with immediate feedback."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class GameScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BACKGROUND)
        self.app = app

        self.header = tk.Label(self, text="Game", bg=theme.BACKGROUND,
                               fg=theme.ACCENT, font=theme.SUBTITLE_FONT)
        self.header.pack(pady=(20, 10))

        self.prompt_label = tk.Label(self, text="", bg=theme.BACKGROUND,
                                     fg=theme.TEXT, font=theme.CONTENT_FONT,
                                     wraplength=1000, justify="center")
        self.prompt_label.pack(pady=20)

        self.typed_frame = tk.Frame(self, bg=theme.BACKGROUND)
        self.entry = tk.Entry(self.typed_frame, width=14)
        theme.style_entry(self.entry)
        self.entry.pack(side="left", padx=10)
        self.submit_btn = tk.Button(self.typed_frame, text="Submit",
                                    command=self._submit_typed)
        theme.style_button(self.submit_btn)
        self.submit_btn.pack(side="left", padx=10)
        self.entry.bind("<Return>", lambda e: self._submit_typed())

        self.choice_frame = tk.Frame(self, bg=theme.BACKGROUND)
        self.choice_buttons: list[tk.Button] = []

        self.feedback = tk.Label(self, text="", bg=theme.BACKGROUND,
                                 fg=theme.SUCCESS, font=theme.FEEDBACK_FONT)
        self.feedback.pack(pady=10)

        self.pause_btn = tk.Button(self, text="\u23f8 Pause", command=self._pause)
        theme.style_button(self.pause_btn)
        self.pause_btn.pack(side="bottom", pady=20)

    def begin(self):
        self.app.service.play()
        self._render()

    def _render(self):
        q = self.app.service.current_question()
        if q is None:
            self.app.show("results")
            return
        self.prompt_label.configure(text=q.prompt)
        self.feedback.configure(text="")
        self.typed_frame.pack_forget()
        self.choice_frame.pack_forget()
        for b in self.choice_buttons:
            b.destroy()
        self.choice_buttons = []

        if q.options:
            for opt in q.options:
                b = tk.Button(self.choice_frame, text=opt,
                              command=lambda o=opt: self._submit_choice(o))
                theme.style_button(b)
                b.pack(side="left", padx=8, pady=8)
                self.choice_buttons.append(b)
            self.choice_frame.pack(pady=10)
        else:
            self.entry.delete(0, "end")
            self.typed_frame.pack(pady=10)
            self.entry.focus_set()

    def _submit_typed(self):
        value = self.entry.get()
        self.entry.delete(0, "end")
        self._handle(value)

    def _submit_choice(self, opt):
        self._handle(opt)

    def _handle(self, value):
        result = self.app.service.submit(value)
        if result is None:
            return
        if result.correct:
            self.feedback.configure(text=f"Correct! \u2713  ({result.expected})",
                                    fg=theme.SUCCESS)
        else:
            self.feedback.configure(
                text=f"Not quite \u2014 the answer was {result.expected}",
                fg=theme.ERROR)
        self.after(900, self._render)

    def _pause(self):
        self.app.service.pause()
        self.app.show("pause")


__all__ = ["GameScreen"]
