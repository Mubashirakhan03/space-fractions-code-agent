"""Question screen: progress, score, question prompt, 2x2 answer buttons or a
typed input, immediate feedback, Pause button."""
from __future__ import annotations

import tkinter as tk

from ui import theme
from ui.base import BaseScreen


class QuestionScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self._feedback_after = None
        self._next_after = None

        # Top bar
        self.progress_label = tk.Label(
            self.canvas, text="Question 1 of 10", font=self.theme.body(),
            bg=theme.BG, fg=theme.TEXT_MUTED,
        )
        self.score_label = tk.Label(
            self.canvas, text="Score: 0", font=self.theme.body(),
            bg=theme.BG, fg=theme.PRIMARY,
        )
        self.pause_button = tk.Button(
            self.canvas, text="⏸ Pause", command=self._pause,
            font=self.theme.button(), bg=theme.SURFACE, fg=theme.TEXT,
            activebackground=theme.SURFACE_ALT, relief="flat", padx=20, pady=8,
        )
        self.progress_bar = tk.Frame(self.canvas, bg=theme.SURFACE, height=24)
        self.progress_fill = tk.Frame(self.progress_bar, bg=theme.ACCENT, height=24)

        # Middle: prompt + answers
        self.prompt_label = tk.Label(
            self.canvas, text="", font=self.theme.question(),
            bg=theme.BG, fg=theme.TEXT, wraplength=900, justify="center",
        )
        self.feedback_label = tk.Label(
            self.canvas, text="", font=self.theme.heading(),
            bg=theme.BG, fg=theme.SUCCESS,
        )
        self.answer_frame = tk.Frame(self.canvas, bg=theme.BG)
        self.entry = tk.Entry(
            self.answer_frame, font=self.theme.question(), bg=theme.SURFACE_ALT,
            fg=theme.TEXT, insertbackground=theme.TEXT, relief="flat", width=12,
        )
        self.entry.bind("<Return>", lambda e: self._submit_text())

        self.pause_overlay = None

    def on_show(self):
        self._refresh()

    def start_round(self, name, service):
        self._name = name
        self._service = service
        self._refresh()

    def _refresh(self):
        svc = getattr(self, "_service", None)
        if svc is None:
            self.progress_label.config(text="Question 1 of 10")
            self.score_label.config(text="Score: 0")
            self.prompt_label.config(text="")
            self.feedback_label.config(text="")
            return
        q = svc.game.current_question
        if q is None:
            self.app.show("end")
            return
        total = len(svc.game.questions)
        self.progress_label.config(
            text=f"Question {svc.game.current_index + 1} of {total}"
        )
        self.score_label.config(text=f"Score: {svc.game.score}")
        self.prompt_label.config(text=q.get_prompt())
        self.feedback_label.config(text="")
        self._build_answers(q)
        self._update_progress(svc.game.current_index + 1, total)

    def _update_progress(self, current, total):
        frac = current / total if total else 0
        pw = max(self.canvas.winfo_width(), 800)
        self.progress_bar.place(relx=0.5, rely=0.16, anchor="center", width=int(pw * 0.6))
        self.progress_fill.place(relx=0, rely=0, relwidth=frac, relheight=1)

    def _build_answers(self, q):
        for w in self.answer_frame.winfo_children():
            if w is not self.entry:
                w.destroy()
        options = q.get_options()
        if options:
            for i, opt in enumerate(options):
                color = theme.ANSWER_COLORS[i % len(theme.ANSWER_COLORS)]
                b = tk.Button(
                    self.answer_frame, text=opt, font=self.theme.button(),
                    bg=color, fg=theme.BG, relief="flat", padx=24, pady=16,
                    activebackground=theme.PRIMARY, activeforeground=theme.BG,
                    command=lambda o=opt: self._submit_text(o),
                )
                b.grid(row=i // 2, column=i % 2, padx=14, pady=14, sticky="nsew")
            self.entry.pack_forget()
        else:
            self.entry.delete(0, "end")
            self.entry.pack(pady=12, ipady=8)
            self.entry.focus_set()

    def _place_widgets(self):
        return  # layout is done via _refresh / place below

    def _layout_on_show(self):
        self.score_label.place(relx=0.95, rely=0.06, anchor="ne")
        self.pause_button.place(relx=0.05, rely=0.05, anchor="nw")
        self.prompt_label.place(relx=0.5, rely=0.34, anchor="center")
        self.feedback_label.place(relx=0.5, rely=0.5, anchor="center")
        self.answer_frame.place(relx=0.5, rely=0.66, anchor="center")

    def draw_background(self, w, h):
        super().draw_background(w, h)
        self._layout_on_show()
        self._update_progress(
            getattr(getattr(self, "_service", None), "game", None).current_index + 1
            if self._service and self._service.game else 1,
            len(self._service.game.questions) if self._service and self._service.game else 10,
        )

    # -- actions ----------------------------------------------------------
    def _submit_text(self, value=None):
        value = value if value is not None else self.entry.get().strip()
        if not value:
            return
        svc = self._service
        q = svc.game.current_question
        self.entry.delete(0, "end")
        correct = svc.submit(value)
        self.score_label.config(text=f"Score: {svc.game.score}")
        if correct:
            self.feedback_label.config(text="Correct! 🎉", fg=theme.SUCCESS)
        else:
            expected = q.answer
            self.feedback_label.config(
                text=f"Not quite — the answer is {expected}", fg=theme.ERROR,
            )
        if svc.game.state.value == "GameOver":
            self._next_after = self.after(1000, lambda: self.app.show("end"))
        else:
            self._next_after = self.after(1000, self._refresh)

    def _pause(self):
        self._cancel_pending()
        self._service.game.pause()
        self._show_overlay()

    def _show_overlay(self):
        panel = tk.Frame(self, bg=theme.SURFACE, padx=40, pady=40)
        panel.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(panel, text="⏸ Paused", font=self.theme.heading(),
                 bg=theme.SURFACE, fg=theme.PRIMARY).pack(pady=(0, 20))
        resume = tk.Button(
            panel, text="▶ Resume", command=self._resume,
            font=self.theme.button(), bg=theme.PRIMARY, fg=theme.BG,
            relief="flat", padx=30, pady=10,
        )
        resume.pack()
        self.pause_overlay = panel
        self.resume_button = resume

    def _resume(self):
        self._service.game.resume()
        if self.pause_overlay:
            self.pause_overlay.destroy()
            self.pause_overlay = None

    def _cancel_pending(self):
        for attr in ("_feedback_after", "_next_after"):
            aid = getattr(self, attr, None)
            if aid:
                self.after_cancel(aid)
                setattr(self, attr, None)
