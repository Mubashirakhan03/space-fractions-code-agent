"""Admin screen: list + add/edit/delete questions."""
import tkinter as tk
from tkinter import messagebox

from questions.question import Question
from ui import theme
from ui.base_screen import BaseScreen


class AdminScreen(BaseScreen):
    """Manage the persisted question pool. The add/edit form includes a field
    for every attribute (prompt, correct value, kind, choices)."""

    def __init__(self, master, app):
        super().__init__(master, app)
        self._editing = None  # question id being edited
        self.title_label = tk.Label(
            self.body, text="Update Questions", font=theme.HEADING,
            fg=theme.ACCENT, bg=theme.BG,
        )
        self.title_label.pack(pady=(0, 8))

        self.listbox = tk.Listbox(
            self.body, font=theme.SMALL, bg=theme.SURFACE, fg=theme.TEXT,
            relief="flat", height=8, width=70,
        )
        self.listbox.pack(pady=(0, 8))
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        self.form = tk.Frame(self.body, bg=theme.BG)
        self.form.pack(pady=8)

        self._build_form()

        self.feedback_label = tk.Label(
            self.body, text="", font=theme.SMALL, bg=theme.BG,
        )
        self.feedback_label.pack(pady=(4, 8))

        self.actions = tk.Frame(self.body, bg=theme.BG)
        self.actions.pack()
        self.back_btn = self.make_button("Back to Menu", self._back, primary=False)
        self.back_btn.pack(pady=(12, 0))

    def _build_form(self):
        for w in self.form.winfo_children():
            w.destroy()
        bg = theme.BG
        self.prompt_label = tk.Label(self.form, text="Prompt:", font=theme.SMALL,
                                     fg=theme.TEXT, bg=bg)
        self.prompt_label.grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.prompt_entry = tk.Entry(self.form, font=theme.SMALL, width=40,
                                     bg=theme.SURFACE, fg=theme.TEXT,
                                     insertbackground=theme.TEXT, relief="flat")
        self.prompt_entry.grid(row=0, column=1, sticky="w", padx=6, pady=4, ipady=4)

        self.correct_label = tk.Label(self.form, text="Correct value:", font=theme.SMALL,
                                      fg=theme.TEXT, bg=bg)
        self.correct_label.grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.correct_entry = tk.Entry(self.form, font=theme.SMALL, width=20,
                                      bg=theme.SURFACE, fg=theme.TEXT,
                                      insertbackground=theme.TEXT, relief="flat")
        self.correct_entry.grid(row=1, column=1, sticky="w", padx=6, pady=4, ipady=4)

        self.kind_label = tk.Label(self.form, text="Kind:", font=theme.SMALL,
                                   fg=theme.TEXT, bg=bg)
        self.kind_label.grid(row=2, column=0, sticky="e", padx=6, pady=4)
        self.kind_var = tk.StringVar(value="choice")
        self.kind_menu = tk.OptionMenu(self.form, self.kind_var, "choice", "typed",
                                       command=self._on_kind_change)
        self.kind_menu.config(font=theme.SMALL, bg=theme.SURFACE, fg=theme.TEXT,
                              relief="flat")
        self.kind_menu.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        self.options_label = tk.Label(self.form, text="Choices (comma,sep):",
                                      font=theme.SMALL, fg=theme.TEXT, bg=bg)
        self.options_label.grid(row=3, column=0, sticky="e", padx=6, pady=4)
        self.options_entry = tk.Entry(self.form, font=theme.SMALL, width=40,
                                      bg=theme.SURFACE, fg=theme.TEXT,
                                      insertbackground=theme.TEXT, relief="flat")
        self.options_entry.grid(row=3, column=1, sticky="w", padx=6, pady=4, ipady=4)

        self.save_btn = self.make_button("Save", self._save)
        self.save_btn.grid(row=4, column=0, columnspan=2, pady=(8, 4))
        self.delete_btn = self.make_button("Delete Selected", self._delete, primary=False)
        self.delete_btn.grid(row=5, column=0, columnspan=2, pady=4)

    def _on_kind_change(self, *_):
        if self.kind_var.get() == "typed":
            self.options_entry.delete(0, "end")
            self.options_entry.config(state="disabled")
        else:
            self.options_entry.config(state="normal")

    def show(self):
        self._editing = None
        self._refresh_list()
        self._clear_form()
        self.feedback_label.config(text="")

    def _refresh_list(self):
        self.listbox.delete(0, "end")
        for q in self.app.controller.all_questions():
            self.listbox.insert("end", f"{q.id}: {q.prompt}")

    def _on_select(self, *_):
        sel = self.listbox.curselection()
        if not sel:
            return
        q = self.app.controller.all_questions()[sel[0]]
        self._editing = q.id
        self.prompt_entry.delete(0, "end")
        self.prompt_entry.insert(0, q.prompt)
        self.correct_entry.delete(0, "end")
        self.correct_entry.insert(0, q.correct)
        self.kind_var.set(q.kind)
        self.options_entry.config(state="normal")
        self.options_entry.delete(0, "end")
        self.options_entry.insert(0, ",".join(q.options))
        self._on_kind_change()

    def _clear_form(self):
        self._editing = None
        for e in (self.prompt_entry, self.correct_entry):
            e.delete(0, "end")
        self.kind_var.set("choice")
        self.options_entry.config(state="normal")
        self.options_entry.delete(0, "end")

    def _save(self):
        prompt = self.prompt_entry.get().strip()
        correct = self.correct_entry.get().strip()
        kind = self.kind_var.get()
        if kind == "choice":
            options = [o.strip() for o in self.options_entry.get().split(",") if o.strip()]
        else:
            options = []
        if not prompt or not correct:
            self.feedback_label.config(text="Prompt and correct value are required.",
                                       fg=theme.ERROR)
            return
        try:
            q = Question(id=self._editing or _new_id(), prompt=prompt, correct=correct,
                         kind=kind, options=options)
        except ValueError as e:
            self.feedback_label.config(text=f"Error: {e}", fg=theme.ERROR)
            return
        if self._editing:
            self.app.controller.repo.update(q)
        else:
            self.app.controller.add_question(q)
        self.feedback_label.config(text=f"Saved question: {prompt}", fg=theme.SUCCESS)
        self._refresh_list()
        self._clear_form()

    def _delete(self):
        sel = self.listbox.curselection()
        if not sel:
            self.feedback_label.config(text="Select a question to delete.", fg=theme.ERROR)
            return
        q = self.app.controller.all_questions()[sel[0]]
        name = q.prompt
        if messagebox.askyesno("Delete question", f"Delete question: {name}?"):
            self.app.controller.delete_question(q.id)
            self.feedback_label.config(text=f"Deleted question: {name}", fg=theme.SUCCESS)
            self._refresh_list()
            self._clear_form()

    def _back(self):
        self.app.show("menu")


def _new_id() -> str:
    import uuid
    return "q-" + uuid.uuid4().hex[:8]
