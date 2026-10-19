"""Play screen: question flow with choice and typed inputs."""
import tkinter as tk

from ui import theme
from ui.base_screen import BaseScreen


class PlayScreen(BaseScreen):
    """Runs a full round. Switches layout between choice buttons and a
    typed-answer input; each layout has its own inner frame to avoid mixing
    pack/grid in the same parent."""

    def __init__(self, master, app):
        super().__init__(master, app)
        self.prompt_label = tk.Label(
            self.body, text="", font=theme.QUESTION, fg=theme.TEXT, bg=theme.BG,
            wraplength=900, justify="center",
        )
        self.prompt_label.pack(pady=(0, 24))

        self.progress_label = tk.Label(
            self.body, text="", font=theme.SMALL, fg=theme.TEXT_MUTED, bg=theme.BG,
        )
        self.progress_label.pack(pady=(0, 12))

        self.choice_frame = tk.Frame(self.body, bg=theme.BG)
        self.type_frame = tk.Frame(self.body, bg=theme.BG)

        self.feedback_label = tk.Label(
            self.body, text="", font=theme.BODY, bg=theme.BG,
        )
        self.feedback_label.pack(pady=(16, 8))

        self.pause_btn = self.make_button("Pause", self._pause, primary=False)
        self.pause_btn.pack(pady=(8, 0))

        self._choice_buttons = []
        self._entry = None
        self._transitioning = False

    def show(self):
        self.app.controller.new_game()
        self._transitioning = False
        self.feedback_label.config(text="")
        self._render_question()

    def resume_game(self):
        """Re-render the current question without starting a new round."""
        self._transitioning = False
        self._render_question()

    def _render_question(self):
        game = self.app.controller.game
        if game is None or game.state.value == "GameOver":
            return
        q = game.current_question
        self.prompt_label.config(text=q.get_prompt())
        total = game.total
        self.progress_label.config(text=f"Question {game.index + 1} of {total}")
        self._clear_inputs()

        if q.kind == "choice":
            self.type_frame.pack_forget()
            self.choice_frame.pack(pady=4)
            self._choice_buttons = []
            for opt in q.get_options():
                b = self.make_button(opt, lambda o=opt: self._submit(o))
                b.pack(pady=6, fill="x")
                self._choice_buttons.append(b)
        else:
            self.choice_frame.pack_forget()
            self.type_frame.pack(pady=4)
            self._entry = tk.Entry(
                self.type_frame, font=theme.INPUT, width=14, justify="center",
                bg=theme.SURFACE, fg=theme.TEXT, insertbackground=theme.TEXT,
                relief="flat",
            )
            self._entry.pack(side="left", padx=(0, 12), ipady=8)
            check = self.make_button("Check", self._submit_typed)
            check.pack(side="left")
            self._entry.focus_set()
            self._entry.bind("<Return>", lambda e: self._submit_typed())

    def _clear_inputs(self):
        for b in self._choice_buttons:
            b.destroy()
        self._choice_buttons = []
        for w in self.type_frame.winfo_children():
            w.destroy()
        self._entry = None

    def _submit(self, answer):
        self._handle_answer(answer)

    def _submit_typed(self):
        if self._entry is None:
            return
        answer = self._entry.get().strip()
        self._handle_answer(answer)

    def _handle_answer(self, answer):
        game = self.app.controller.game
        if game is None or self._transitioning:
            return
        q = game.current_question
        expected = q.correct
        correct = game.submit_answer(answer)
        if correct:
            self.feedback_label.config(
                text=f"Correct! The answer is {expected}.", fg=theme.SUCCESS)
        else:
            self.feedback_label.config(
                text=f"Not quite — the answer is {expected}.", fg=theme.ERROR)
        self._transitioning = True
        self._clear_inputs()
        self.after(800, self._advance)

    def _advance(self):
        self._transitioning = False
        game = self.app.controller.game
        if game is None:
            return
        if game.state.value == "GameOver":
            self.app.controller.save_score()
            self.app.show("score")
        else:
            self._render_question()

    def _pause(self):
        game = self.app.controller.game
        if game is None:
            return
        try:
            game.pause()
        except Exception:
            return
        self.app.show("pause")
