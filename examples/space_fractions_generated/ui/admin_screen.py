"""Admin screen: add / edit / delete questions (Update Questions use case)."""
from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, messagebox

from admin.admin import Admin
from questions.question import Question, QType
from . import theme
from .space_canvas import SpaceCanvas

QTYPES = [q.value for q in QType]


class AdminScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BG)
        self.app = app
        self.admin = Admin(repository=QuestionRepository_from_app(app))

        self.canvas = SpaceCanvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self, text="⚙️ Admin — Manage Questions", font=theme.SUBTITLE_FONT,
            bg=theme.BG, fg=theme.PRIMARY)
        self.title_label.place(relx=0.5, rely=0.08, anchor="center")

        self.list_frame = tk.Frame(self, bg=theme.SURFACE)
        self.list_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.6)

        self.add_button = tk.Button(self, text="➕ Add Question", font=theme.BUTTON_FONT,
                                    bg=theme.SURFACE, fg=theme.TEXT, relief="flat", padx=16, pady=8,
                                    command=self._add_question)
        self.add_button.place(relx=0.3, rely=0.88, anchor="center")

        self.back_button = tk.Button(self, text="← Menu", font=theme.BUTTON_FONT,
                                     bg=theme.SURFACE, fg=theme.TEXT, relief="flat", padx=16, pady=8,
                                     command=lambda: app.show("menu"))
        self.back_button.place(relx=0.7, rely=0.88, anchor="center")

    def _refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        questions = self.admin.list_questions()
        if not questions:
            lbl = tk.Label(self.list_frame, text="No questions,", font=theme.BODY_FONT,
                           bg=theme.SURFACE, fg=theme.TEXT_MUTED)
            lbl.pack(expand=True)
            return
        for q in questions:
            row = tk.Frame(self.list_frame, bg=theme.SURFACE)
            row.pack(fill="x", padx=10, pady=2)
            txt = f"{q.id} [{q.qtype.value}] {q.getPrompt()}"
            lbl = tk.Label(row, text=txt, font=theme.SMALL_FONT,
                           bg=theme.SURFACE, fg=theme.TEXT, anchor="w")
            lbl.pack(side="left", expand=True, fill="x")
            edit_btn = tk.Button(row, text="Edit", font=theme.SMALL_FONT,
                                 bg=theme.SURFACE_ALT, fg=theme.TEXT, relief="flat",
                                 command=lambda qid=q.id: self._edit_question(qid))
            edit_btn.pack(side="left", padx=2)
            del_btn = tk.Button(row, text="✕", font=theme.SMALL_FONT,
                                bg=theme.SURFACE_ALT, fg=theme.ERROR, relief="flat",
                                command=lambda qid=q.id: self._delete_question(qid))
            del_btn.pack(side="left", padx=2)

    def _add_question(self):
        prompt = simpledialog.askstring("Add Question", "Question prompt:", parent=self)
        if not prompt:
            return
        answer = simpledialog.askstring("Add Question", "Correct answer (e.g. 3/4):", parent=self)
        if not answer:
            return
        qtype = simpledialog.askstring(
            "Add Question", f"Type ({', '.join(QTYPES)}):", parent=self,
            initialvalue=QTYPES[0]) or QTYPES[0]
        if qtype not in QTYPES:
            qtype = QTYPES[0]
        q = Question(id=self.admin.list_questions() and "q" + str(len(self.admin.list_questions()) + 1),
                     prompt=prompt, answer=answer, qtype=qtype)
        self.admin.add_question(q)
        self._refresh()

    def _edit_question(self, qid):
        q = next((x for x in self.admin.list_questions() if x.id == qid), None)
        if not q:
            return
        prompt = simpledialog.askstring("Edit Question", "Prompt:", parent=self, initialvalue=q.getPrompt())
        if prompt is None:
            return
        answer = simpledialog.askstring("Edit Question", "Answer:", parent=self, initialvalue=str(q.answer))
        if answer is None:
            return
        new_q = Question(id=qid, prompt=prompt, answer=answer, qtype=q.qtype.value,
                         options=q.getOptions() or None)
        self.admin.add_question(new_q)
        self._refresh()

    def _delete_question(self, qid):
        if messagebox.askyesno("Delete", f"Delete {qid}?", parent=self):
            self.admin.delete_question(qid)
            self._refresh()

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self._refresh()


def QuestionRepository_from_app(app):
    from questions.repository import QuestionRepository
    return QuestionRepository(db_path=app.db_path)
