"""Question screen: the series of fraction questions (Play Game use case)."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.screens.base import BaseScreen
from game.state_machine import State


class QuestionScreen(BaseScreen):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "question_screen")

        self.header = theme.make_label(self, "", theme.FEEDBACK_SIZE, theme.MUTED)
        self.header.pack(pady=(16, 4))

        self.prompt_label = theme.make_label(self, "", theme.CONTENT_SIZE + 2,
                                             theme.TEXT, "bold",
                                             wraplength=900)
        self.prompt_label.pack(pady=(8, 16))

        # two layout containers: choice buttons vs typed input
        self.choices_frame = tk.Frame(self, bg=theme.BG)
        self.input_frame = tk.Frame(self, bg=theme.BG)

        self.feedback_label = theme.make_label(self, "", theme.FEEDBACK_SIZE, theme.TEXT, "bold")
        self.feedback_label.pack(pady=10)

        self.controls = tk.Frame(self, bg=theme.BG)
        self.controls.pack(pady=10)

        self.pause_btn = theme.make_button(self.controls, "⏸ Pause", self.pause_or_resume,
                                           bg=theme.SURFACE)
        self.pause_btn.pack(side="left", padx=10)
        self.quit_btn = theme.make_button(self.controls, "Exit to Menu", self.quit_to_menu,
                                          bg=theme.SURFACE)
        self.quit_btn.pack(side="left", padx=10)

        self._choice_buttons = []
        self._entry = None
        self._submit_btn = None
        self._paused = False

    def on_show(self) -> None:
        self.app.start_round()   # ensures a fresh round if none exists yet
        self._paused = False
        self.pause_btn.config(text="⏸ Pause")
        self.render_question()

    def render_question(self) -> None:
        rnd = self.app.service.current_round
        if rnd is None:
            self.app.start_round()
            rnd = self.app.service.current_round
        q = rnd.current
        self.clear_answer_widgets()

        self.header.config(text=f"Question {rnd.index + 1} of {rnd.total}   ·   "
                                f"Score: {rnd.correct}  ✓  |  {rnd.wrong} ✗")
        self.prompt_label.config(text=q.prompt)
        self.feedback_label.config(text="")

        if q.has_choices():
            self.choices_frame.pack(fill="both", expand=True)
            self._choice_buttons = []
            for opt in q.choices:
                btn = theme.make_button(self.choices_frame, opt,
                                        lambda o=opt: self.choose(o))
                btn.pack(pady=6)
                self._choice_buttons.append(btn)
        else:
            self.input_frame.pack(fill="both", expand=True, pady=20)
            self._entry = theme.make_entry(self.input_frame)
            self._entry.pack(side="left", padx=10)
            self._submit_btn = theme.make_button(self.input_frame, "Check",
                                                 self.submit_typed)
            self._submit_btn.pack(side="left", padx=10)
            self._entry.focus_set()
            self._entry.bind("<Return>", lambda _e: self.submit_typed())

    def clear_answer_widgets(self) -> None:
        for w in self.choices_frame.winfo_children():
            w.destroy()
        for w in self.input_frame.winfo_children():
            w.destroy()
        self.choices_frame.pack_forget()
        self.input_frame.pack_forget()
        self._choice_buttons = []
        self._entry = None
        self._submit_btn = None

    def choose(self, option: str) -> None:
        self._handle_submit(option)

    def submit_typed(self) -> None:
        if self._entry is None:
            return
        value = self._entry.get()
        self._entry.delete(0, "end")   # clear input after each submission
        self._handle_submit(value)

    def _handle_submit(self, answer: str) -> None:
        rnd = self.app.service.current_round
        if rnd is None or rnd.finished:
            return
        if self._paused:
            return
        expected = rnd.current.correct_value
        finished = rnd.submit(answer)
        if rnd.last_was_correct:
            self.feedback_label.config(
                text=f"✅ Correct! The answer was {expected}.",
                fg=theme.SUCCESS)
        else:
            self.feedback_label.config(
                text=f"❌ Not quite — the answer was {expected}.",
                fg=theme.ERROR)
        if finished:
            self.app.finish_round()
            self.after(700, lambda: self.app.show("ending_scene"))
        else:
            self.after(650, self.render_question)

    def pause_or_resume(self) -> None:
        rnd = self.app.service.current_round
        if rnd is None:
            return
        if self._paused:
            rnd.state_machine.resume()
            self._paused = False
            self.pause_btn.config(text="⏸ Pause")
            self.feedback_label.config(text="", fg=theme.TEXT)
        else:
            rnd.state_machine.pause()
            self._paused = True
            self.pause_btn.config(text="▶ Resume")
            self.feedback_label.config(text="Game paused. Press Resume to continue.",
                                       fg=theme.ACCENT)

    def quit_to_menu(self) -> None:
        self.app.show("main_menu")
