"""The question flow screen (Play Game): progress, score, pause, feedback."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk

import ui.theme as theme
from ui.screens.base import BaseScreen, make_button


class QuestionScreen(BaseScreen):
    def __init__(self, master, app):
        self._choice_layout = None
        self._typed_layout = None
        self._input_entry = None
        self._input_var = None
        self._pause_overlay = None
        self._feedback_after = None
        super().__init__(master, app)

    def _build(self):
        # top bar: progress + score
        top = tk.Frame(self.content, bg=theme.SPACE_BG)
        top.pack(fill="x", pady=(0, 20))

        self.progress_label = tk.Label(
            top, text="", font=theme.SUBTITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.MUTED_TEXT,
        )
        self.progress_label.pack(side="left")

        self.score_label = tk.Label(
            top, text="Score: 0", font=theme.SUBTITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.ACCENT_GREEN,
        )
        self.score_label.pack(side="right")

        self.progress = ttk.Progressbar(self.content, maximum=10, length=600)
        self.progress.pack(fill="x", pady=(0, 20))

        self.question_label = tk.Label(
            self.content, text="", font=theme.QUESTION_FONT,
            bg=theme.SPACE_BG, fg=theme.TEXT, wraplength=800, justify="center",
        )
        self.question_label.pack(pady=(0, 20))

        # two alternative layout frames (choice buttons vs typed input)
        self._choice_layout = tk.Frame(self.content, bg=theme.SPACE_BG)
        self._typed_layout = tk.Frame(self.content, bg=theme.SPACE_BG)

        # typed layout
        self._input_var = tk.StringVar()
        self._input_entry = tk.Entry(
            self._typed_layout, textvariable=self._input_var,
            font=theme.INPUT_FONT, bg=theme.PANEL, fg=theme.TEXT,
            insertbackground=theme.TEXT, relief="flat", justify="center",
            width=14,
        )
        self._input_entry.pack(ipady=10, pady=6)
        self._input_entry.bind("<Return>", lambda e: self._submit())
        self._typed_submit = make_button(
            self._typed_layout, "Check", self._submit)
        self._typed_submit.pack(pady=6)

        self.feedback = tk.Label(
            self.content, text="", font=theme.FEEDBACK_FONT,
            bg=theme.SPACE_BG, fg=theme.SUCCESS,
        )
        self.feedback.pack(pady=(16, 0))

        self.pause_btn = make_button(
            self.content, "Pause", self._pause, bg=theme.ACCENT_PINK)
        self.pause_btn.pack(pady=(16, 0))

        self._build_pause_overlay()

    def _build_pause_overlay(self):
        self._pause_overlay = tk.Frame(self, bg="#102040")
        inner = tk.Frame(self._pause_overlay, bg=theme.PANEL)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(inner, text="Game Paused", font=theme.TITLE_FONT,
                 bg=theme.PANEL, fg=theme.ACCENT_YELLOW).pack(pady=20, padx=60)
        resume = make_button(inner, "Resume", self._resume,
                             bg=theme.ACCENT_GREEN)
        resume.pack(pady=20)

    def refresh(self):
        ctl = self.app.controller
        if ctl is None:
            self.question_label.config(text="No game in progress.")
            return
        self._hide_pause()
        self._feedback_after = None
        self._show_question()

    def focus(self):
        if self._input_entry.winfo_ismapped():
            self._input_entry.focus_set()

    def _show_question(self):
        ctl = self.app.controller
        q = ctl.current_question
        if q is None:
            self.app.show("end")
            return
        total = ctl.game.total
        idx = ctl.game.current_index
        self.progress_label.config(text=f"Question {idx + 1} of {total}")
        self.score_label.config(text=f"Score: {ctl.game.score}")
        self.progress.config(maximum=total, value=idx)
        self.question_label.config(text=q.prompt)
        self._clear_choice_buttons()
        self.feedback.config(text="")
        self._input_var.set("")

        if q.is_multiple_choice:
            self._typed_layout.pack_forget()
            self._choice_layout.pack(fill="x")
            self._render_choices(q.options)
        else:
            self._choice_layout.pack_forget()
            self._typed_layout.pack(fill="x")
            self._input_entry.delete(0, "end")
            self._input_entry.focus_set()

    def _clear_choice_buttons(self):
        for w in self._choice_layout.winfo_children():
            w.destroy()

    def _render_choices(self, options):
        palette = [theme.PRIMARY, theme.ACCENT_CYAN,
                   theme.ACCENT_PINK, theme.ACCENT_GREEN]
        for i, opt in enumerate(options):
            btn = tk.Button(
                self._choice_layout, text=opt, font=theme.BUTTON_FONT,
                bg=palette[i % len(palette)], fg=theme.TEXT,
                activebackground=theme.HOVER, activeforeground=theme.TEXT,
                relief="flat", padx=20, pady=16, cursor="hand2",
                command=lambda o=opt: self._submit(o),
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")

    def _submit(self, choice=None):
        ctl = self.app.controller
        if ctl is None or not ctl.state_machine.is_playing:
            return
        if choice is None:
            choice = self._input_var.get()
        correct, expected = ctl.submit_answer(choice)
        self.score_label.config(text=f"Score: {ctl.game.score}")
        if correct:
            self.feedback.config(text="Correct! 🎉", fg=theme.SUCCESS)
        else:
            self.feedback.config(
                text=f"Not quite — the answer is {expected}", fg=theme.ERROR)
        # clear input automatically
        self._input_var.set("")
        if self._input_entry.winfo_exists():
            self._input_entry.delete(0, "end")
        ctl.advance()
        # show next question after a short delay
        self._feedback_after = self.after(900, self._show_question)

    def _pause(self):
        ctl = self.app.controller
        if ctl is None:
            return
        try:
            ctl.pause()
        except Exception:
            return
        self._show_pause()

    def _resume(self):
        ctl = self.app.controller
        if ctl is None:
            return
        ctl.resume()
        self._hide_pause()
        self._input_entry.focus_set()

    def _show_pause(self):
        self._pause_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self._pause_overlay.tkraise()

    def _hide_pause(self):
        self._pause_overlay.place_forget()
