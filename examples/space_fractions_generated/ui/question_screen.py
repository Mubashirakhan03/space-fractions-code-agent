"""Question flow screen: progress, score, question, answer, pause overlay.

Supports multiple-choice (2x2 coloured buttons) and typed answers.
Input is cleared automatically after each answer; next question after ~1s.
"""
from __future__ import annotations

import tkinter as tk

from . import theme
from .space_canvas import SpaceCanvas

NEXT_DELAY_MS = 1000


class QuestionScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BG)
        self.app = app

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        # --- top bar --------------------------------------------------
        self.progress_label = tk.Label(
            self, text="Question 1 of 10", font=theme.BODY_FONT,
            bg=theme.BG, fg=theme.TEXT)
        self.progress_label.place(relx=0.5, rely=0.06, anchor="center")

        self.score_label = tk.Label(
            self, text="Score: 0", font=theme.BODY_FONT,
            bg=theme.BG, fg=theme.PRIMARY)
        self.score_label.place(relx=0.9, rely=0.06, anchor="center")

        self.pause_button = tk.Button(
            self, text="⏸ Pause", font=theme.BUTTON_FONT,
            bg=theme.SURFACE, fg=theme.TEXT, relief="flat",
            activebackground=theme.ACCENT_CYAN,
            command=lambda: self.app.pause_game())
        self.pause_button.place(relx=0.08, rely=0.06, anchor="center")
        self.pause_button.bind("<Enter>", lambda e: self.pause_button.config(bg=theme.ACCENT_CYAN, fg=theme.BG))
        self.pause_button.bind("<Leave>", lambda e: self.pause_button.config(bg=theme.SURFACE, fg=theme.TEXT))

        # --- progress bar --------------------------------------------
        self.bar_canvas = tk.Canvas(self, height=18, bg=theme.SURFACE, highlightthickness=0)
        self.bar_canvas.place(relx=0.5, rely=0.12, anchor="center", relwidth=0.7)
        self.bar_canvas.bind("<Configure>", self._redraw_bar)

        # --- question area -------------------------------------------
        self.question_label = tk.Label(
            self, text="", font=theme.QUESTION_FONT,
            bg=theme.BG, fg=theme.TEXT, wraplength=900)
        self.question_label.place(relx=0.5, rely=0.26, anchor="center")

        self.answer_entry = tk.Entry(
            self, font=theme.INPUT_FONT, bg=theme.SURFACE_ALT, fg=theme.TEXT,
            insertbackground=theme.PRIMARY, relief="flat", justify="center", width=16)
        self.answer_entry.place(relx=0.5, rely=0.36, anchor="center")
        self.answer_entry.bind("<Return>", lambda e: self._submit_typed())

        self.submit_button = tk.Button(
            self, text="Submit", font=theme.BUTTON_FONT,
            bg=theme.SURFACE, fg=theme.TEXT, relief="flat", padx=20, pady=8,
            activebackground=theme.PRIMARY,
            command=self._submit_typed)
        self.submit_button.place(relx=0.5, rely=0.45, anchor="center")
        self.submit_button.bind("<Enter>", lambda e: self.submit_button.config(bg=theme.PRIMARY, fg=theme.BG))
        self.submit_button.bind("<Leave>", lambda e: self.submit_button.config(bg=theme.SURFACE, fg=theme.TEXT))

        # multiple-choice buttons (2x2 grid)
        self.choice_buttons = []
        for i in range(4):
            b = tk.Button(self, text="", font=theme.BUTTON_FONT,
                          bg=theme.SURFACE, fg=theme.TEXT, relief="flat", wraplength=220,
                          width=16, pady=16, command=lambda idx=i: self._submit_choice(idx))
            self.choice_buttons.append(b)

        # --- feedback ------------------------------------------------
        self.feedback_label = tk.Label(
            self, text="", font=theme.BODY_FONT, bg=theme.BG, fg=theme.SUCCESS)
        self.feedback_label.place(relx=0.5, rely=0.62, anchor="center")

        # --- pause overlay -------------------------------------------
        self._overlay = None
        self._after_id = None

    # -- progress bar -------------------------------------------------
    def _redraw_bar(self, event=None):
        self.bar_canvas.delete("all")
        w = self.bar_canvas.winfo_width()
        if w <= 1:
            return
        game = self.app.game
        if game and game.total:
            frac = (game.index) / game.total
        else:
            frac = 0.0
        self.bar_canvas.create_rectangle(0, 0, w * frac, 18, fill=theme.PRIMARY, outline="")

    # -- rendering ----------------------------------------------------
    def _render_question(self):
        game = self.app.game
        if game is None or game.total == 0:
            self.progress_label.config(text="Question 1 of 10")
            self.score_label.config(text="Score: 0")
            self.question_label.config(text="No questions available yet.")
            self.feedback_label.config(text="")
            return
        q = game.current_question()
        if q is None:
            self.app.show("end")
            return
        self.progress_label.config(text=f"Question {game.index + 1} of {game.total}")
        self.score_label.config(text=f"Score: {game.score}")
        self.question_label.config(text=q.getPrompt())
        self.feedback_label.config(text="")
        self.answer_entry.delete(0, tk.END)
        self._redraw_bar()

        use_choices = q.is_multiple_choice()
        # hide/show typed input vs choices
        if use_choices:
            self.answer_entry.place_forget()
            self.submit_button.place_forget()
            opts = q.getOptions()
            for i, btn in enumerate(self.choice_buttons):
                if i < len(opts):
                    btn.config(text=opts[i], state="normal")
                    col = i % 2
                    row = i // 2
                    btn.place(relx=0.32 + col * 0.36, rely=0.36 + row * 0.13, anchor="center")
                else:
                    btn.place_forget()
        else:
            for btn in self.choice_buttons:
                btn.place_forget()
            self.answer_entry.place(relx=0.5, rely=0.36, anchor="center")
            self.submit_button.place(relx=0.5, rely=0.45, anchor="center")
            self.answer_entry.focus_set()

    def _submit_typed(self):
        text = self.answer_entry.get().strip()
        if not text:
            return
        self._evaluate(text)

    def _submit_choice(self, idx):
        text = self.choice_buttons[idx].cget("text")
        self._evaluate(text)

    def _evaluate(self, answer_text):
        game = self.app.game
        if game is None or game.is_finished():
            return
        correct = game.submit_answer(answer_text)
        q = game.current_question() or game.questions[-1]
        if correct:
            self.feedback_label.config(text="Correct! 🎉", fg=theme.SUCCESS)
        else:
            self.feedback_label.config(
                text=f"Not quite — the answer is {q.answer}", fg=theme.ERROR)
        self.score_label.config(text=f"Score: {game.score}")
        self.answer_entry.delete(0, tk.END)
        self._redraw_bar()
        self._cancel_next()
        self._after_id = self.after(NEXT_DELAY_MS, self._next)

    def _next(self):
        if self.app.game and not self.app.game.is_finished():
            self._render_question()
        else:
            self.app.finish_game()
            self.app.show("end")

    def _cancel_next(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    # -- pause overlay ------------------------------------------------
    def show_pause_overlay(self, paused=True):
        if paused and self._overlay is None:
            self._overlay = tk.Frame(self, bg=theme.BG)
            self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            label = tk.Label(self._overlay, text="⏸ Paused", font=theme.SUBTITLE_FONT,
                             bg=theme.BG, fg=theme.PRIMARY)
            label.place(relx=0.5, rely=0.4, anchor="center")
            resume = tk.Button(self._overlay, text="▶ Resume", font=theme.BUTTON_FONT,
                               bg=theme.SURFACE, fg=theme.TEXT, relief="flat", padx=24, pady=10,
                               command=lambda: self.app.resume_game())
            resume.place(relx=0.5, rely=0.52, anchor="center")
            quit_btn = tk.Button(self._overlay, text="Quit to Menu", font=theme.BUTTON_FONT,
                                 bg=theme.SURFACE, fg=theme.ERROR, relief="flat", padx=24, pady=10,
                                 command=lambda: self.app.show("menu"))
            quit_btn.place(relx=0.5, rely=0.62, anchor="center")
        elif not paused and self._overlay is not None:
            self._overlay.destroy()
            self._overlay = None

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self._render_question()
        self.show_pause_overlay(False)

    def cancel(self):
        self._cancel_next()
