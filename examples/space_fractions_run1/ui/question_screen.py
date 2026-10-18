"""Question flow screen: mixed fraction questions, feedback, progress, pause."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk

from questions.checker import check_answer
from . import theme
from .widgets import SpaceCanvas


class QuestionScreen(tk.Frame):
    name = "question"

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app
        self._current_question = None
        self._pending_advance = None

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        # Top bar: progress + score + pause
        self.topbar = tk.Frame(self.canvas, bg=theme.PANEL)
        self.canvas.create_window(550, 30, window=self.topbar, width=1080)

        self.progress_text = tk.Label(
            self.topbar, text="Question 1 of 10", bg=theme.PANEL, fg=theme.TEXT,
            font=theme.font(18, "bold"),
        )
        self.progress_text.grid(row=0, column=0, padx=20, pady=8, sticky="w")

        self.score_text = tk.Label(
            self.topbar, text="Score: 0", bg=theme.PANEL, fg=theme.YELLOW,
            font=theme.font(18, "bold"),
        )
        self.score_text.grid(row=0, column=1, padx=20, pady=8)

        self.pause_btn = theme.big_button(
            self.topbar, "Pause", command=self._pause, bg=theme.PINK, size=16, pady=4,
        )
        self.pause_btn.grid(row=0, column=2, padx=20, pady=8, sticky="e")

        self.progress = ttk.Progressbar(self.topbar, length=300, maximum=10)
        self.progress.grid(row=0, column=3, padx=20, pady=8)

        self.topbar.grid_columnconfigure(3, weight=1)

        # Question area
        self.question_label = tk.Label(
            self.canvas, text="", bg=theme.BG, fg=theme.TEXT,
            font=theme.font(30, "bold"), wraplength=900, justify="center",
        )
        self.canvas.create_window(550, 180, window=self.question_label)

        self.feedback = tk.Label(
            self.canvas, text="", bg=theme.BG, fg=theme.GREEN,
            font=theme.font(26, "bold"),
        )
        self.canvas.create_window(550, 340, window=self.feedback)

        self.answer_var = tk.StringVar()
        self.entry = tk.Entry(
            self.canvas, textvariable=self.answer_var, font=theme.font(22),
            width=20, justify="center",
        )
        self.canvas.create_window(550, 430, window=self.entry)
        self.entry.bind("<Return>", lambda e: self._submit())

        self.submit_btn = theme.big_button(
            self.canvas, "Submit", command=self._submit, bg=theme.CYAN,
        )
        self.canvas.create_window(550, 520, window=self.submit_btn)

        # Multiple-choice option buttons (2x2 grid)
        self.option_frame = tk.Frame(self.canvas, bg=theme.BG)
        self.canvas.create_window(550, 430, window=self.option_frame)
        self._option_btns = []

    def refresh(self) -> None:
        self.canvas.draw_background()
        self.canvas.twinkle()
        self._cancel_advance()
        self.app.start_round(10)
        self._show_next()

    def _show_next(self) -> None:
        q = self.app.next_question()
        if q is None:
            self._finish()
            return
        self._current_question = q
        idx = self.app.current_index
        total = len(self.app.round_questions)
        self.progress_text.configure(text=f"Question {idx} of {total}")
        self.progress.configure(maximum=total, value=idx - 1)
        self.score_text.configure(text=f"Score: {self.app.game.score}")
        self.feedback.configure(text="")
        self.answer_var.set("")
        self.question_label.configure(text=q.prompt)

        if q.is_multiple_choice():
            self._build_options(q)
            self.entry.place_forget()
            self.option_frame.place(x=550, y=430, anchor="center")
            self.canvas.delete("submit_placeholder")
        else:
            self._clear_options()
            self.option_frame.place_forget()
            self.entry.place(x=550, y=430, anchor="center")
            self.entry.focus_set()

    def _build_options(self, q) -> None:
        self._clear_options()
        self._option_btns = []
        colours = [theme.YELLOW, theme.CYAN, theme.PINK, theme.GREEN]
        for i, opt in enumerate(q.options):
            btn = theme.big_button(
                self.option_frame, opt, command=lambda o=opt: self._answer(o),
                bg=colours[i % len(colours)], width=16, size=18, pady=10,
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self._option_btns.append(btn)

    def _clear_options(self) -> None:
        for b in self._option_btns:
            b.destroy()
        self._option_btns = []

    def _answer(self, value: str) -> None:
        self.answer_var.set(value)
        self._submit()

    def _submit(self) -> None:
        if self._current_question is None:
            return
        answer = self.answer_var.get().strip()
        if not answer:
            self.feedback.configure(text="Type an answer first!", fg=theme.RED)
            return
        correct = check_answer(self._current_question.answer, answer)
        self.app.game.record_answer(correct)
        self.score_text.configure(text=f"Score: {self.app.game.score}")
        if correct:
            self.feedback.configure(text="Correct! 🎉", fg=theme.GREEN)
        else:
            self.feedback.configure(
                text=f"Not quite — the answer is {self._current_question.answer}",
                fg=theme.RED,
            )
        self.answer_var.set("")  # cleared automatically
        self._pending_advance = self.after(1200, self._show_next)

    def _pause(self) -> None:
        try:
            self.app.game.pause()
        except Exception:
            return
        self.app.show("pause")

    def _finish(self) -> None:
        try:
            self.app.game.game_over()
        except Exception:
            pass
        self.app.save_score()
        self.app.show("end")

    def _cancel_advance(self) -> None:
        if self._pending_advance is not None:
            try:
                self.after_cancel(self._pending_advance)
            except tk.TclError:
                pass
            self._pending_advance = None
