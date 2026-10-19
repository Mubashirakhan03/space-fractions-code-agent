"""Admin screen (Update Questions use case): list, add, edit, delete."""
from __future__ import annotations

import tkinter as tk

from question.question import Question, QuestionKind
from ui import theme


class AdminScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=theme.BACKGROUND)
        self.app = app
        self.editing_id = None

        self.title = tk.Label(self, text="Admin: Update Questions",
                              bg=theme.BACKGROUND, fg=theme.ACCENT,
                              font=theme.SUBTITLE_FONT)
        self.title.pack(pady=(10, 4))

        form = tk.Frame(self, bg=theme.BACKGROUND)
        form.pack(pady=2)
        self.prompt_var = tk.StringVar()
        self.correct_var = tk.StringVar()
        self.options_var = tk.StringVar()
        self.kind_var = tk.StringVar(value="compare")
        self._make_label_entry(form, "Prompt", 0, self.prompt_var)
        self._make_label_entry(form, "Correct value", 1, self.correct_var)
        self._make_label_entry(form, "Options (comma separated)", 2, self.options_var)
        self._make_label_entry(form, "Kind", 3, self.kind_var)

        self.feedback = tk.Label(self, text="", bg=theme.BACKGROUND,
                                 fg=theme.ERROR, font=theme.SMALL_FONT)
        self.feedback.pack(pady=2)

        btnrow = tk.Frame(self, bg=theme.BACKGROUND)
        btnrow.pack(pady=2)
        self.add_btn = tk.Button(btnrow, text="Add Question", command=self._add)
        theme.style_button(self.add_btn)
        self.add_btn.pack(side="left", padx=6)
        self.save_btn = tk.Button(btnrow, text="Save Edit", command=self._save)
        theme.style_button(self.save_btn)
        self.save_btn.pack(side="left", padx=6)

        self.listbox = tk.Listbox(self, bg=theme.SURFACE, fg=theme.TEXT,
                                  font=theme.SMALL_FONT, height=6,
                                  selectbackground=theme.PRIMARY)
        self.listbox.pack(pady=4, fill="both", expand=True, padx=30)

        editrow = tk.Frame(self, bg=theme.BACKGROUND)
        editrow.pack(pady=2)
        self.edit_btn = tk.Button(editrow, text="Load Selected", command=self._load)
        theme.style_button(self.edit_btn)
        self.edit_btn.pack(side="left", padx=6)
        self.delete_btn = tk.Button(editrow, text="Delete Selected", command=self._delete)
        theme.style_button(self.delete_btn)
        self.delete_btn.configure(bg=theme.ERROR, activebackground=theme.ERROR)
        self.delete_btn.pack(side="left", padx=6)

        self.back_btn = tk.Button(self, text="Back to Menu",
                                  command=lambda: self.app.show("menu"))
        theme.style_button(self.back_btn)
        self.back_btn.pack(pady=6)

    def _make_label_entry(self, parent, label, row, var):
        tk.Label(parent, text=label, bg=theme.BACKGROUND, fg=theme.MUTED,
                 font=theme.SMALL_FONT).grid(row=row, column=0, sticky="e", padx=6, pady=2)
        e = tk.Entry(parent, textvariable=var, width=40)
        theme.style_entry(e)
        e.grid(row=row, column=1, padx=6, pady=2)

    def begin(self):
        self._refresh()

    def _refresh(self):
        self.listbox.delete(0, "end")
        for q in self.app.repo.list_all():
            self.listbox.insert("end", f"{q.id} | {q.prompt}")

    def _selected_id(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        text = self.listbox.get(sel[0])
        return text.split(" | ", 1)[0]

    def _clear_form(self):
        self.editing_id = None
        for var in (self.prompt_var, self.correct_var, self.options_var):
            var.set("")
        self.kind_var.set("compare")
        self.feedback.configure(text="")

    def _make_question(self) -> Question:
        options = [o.strip() for o in self.options_var.get().split(",") if o.strip()]
        kind = self.kind_var.get().strip().lower() or "compare"
        try:
            kind_enum = QuestionKind(kind)
        except ValueError:
            kind_enum = QuestionKind.COMPARE
        q = Question(
            id=self.editing_id or f"q-{len(self.app.repo.list_all()) + 1}",
            prompt=self.prompt_var.get().strip(),
            correct=self.correct_var.get().strip(),
            options=options,
            kind=kind_enum,
        )
        return q

    def _add(self):
        q = self._make_question()
        errors = self.app.repo.add(q)
        if errors:
            self.feedback.configure(text="; ".join(errors), fg=theme.ERROR)
            return
        self.feedback.configure(text=f"Added: {q.prompt}", fg=theme.SUCCESS)
        self._clear_form()
        self._refresh()

    def _load(self):
        qid = self._selected_id()
        if not qid:
            self.feedback.configure(text="Select a question first", fg=theme.ERROR)
            return
        for q in self.app.repo.list_all():
            if q.id == qid:
                self.editing_id = q.id
                self.prompt_var.set(q.prompt)
                self.correct_var.set(q.correct)
                self.options_var.set(", ".join(q.options))
                self.kind_var.set(q.kind.value)
                self.feedback.configure(text=f"Editing {q.id}", fg=theme.MUTED)
                return

    def _save(self):
        if not self.editing_id:
            self.feedback.configure(text="Load a question to edit first", fg=theme.ERROR)
            return
        q = self._make_question()
        errors = self.app.repo.update(q)
        if errors:
            self.feedback.configure(text="; ".join(errors), fg=theme.ERROR)
            return
        self.feedback.configure(text=f"Saved: {q.prompt}", fg=theme.SUCCESS)
        self._clear_form()
        self._refresh()

    def _delete(self):
        qid = self._selected_id()
        if not qid:
            self.feedback.configure(text="Select a question first", fg=theme.ERROR)
            return
        removed = self.app.repo.delete(qid)
        if removed:
            self.feedback.configure(text=f"Deleted {qid}", fg=theme.SUCCESS)
        else:
            self.feedback.configure(text="Could not delete", fg=theme.ERROR)
        self._clear_form()
        self._refresh()


__all__ = ["AdminScreen"]
