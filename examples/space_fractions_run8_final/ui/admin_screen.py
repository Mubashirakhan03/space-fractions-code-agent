"""Admin 'Update Questions' use case: add/edit/delete fraction questions.

Reached only through the PIN gate; locks again when the user leaves (App.show).
"""
import tkinter as tk
from tkinter import messagebox, ttk

from ui import theme
from ui.base_screen import make_button, title_label
from question.question import Question, QuestionKind


KIND_LABELS = {
    "equivalent": "Equivalent fraction",
    "simplify": "Simplify",
    "decimal": "Decimal conversion",
    "larger": "Which is larger",
}


class AdminScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.BG)
        self.app = app
        self._editing_id = None

        self.title = title_label(self, "Manage Questions", 30)
        self.title.pack(pady=(20, 8))

        form = tk.Frame(self, bg=theme.SURFACE)
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Prompt:", bg=theme.SURFACE, fg=theme.TEXT,
                 font=theme.body_font(16)).grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.prompt_var = tk.StringVar()
        self.prompt_entry = tk.Entry(form, textvariable=self.prompt_var, width=44,
                                     font=theme.body_font(16), bg=theme.INPUT_BG,
                                     fg=theme.TEXT, relief="solid", bd=2,
                                     highlightthickness=2,
                                     highlightbackground=theme.INPUT_BORDER)
        self.prompt_entry.grid(row=0, column=1, sticky="we", padx=6, pady=4)

        tk.Label(form, text="Correct answer:", bg=theme.SURFACE, fg=theme.TEXT,
                 font=theme.body_font(16)).grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.correct_var = tk.StringVar()
        self.correct_entry = tk.Entry(form, textvariable=self.correct_var, width=24,
                                      font=theme.body_font(16), bg=theme.INPUT_BG,
                                      fg=theme.TEXT, relief="solid", bd=2,
                                      highlightthickness=2,
                                      highlightbackground=theme.INPUT_BORDER)
        self.correct_entry.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        tk.Label(form, text="Wrong options (comma-separated):", bg=theme.SURFACE,
                 fg=theme.TEXT, font=theme.body_font(16)).grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.options_var = tk.StringVar()
        self.options_entry = tk.Entry(form, textvariable=self.options_var, width=44,
                                      font=theme.body_font(16), bg=theme.INPUT_BG,
                                      fg=theme.TEXT, relief="solid", bd=2,
                                      highlightthickness=2,
                                      highlightbackground=theme.INPUT_BORDER)
        self.options_entry.grid(row=2, column=1, sticky="we", padx=6, pady=4)

        tk.Label(form, text="Kind:", bg=theme.SURFACE, fg=theme.TEXT,
                 font=theme.body_font(16)).grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.kind_var = tk.StringVar(value="equivalent")
        self.kind_combo = ttk.Combobox(form, textvariable=self.kind_var,
                                       values=list(KIND_LABELS.keys()),
                                       font=theme.body_font(16), state="readonly", width=20)
        self.kind_combo.grid(row=3, column=1, sticky="w", padx=6, pady=4)

        form.grid_columnconfigure(1, weight=1)

        btns = tk.Frame(self, bg=theme.BG)
        btns.pack(fill="x", padx=20, pady=4)
        self.save_btn = make_button(btns, "Add Question", self._save)
        self.save_btn.pack(side="left")
        self.clear_btn = make_button(btns, "Clear", self._clear_form)
        self.clear_btn.pack(side="left", padx=10)
        self.done_btn = make_button(btns, "Done", self._done)
        self.done_btn.pack(side="right")

        self.msg = tk.Label(self, text="", bg=theme.BG, fg=theme.SUCCESS,
                            font=theme.body_font(18))
        self.msg.pack(pady=4)

        # scrollable list
        list_frame = tk.Frame(self, bg=theme.BG)
        list_frame.pack(expand=True, fill="both", padx=20, pady=8)
        self.canvas = tk.Canvas(list_frame, bg=theme.BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                       command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=theme.BG)
        self.list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def on_show(self):
        if not self.app.admin_unlocked:
            return
        self._refresh_list()

    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        for q in self.app.db.all_questions():
            row = tk.Frame(self.list_frame, bg=theme.SURFACE)
            row.pack(fill="x", pady=3)
            txt = tk.Label(row, text=f"{q.prompt}  →  {q.correct_answer}",
                           bg=theme.SURFACE, fg=theme.TEXT, font=theme.body_font(16),
                           anchor="w", wraplength=700)
            txt.pack(side="left", padx=8, pady=4, expand=True, fill="x")
            edit_btn = make_button(row, "Edit", lambda qid=q.id: self._edit(qid),
                                   font=theme.button_font(14), padx=10, pady=4)
            edit_btn.pack(side="right", padx=4)
            del_btn = make_button(row, "Delete",
                                  lambda qid=q.id: self._delete(qid),
                                  font=theme.button_font(14), padx=10, pady=4)
            del_btn.pack(side="right", padx=4)

    def _save(self):
        prompt = self.prompt_var.get().strip()
        correct = self.correct_var.get().strip()
        options_raw = self.options_var.get().strip()
        kind = self.kind_var.get()
        if not prompt or not correct:
            self.msg.config(text="Prompt and correct answer are required.",
                            fg=theme.ERROR)
            return
        wrongs = [w.strip() for w in options_raw.split(",") if w.strip()]
        if len(wrongs) < 1:
            self.msg.config(text="Add at least one wrong option.", fg=theme.ERROR)
            return
        options = [correct] + wrongs
        if len(set(options)) != len(options):
            self.msg.config(text="Options must be distinct.", fg=theme.ERROR)
            return
        q = Question(prompt=prompt, options=options, correct_index=0,
                     kind=QuestionKind(kind), qid=self._editing_id or "")
        if self._editing_id:
            self.app.db.update_question(q)
            self.msg.config(text=f"Updated: {prompt}", fg=theme.SUCCESS)
        else:
            self.app.db.add_question(q)
            self.msg.config(text=f"Added: {prompt}", fg=theme.SUCCESS)
        self._clear_form()
        self._refresh_list()

    def _edit(self, qid):
        q = self.app.db.get_question(qid)
        if not q:
            return
        self._editing_id = qid
        self.prompt_var.set(q.prompt)
        self.correct_var.set(q.correct_answer)
        wrongs = [o for i, o in enumerate(q.getOptions()) if i != q.correct_index]
        self.options_var.set(", ".join(wrongs))
        self.kind_var.set(q.kind.value)
        self.save_btn.config(text="Update Question")
        self.msg.config(text=f"Editing: {q.prompt}", fg=theme.ACCENT)

    def _delete(self, qid):
        q = self.app.db.get_question(qid)
        name = q.prompt if q else qid
        if messagebox.askyesno("Delete question", f"Delete '{name}'?"):
            self.app.db.delete_question(qid)
            self._refresh_list()
            self.msg.config(text=f"Deleted: {name}", fg=theme.SUCCESS)

    def _clear_form(self):
        self._editing_id = None
        self.prompt_var.set("")
        self.correct_var.set("")
        self.options_var.set("")
        self.kind_var.set("equivalent")
        self.save_btn.config(text="Add Question")

    def _done(self):
        self.app.admin_unlocked = False
        self.app.show("menu")
