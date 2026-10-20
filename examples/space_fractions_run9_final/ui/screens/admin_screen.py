"""Admin screen: lists ALL questions (seed included) with Add/Edit/Delete."""
from __future__ import annotations

import uuid
import tkinter as tk
from tkinter import messagebox

from ui import theme
from ui.screens.base import BaseScreen
from question.question import Question, KNOWN_KINDS

KIND_NAMES = {
    "identify": "Identify a fraction",
    "compare": "Compare fractions",
    "add": "Add fractions",
    "subtract": "Subtract fractions",
    "reduce": "Reduce to lowest terms",
    "equivalent": "Find an equivalent fraction",
}


class AdminScreen(BaseScreen):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "admin_screen")

        header = tk.Frame(self, bg=theme.BG)
        header.pack(fill="x", padx=20, pady=(8, 2))
        theme.make_label(header, "Manage Questions", theme.TITLE_SIZE - 6,
                         theme.ACCENT, "bold").pack(side="left")
        self.back_btn = theme.make_button(header, "⬅ Menu",
                                          lambda: self.app.show("main_menu"),
                                          bg=theme.SURFACE)
        self.back_btn.pack(side="right")

        self.error_label = theme.make_label(self, "", theme.FEEDBACK_SIZE - 2,
                                            theme.ERROR, "bold")
        self.error_label.pack()

        # List area (compact height)
        self.listbox = tk.Listbox(self, bg=theme.SURFACE, fg=theme.TEXT,
                                  font=theme.font(theme.BUTTON_SIZE - 2),
                                  selectbackground=theme.PRIMARY,
                                  relief="flat", bd=0, height=6)
        self.listbox.pack(fill="both", expand=True, padx=40, pady=(2, 2))
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        self.selection_label = theme.make_label(self, "", theme.FEEDBACK_SIZE - 2,
                                                theme.MUTED)
        self.selection_label.pack()

        # Form: each text input has a visible submit button next to it.
        form = tk.Frame(self, bg=theme.BG)
        form.pack(pady=4)

        self.prompt_entry = self._add_field(form, "Prompt:", 0)
        self.add_btn = theme.make_button(form, "➕ Add", self.add_question)
        self.add_btn.grid(row=0, column=2, sticky="w", padx=6, pady=2)

        self.kind_var = tk.StringVar(value="identify")
        kind_menu = tk.OptionMenu(form, self.kind_var, *KNOWN_KINDS)
        kind_menu.config(bg=theme.SURFACE_ALT, fg=theme.TEXT,
                         font=theme.font(theme.BUTTON_SIZE - 2), relief="flat")
        kind_menu["menu"].config(bg=theme.SURFACE, fg=theme.TEXT,
                                font=theme.font(theme.BUTTON_SIZE - 2))
        kind_menu.grid(row=1, column=1, sticky="w", pady=2, padx=4)
        theme.make_label(form, "Kind:", theme.BUTTON_SIZE - 2, theme.MUTED).grid(
            row=1, column=0, sticky="e", padx=4)

        self.correct_entry = self._add_field(form, "Correct:", 2)
        self.edit_btn = theme.make_button(form, "✏️ Edit", self.edit_question,
                                          bg=theme.SURFACE)
        self.edit_btn.grid(row=2, column=2, sticky="w", padx=6, pady=2)

        self.choices_entry = self._add_field(form, "Choices:", 3)
        self.delete_btn = theme.make_button(form, "🗑 Delete", self.delete_question,
                                            bg=theme.ERROR)
        self.delete_btn.grid(row=3, column=2, sticky="w", padx=6, pady=2)

        self._questions = []
        self._selected_id = None

    def _add_field(self, parent, label, row):
        theme.make_label(parent, label, theme.BUTTON_SIZE - 2, theme.MUTED).grid(
            row=row, column=0, sticky="e", padx=4, pady=2)
        entry = theme.make_entry(parent, width=40)
        entry.grid(row=row, column=1, sticky="w", pady=2)
        return entry

    def on_show(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        self._questions = self.app.repository.list_all()
        self.listbox.delete(0, "end")
        for q in self._questions:
            self.listbox.insert("end", f"{q.id}: {q.prompt}")
        self.error_label.config(text="")
        self._selected_id = None
        self.selection_label.config(text=f"{len(self._questions)} questions loaded.")

    def _on_select(self, _event=None) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self._questions):
            q = self._questions[idx]
            self._selected_id = q.id
            self.prompt_entry.delete(0, "end")
            self.prompt_entry.insert(0, q.prompt)
            self.correct_entry.delete(0, "end")
            self.correct_entry.insert(0, q.correct_value)
            self.choices_entry.delete(0, "end")
            self.choices_entry.insert(0, ", ".join(q.choices))
            self.kind_var.set(q.kind)
            self.selection_label.config(text=f"Selected: {q.id}")

    def _collect(self) -> Question:
        prompt = self.prompt_entry.get().strip()
        correct = self.correct_entry.get().strip()
        kind = self.kind_var.get()
        choices_raw = self.choices_entry.get().strip()
        choices = [c.strip() for c in choices_raw.split(",") if c.strip()] if choices_raw else []
        if not prompt:
            raise ValueError("Prompt is required.")
        if not correct:
            raise ValueError("Correct value is required.")
        return Question(id=f"q-{uuid.uuid4().hex[:8]}", prompt=prompt,
                        kind=kind, correct_value=correct, choices=choices)

    def add_question(self) -> None:
        try:
            q = self._collect()
        except ValueError as e:
            self.error_label.config(text=f"❌ {e}")
            return
        self.app.repository.add(q)
        self.error_label.config(text=f"✅ Added: {q.prompt}")
        self.refresh()

    def edit_question(self) -> None:
        if not self._selected_id:
            self.error_label.config(text="❌ Select a question to edit.")
            return
        try:
            q = self._collect()
        except ValueError as e:
            self.error_label.config(text=f"❌ {e}")
            return
        q.id = self._selected_id
        self.app.repository.update(q)
        self.error_label.config(text=f"✅ Updated: {q.prompt}")
        self.refresh()

    def delete_question(self) -> None:
        if not self._selected_id:
            self.error_label.config(text="❌ Select a question to delete.")
            return
        target = self.app.repository.store.get_question(self._selected_id)
        name = target.prompt if target else self._selected_id
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete question:\n{name}\n\nThis cannot be undone."):
            return
        self.app.repository.delete(self._selected_id)
        self.error_label.config(text=f"🗑 Deleted: {name}")
        self.refresh()
