"""Admin screen (Update Questions use case): PIN-gated add/edit/delete."""
from __future__ import annotations

import uuid
import tkinter as tk

from admin import Admin
from questions.question import Question, VALID_TYPES
from . import theme
from .widgets import SpaceCanvas, SpacePanel


class AdminScreen(tk.Frame):
    name = "admin"

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app
        self._unlocked = False

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.panel = SpacePanel(self.canvas)
        self.panel.place(relx=0.5, rely=0.5, anchor="center")

        # PIN gate widgets
        self.gate_title = tk.Label(
            self.panel, text="Admin — enter PIN", bg=theme.PANEL, fg=theme.YELLOW,
            font=theme.font(26, "bold"),
        )
        self.gate_title.pack(pady=(20, 10))

        self.pin_var = tk.StringVar()
        self.pin_entry = tk.Entry(
            self.panel, textvariable=self.pin_var, font=theme.font(20),
            width=20, show="*", justify="center",
        )
        self.pin_entry.pack(pady=6, ipady=6)
        self.pin_entry.bind("<Return>", lambda e: self._unlock())

        self.gate_feedback = tk.Label(
            self.panel, text="", bg=theme.PANEL, fg=theme.RED, font=theme.font(16),
        )
        self.gate_feedback.pack(pady=(0, 6))

        self.unlock_btn = theme.big_button(
            self.panel, "Unlock", command=self._unlock, bg=theme.CYAN, width=14,
        )
        self.unlock_btn.pack(pady=6)

        self.back_btn = theme.big_button(
            self.panel, "Back", command=lambda: self.app.show("menu"),
            bg=theme.MUTED, width=14,
        )
        self.back_btn.pack(pady=(6, 20))

        # Edit form widgets (hidden until unlocked)
        self.edit_frame = tk.Frame(self.panel, bg=theme.PANEL)

        self.e_prompt = self._field(self.edit_frame, "Prompt")
        self.e_type = self._field(self.edit_frame, "Type (equivalent/compare/add_subtract/simplify)")
        self.e_options = self._field(self.edit_frame, "Options (comma-separated, empty for typed)")
        self.e_answer = self._field(self.edit_frame, "Answer (e.g. 1/2)")

        self.form_feedback = tk.Label(
            self.edit_frame, text="", bg=theme.PANEL, fg=theme.GREEN,
            font=theme.font(16),
        )
        self.form_feedback.pack(pady=(0, 6))

        btns = tk.Frame(self.edit_frame, bg=theme.PANEL)
        btns.pack(pady=6)
        self.add_btn = theme.big_button(
            btns, "Add Question", command=self._add, bg=theme.GREEN, size=16, pady=8,
        )
        self.add_btn.pack(side="left", padx=6)
        self.delete_btn = theme.big_button(
            btns, "Delete by ID", command=self._delete, bg=theme.RED, fg=theme.TEXT,
            size=16, pady=8,
        )
        self.delete_btn.pack(side="left", padx=6)
        self.done_btn = theme.big_button(
            btns, "Done", command=lambda: self.app.show("menu"), bg=theme.MUTED,
            size=16, pady=8,
        )
        self.done_btn.pack(side="left", padx=6)

        self.count_label = tk.Label(
            self.edit_frame, text="", bg=theme.PANEL, fg=theme.MUTED,
            font=theme.font(14),
        )
        self.count_label.pack(pady=(4, 16))

    def _field(self, parent, label_text):
        row = tk.Frame(parent, bg=theme.PANEL)
        row.pack(fill="x", padx=16, pady=4)
        lbl = tk.Label(row, text=label_text, bg=theme.PANEL, fg=theme.MUTED,
                       font=theme.font(13), anchor="w")
        lbl.pack(fill="x")
        var = tk.StringVar()
        entry = tk.Entry(row, textvariable=var, font=theme.font(16), width=50)
        entry.pack(fill="x", ipady=4)
        return var

    def refresh(self) -> None:
        self.canvas.draw_background()
        self.canvas.twinkle()
        self._unlocked = False
        self.edit_frame.pack_forget()
        self.pin_var.set("")
        self.gate_feedback.configure(text="")
        self.pin_entry.focus_set()

    def _unlock(self) -> None:
        pin = self.pin_var.get().strip()
        if Admin.verify_pin(pin):
            self._unlocked = True
            self.pin_var.set("")
            self.gate_feedback.configure(text="")
            self.edit_frame.pack(fill="x", padx=10, pady=10)
            self._refresh_count()
        else:
            self.gate_feedback.configure(text="Incorrect PIN.", fg=theme.RED)

    def _add(self) -> None:
        prompt = self.e_prompt.get().strip()
        qtype = self.e_type.get().strip()
        options = self.e_options.get().strip()
        answer = self.e_answer.get().strip()
        if not prompt or not qtype or not answer:
            self.form_feedback.configure(
                text="Prompt, type and answer are required.", fg=theme.RED
            )
            return
        if qtype not in VALID_TYPES:
            self.form_feedback.configure(text=f"Invalid type: {qtype}", fg=theme.RED)
            return
        opts = [o.strip() for o in options.split(",") if o.strip()] if options else []
        q = Question(id=uuid.uuid4().hex[:8], prompt=prompt, type=qtype,
                     options=opts, answer=answer)
        self.app.questions.add(q)
        self._clear_form()
        self.form_feedback.configure(text="Question added!", fg=theme.GREEN)
        self._refresh_count()

    def _delete(self) -> None:
        qid = self.e_prompt.get().strip()
        if not qid:
            self.form_feedback.configure(
                text="Enter the question ID in the Prompt field to delete.", fg=theme.RED
            )
            return
        if self.app.questions.get(qid) is None:
            self.form_feedback.configure(text=f"No question with ID {qid!r}.", fg=theme.RED)
            return
        self.app.questions.delete(qid)
        self._clear_form()
        self.form_feedback.configure(text="Question deleted!", fg=theme.GREEN)
        self._refresh_count()

    def _clear_form(self) -> None:
        for v in (self.e_prompt, self.e_type, self.e_options, self.e_answer):
            v.set("")

    def _refresh_count(self) -> None:
        self.count_label.configure(
            text=f"Question ID format: seed ids like eq-01 or an 8-character id like 3f2a9b1c. "
                 f"Total questions: {self.app.questions.count()}"
        )
