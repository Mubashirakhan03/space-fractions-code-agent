"""Admin screen: list + add/edit/delete questions (two-column layout)."""
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

        # Self-contained content frame (not the shared centred body) so we can
        # lay columns out with grid and keep everything inside the window.
        self.content = tk.Frame(self, bg=theme.BG)
        self.content.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = tk.Label(
            self.content, text="Update Questions", font=theme.HEADING,
            fg=theme.ACCENT, bg=theme.BG,
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 16))

        # Left column: question list.
        self.left = tk.Frame(self.content, bg=theme.BG)
        self.left.grid(row=1, column=0, sticky="n", padx=(0, 20))
        self.listbox = tk.Listbox(
            self.left, font=theme.SMALL, bg=theme.SURFACE, fg=theme.TEXT,
            relief="flat", height=10, width=44,
        )
        self.listbox.pack()
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # Right column: add/edit form.
        self.form = tk.Frame(self.content, bg=theme.SURFACE)
        self.form.grid(row=1, column=1, sticky="n", padx=(20, 0))
        self._build_form()

        self.feedback_label = tk.Label(
            self.content, text="", font=theme.SMALL, bg=theme.BG,
        )
        self.feedback_label.grid(row=2, column=0, columnspan=2, pady=(12, 8))

        self.back_btn = self.make_button("Back to Menu", self._back, primary=False,
                                         master=self.content)
        self.back_btn.grid(row=3, column=0, columnspan=2, pady=(0, 4))

    def _build_form(self):
        for w in self.form.winfo_children():
            w.destroy()
        bg = theme.SURFACE
        self.prompt_label = tk.Label(self.form, text="Prompt:", font=theme.SMALL,
                                     fg=theme.TEXT, bg=bg)
        self.prompt_label.grid(row=0, column=0, sticky="e", padx=6, pady=3)
        self.prompt_entry = tk.Entry(self.form, font=theme.SMALL, width=32,
                                     bg=theme.SURFACE, fg=theme.TEXT,
                                     insertbackground=theme.TEXT, relief="flat")
        self.prompt_entry.grid(row=0, column=1, sticky="w", padx=6, pady=3, ipady=3)

        self.correct_label = tk.Label(self.form, text="Correct value:", font=theme.SMALL,
                                      fg=theme.TEXT, bg=bg)
        self.correct_label.grid(row=1, column=0, sticky="e", padx=6, pady=3)
        self.correct_entry = tk.Entry(self.form, font=theme.SMALL, width=14,
                                      bg=theme.SURFACE, fg=theme.TEXT,
                                      insertbackground=theme.TEXT, relief="flat")
        self.correct_entry.grid(row=1, column=1, sticky="w", padx=6, pady=3, ipady=3)

        self.kind_label = tk.Label(self.form, text="Kind:", font=theme.SMALL,
                                   fg=theme.TEXT, bg=bg)
        self.kind_label.grid(row=2, column=0, sticky="e", padx=6, pady=3)
        self.kind_var = tk.StringVar(value="choice")
        self.kind_menu = tk.OptionMenu(self.form, self.kind_var, "choice", "typed",
                                       command=self._on_kind_change)
        self.kind_menu.config(font=theme.SMALL, bg=theme.SURFACE, fg=theme.TEXT,
                              relief="flat")
        self.kind_menu.grid(row=2, column=1, sticky="w", padx=6, pady=3)

        self.options_label = tk.Label(self.form, text="Choices (comma,sep):",
                                      font=theme.SMALL, fg=theme.TEXT, bg=bg)
        self.options_label.grid(row=3, column=0, sticky="e", padx=6, pady=3)
        self.options_entry = tk.Entry(self.form, font=theme.SMALL, width=32,
                                      bg=theme.SURFACE, fg=theme.TEXT,
                                      insertbackground=theme.TEXT, relief="flat")
        self.options_entry.grid(row=3, column=1, sticky="w", padx=6, pady=3, ipady=3)

        self.save_btn = self.make_button("Save", self._save, master=self.form)
        self.save_btn.grid(row=4, column=0, columnspan=2, pady=(6, 3))
        self.delete_btn = self.make_button("Delete Selected", self._delete,
                                           primary=False, master=self.form)
        self.delete_btn.grid(row=5, column=0, columnspan=2, pady=3)

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
