"""Admin screen: add/edit/delete questions (Update Questions use case)."""
from __future__ import annotations

import tkinter as tk
import tkinter.messagebox as mb
import uuid

import ui.theme as theme
from questions.model import Question
from ui.screens.base import BaseScreen, make_button


class AdminScreen(BaseScreen):
    def _build(self):
        self.tk_title = tk.Label(
            self.content, text="Admin — Questions", font=theme.SUBTITLE_FONT,
            bg=theme.SPACE_BG, fg=theme.ACCENT_YELLOW,
        )
        self.tk_title.pack(pady=(0, 12))

        # ---- form (two-column grid for compactness) -----------------------
        form = tk.Frame(self.content, bg=theme.SPACE_BG)
        form.pack(pady=(0, 8))

        self.prompt_var = tk.StringVar()
        self.answer_var = tk.StringVar()
        self.options_var = tk.StringVar()
        self.qtype_var = tk.StringVar(value="choice")
        self.edit_id = None

        self._field(form, 0, 0, "Prompt", self.prompt_var, 34)
        self._field(form, 1, 0, "Answer", self.answer_var, 14)
        self._field(form, 2, 0, "Options (comma,sep)", self.options_var, 34)
        self._field(form, 3, 0, "Type", self.qtype_var, 14)

        btn_row = tk.Frame(self.content, bg=theme.SPACE_BG)
        btn_row.pack(pady=(0, 8))
        self.add_btn = make_button(btn_row, "Add", self._add,
                                   bg=theme.ACCENT_GREEN,
                                   font=theme.BODY_FONT)
        self.add_btn.pack(side="left", padx=6)
        self.save_btn = make_button(btn_row, "Save edit", self._save_edit,
                                    bg=theme.PRIMARY, font=theme.BODY_FONT)
        self.save_btn.pack(side="left", padx=6)
        self.clear_btn = make_button(btn_row, "Clear form", self._clear,
                                     bg=theme.ACCENT_CYAN,
                                     font=theme.BODY_FONT)
        self.clear_btn.pack(side="left", padx=6)
        self.back_btn = make_button(btn_row, "Back to menu", self._back,
                                    bg=theme.ERROR, font=theme.BODY_FONT)
        self.back_btn.pack(side="left", padx=6)

        self.feedback = tk.Label(
            self.content, text="", font=theme.SMALL_FONT,
            bg=theme.SPACE_BG, fg=theme.SUCCESS,
        )
        self.feedback.pack(pady=(0, 8))

        # ---- scrollable question list -------------------------------------
        self.list_canvas = tk.Canvas(
            self.content, bg=theme.PANEL, highlightthickness=0, height=260)
        self.scrollbar = tk.Scrollbar(
            self.content, orient="vertical", command=self.list_canvas.yview)
        self.list_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.list_frame = tk.Frame(self.list_canvas, bg=theme.PANEL)
        self.list_window = self.list_canvas.create_window(
            (0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(
                scrollregion=self.list_canvas.bbox("all")))
        self.list_canvas.bind(
            "<Configure>",
            lambda e: self.list_canvas.itemconfigure(
                self.list_window, width=e.width))

        self.list_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _field(self, parent, row, col, label, var, width):
        l = tk.Label(parent, text=label, font=theme.SMALL_FONT,
                     bg=theme.SPACE_BG, fg=theme.MUTED_TEXT, anchor="e")
        l.grid(row=row, column=col * 2, sticky="e", padx=(0, 6), pady=2)
        e = tk.Entry(parent, textvariable=var, font=theme.SMALL_FONT,
                     bg=theme.PANEL, fg=theme.TEXT,
                     insertbackground=theme.TEXT, relief="flat", width=width)
        e.grid(row=row, column=col * 2 + 1, sticky="w", pady=2, ipady=3)

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        questions = self.app.question_repo.all()
        if not questions:
            tk.Label(self.list_frame, text="No questions stored.",
                     font=theme.BODY_FONT, bg=theme.PANEL,
                     fg=theme.MUTED_TEXT).pack(pady=10)
            return
        for q in questions:
            row = tk.Frame(self.list_frame, bg=theme.PANEL)
            row.pack(fill="x", pady=2)
            entry = tk.Button(
                row, text=q.prompt, font=theme.SMALL_FONT, bg=theme.SPACE_BG,
                fg=theme.TEXT, relief="flat", anchor="w", padx=10,
                command=lambda qid=q.id: self._load_edit(qid),
            )
            entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
            delete = make_button(row, "Delete",
                                 lambda qid=q.id: self._delete(qid),
                                 bg=theme.ERROR, font=theme.SMALL_FONT,
                                 padx=12, pady=4)
            delete.pack(side="right")

    def _load_edit(self, qid):
        q = self.app.question_repo.get(qid)
        if q is None:
            return
        self.edit_id = qid
        self.prompt_var.set(q.prompt)
        self.answer_var.set(q.answer)
        self.options_var.set(", ".join(q.options))
        self.qtype_var.set(q.qtype)
        self.feedback.config(text="Editing selected question.",
                             fg=theme.MUTED_TEXT)

    def _add(self):
        q = self._form_to_question(uuid.uuid4().hex)
        if q is None:
            return
        self.app.question_repo.upsert(q)
        self._clear()
        self.feedback.config(text=f"Added question: {q.prompt}",
                             fg=theme.SUCCESS)
        self.refresh()

    def _save_edit(self):
        if not self.edit_id:
            self.feedback.config(
                text="Select a question first to edit it.", fg=theme.ERROR)
            return
        q = self._form_to_question(self.edit_id)
        if q is None:
            return
        self.app.question_repo.upsert(q)
        self._clear()
        self.feedback.config(text=f"Saved question: {q.prompt}",
                             fg=theme.SUCCESS)
        self.refresh()

    def _delete(self, qid):
        q = self.app.question_repo.get(qid)
        if q is None:
            return
        if not mb.askyesno("Delete", f"Delete '{q.prompt}'?"):
            return
        self.app.question_repo.delete(qid)
        self.feedback.config(text=f"Deleted question: {q.prompt}",
                             fg=theme.SUCCESS)
        self.refresh()

    def _form_to_question(self, qid):
        prompt = self.prompt_var.get().strip()
        answer = self.answer_var.get().strip()
        qtype = self.qtype_var.get().strip() or "choice"
        options = [o.strip() for o in self.options_var.get().split(",")
                   if o.strip()]
        if not prompt or not answer:
            self.feedback.config(
                text="Prompt and answer are required.", fg=theme.ERROR)
            return None
        return Question(prompt=prompt, answer=answer, options=options,
                        qtype=qtype, id=qid)

    def _clear(self):
        self.edit_id = None
        self.prompt_var.set("")
        self.answer_var.set("")
        self.options_var.set("")
        self.qtype_var.set("choice")

    def _back(self):
        self.app.show("menu")
