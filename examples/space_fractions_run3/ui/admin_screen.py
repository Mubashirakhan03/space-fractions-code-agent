"""Admin screen (Update Questions use case): add / edit / delete questions."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from ui import theme
from ui.base import BaseScreen
from questions.question import Question


class AdminScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self._selection = None
        panel = tk.Frame(self, bg=theme.SURFACE, padx=30, pady=24)
        panel.place(relx=0.5, rely=0.08, anchor="n")
        self.title_label = tk.Label(
            panel, text="⚙ Admin — Questions", font=self.theme.title(),
            bg=theme.SURFACE, fg=theme.PRIMARY,
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 12))

        # Question list
        self.listbox = tk.Listbox(
            panel, height=12, width=50, font=self.theme.small(),
            bg=theme.SURFACE_ALT, fg=theme.TEXT, relief="flat",
            exportselection=False,
        )
        self.listbox.grid(row=1, column=0, rowspan=6, padx=(0, 16), sticky="n")
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        self.type_label = tk.Label(panel, text="Type", font=self.theme.small(), bg=theme.SURFACE, fg=theme.TEXT_MUTED)
        self.type_label.grid(row=1, column=1, sticky="w")
        self.type_entry = tk.Entry(panel, font=self.theme.small(), bg=theme.SURFACE_ALT, fg=theme.TEXT, width=22)
        self.type_entry.grid(row=2, column=1, pady=(2, 6))

        self.prompt_label = tk.Label(panel, text="Prompt", font=self.theme.small(), bg=theme.SURFACE, fg=theme.TEXT_MUTED)
        self.prompt_label.grid(row=3, column=1, sticky="w")
        self.prompt_entry = tk.Entry(panel, font=self.theme.small(), bg=theme.SURFACE_ALT, fg=theme.TEXT, width=22)
        self.prompt_entry.grid(row=4, column=1, pady=(2, 6))

        self.options_label = tk.Label(panel, text="Options (comma-separated)", font=self.theme.small(), bg=theme.SURFACE, fg=theme.TEXT_MUTED)
        self.options_label.grid(row=5, column=1, sticky="w")
        self.options_entry = tk.Entry(panel, font=self.theme.small(), bg=theme.SURFACE_ALT, fg=theme.TEXT, width=22)
        self.options_entry.grid(row=6, column=1, pady=(2, 6))

        self.answer_label = tk.Label(panel, text="Answer", font=self.theme.small(), bg=theme.SURFACE, fg=theme.TEXT_MUTED)
        self.answer_label.grid(row=7, column=1, sticky="w")
        self.answer_entry = tk.Entry(panel, font=self.theme.small(), bg=theme.SURFACE_ALT, fg=theme.TEXT, width=22)
        self.answer_entry.grid(row=8, column=1, pady=(2, 6))

        btns = tk.Frame(panel, bg=theme.SURFACE)
        btns.grid(row=9, column=0, columnspan=2, pady=10)
        self.save_button = tk.Button(btns, text="Save", command=self._save,
                                     font=self.theme.button(), bg=theme.PRIMARY, fg=theme.BG,
                                     relief="flat", padx=18, pady=6)
        self.save_button.pack(side="left", padx=8)
        self.delete_button = tk.Button(btns, text="Delete", command=self._delete,
                                       font=self.theme.button(), bg=theme.ERROR, fg=theme.BG,
                                       relief="flat", padx=18, pady=6)
        self.delete_button.pack(side="left", padx=8)
        self.new_button = tk.Button(btns, text="New", command=self._new,
                                    font=self.theme.button(), bg=theme.ACCENT, fg=theme.BG,
                                    relief="flat", padx=18, pady=6)
        self.new_button.pack(side="left", padx=8)
        self.menu_button = tk.Button(btns, text="Menu", command=lambda: self.app.show("menu"),
                                     font=self.theme.button(), bg=theme.SURFACE_ALT, fg=theme.TEXT,
                                     relief="flat", padx=18, pady=6)
        self.menu_button.pack(side="left", padx=8)

    def on_show(self):
        self._reload()

    def _reload(self):
        self.listbox.delete(0, "end")
        self._questions = self.app.question_repo.list_all(self.app.conn)
        for q in self._questions:
            self.listbox.insert("end", f"{q.id}  [{q.qtype}]  {q.prompt[:30]}")

    def _on_select(self, _event):
        sel = self.listbox.curselection()
        if not sel:
            return
        q = self._questions[sel[0]]
        self._selection = q
        self.type_entry.delete(0, "end")
        self.type_entry.insert(0, q.qtype)
        self.prompt_entry.delete(0, "end")
        self.prompt_entry.insert(0, q.prompt)
        self.options_entry.delete(0, "end")
        self.options_entry.insert(0, ",".join(q.options))
        self.answer_entry.delete(0, "end")
        self.answer_entry.insert(0, q.answer)

    def _new(self):
        self._selection = None
        for e in (self.type_entry, self.prompt_entry, self.options_entry, self.answer_entry):
            e.delete(0, "end")

    def _save(self):
        qtype = self.type_entry.get().strip() or "equivalent"
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showwarning("Admin", "Prompt is required.")
            return
        options = [o.strip() for o in self.options_entry.get().split(",") if o.strip()]
        qid = self._selection.id if self._selection else f"q{self.app.question_repo.count(self.app.conn) + 1}"
        q = Question(
            id=qid, prompt=prompt, options=options,
            answer=self.answer_entry.get().strip(), qtype=qtype,
        )
        self.app.question_repo.upsert(self.app.conn, q)
        self.app.conn.commit()
        self._reload()

    def _delete(self):
        if not self._selection:
            messagebox.showwarning("Admin", "Select a question to delete.")
            return
        qid = self._selection.id
        if not messagebox.askyesno("Delete question", f"Delete question {qid}?"):
            return
        self.app.question_repo.delete(self.app.conn, qid)
        self.app.conn.commit()
        self._selection = None
        self._reload()
