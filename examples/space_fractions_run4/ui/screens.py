"""Screens for Space Fractions (one Frame class per use case / major state).

Every screen renders safely when shown directly (e.g. before data exists).
Screens are switched by ui/app.App.show(name).
"""
import sqlite3
import tkinter as tk
from tkinter import ttk

from fractions import Fraction

from game.game import Game, ROUND_SIZE
from game.state import GameState
from questions.repository import QuestionRepository
from admin.admin import Admin, DEFAULT_PASSCODE
import ui.theme as theme


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
class Screen(tk.Frame):
    """Base screen with an optional translucent panel for contrast."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self._panel = None

    def add_panel(self):
        if self._panel is not None:
            return self._panel
        self._panel = tk.Frame(self, bg=theme.SURFACE, highlightthickness=2,
                               highlightbackground=theme.SURFACE_LIGHT)
        self._panel.place(relx=0.5, rely=0.5, anchor="center",
                          relwidth=0.86, relheight=0.84)
        return self._panel

    # Called by the app when a screen is shown (refreshes dynamic content).
    def on_show(self):
        pass


def _make_button(parent, text, command, bg=theme.PRIMARY, fg="#0B1736",
                 font=None, hover=None):
    btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                    font=font or theme.BUTTON_FONT, relief="flat",
                    activebackground=hover or theme.PRIMARY_HOVER,
                    activeforeground=fg, pady=14, padx=18, cursor="hand2",
                    bd=0, highlightthickness=0)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover or theme.PRIMARY_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


# ---------------------------------------------------------------------------
# Intro (the "introductory movie")
# ---------------------------------------------------------------------------
class IntroScreen(Screen):
    TITLE = "Space Fractions"
    TAGLINE = "Blast off into the world of fractions!"

    def __init__(self, master, app):
        super().__init__(master, app)
        self.add_panel()
        p = self._panel
        self.title_label = tk.Label(p, text=self.TITLE, font=theme.F(44, "bold"),
                                    fg=theme.TEXT, bg=theme.SURFACE)
        self.title_label.pack(pady=(70, 10))
        self.tagline = tk.Label(p, text=self.TAGLINE, font=theme.F(22),
                                fg=theme.ACCENT_CYAN, bg=theme.SURFACE)
        self.tagline.pack(pady=10)

        # rocket animation canvas
        self.canvas = tk.Canvas(p, bg=theme.SURFACE, highlightthickness=0,
                                height=240)
        self.canvas.pack(fill="x", pady=20)
        self._rocket_x = -80
        self._after_id = None

        self.skip_button = _make_button(p, "Skip  ▶", self.skip)
        self.skip_button.pack(pady=20)

    def on_show(self):
        self._rocket_x = -80
        self._schedule()

    def _schedule(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        self._after_id = self.after(40, self._animate)

    def _animate(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 600
        self._rocket_x += 3
        if self._rocket_x > w + 90:
            self.auto_advance()
            return
        # exhaust flame
        c.create_polygon(self._rocket_x - 14, 120, self._rocket_x - 34, 100,
                         self._rocket_x - 34, 140, fill=theme.ACCENT_PINK)
        # rocket body
        c.create_oval(self._rocket_x - 20, 90, self._rocket_x + 20, 150,
                      fill=theme.PRIMARY, outline="")
        c.create_polygon(self._rocket_x + 4, 60, self._rocket_x + 20, 90,
                         self._rocket_x - 12, 90, fill=theme.ACCENT_CYAN,
                         outline="")
        c.create_oval(self._rocket_x - 4, 105, self._rocket_x + 8, 117,
                      fill=theme.SURFACE, outline="")
        # moving stars
        for i in range(8):
            sx = (i * 97 - self._rocket_x * 2) % w
            sy = (i * 53) % 200 + 20
            c.create_oval(sx, sy, sx + 2, sy + 2, fill="#FFFFFF", outline="")
        self._after_id = self.after(40, self._animate)

    def auto_advance(self):
        self._cleanup()
        self.app.show("menu")

    def skip(self):
        self._cleanup()
        self.app.show("menu")

    def _cleanup(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------
class MenuScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        p = self.add_panel()
        self.title_label = tk.Label(p, text="🚀 Space Fractions", font=theme.F(44, "bold"),
                                    fg=theme.TEXT, bg=theme.SURFACE)
        self.title_label.pack(pady=(50, 10))
        sub = tk.Label(p, text="Main Menu", font=theme.F(22), fg=theme.ACCENT_CYAN,
                       bg=theme.SURFACE)
        sub.pack(pady=8)

        self.play_button = _make_button(p, "▶  Play", self.start_play)
        self.play_button.pack(pady=12, ipadx=40)
        self.scores_button = _make_button(p, "🏆  High Scores", lambda: app.show("scores"),
                                          bg=theme.ACCENT_CYAN, hover=theme.ACCENT_CYAN)
        self.scores_button.pack(pady=12, ipadx=20)
        self.help_button = _make_button(p, "❓  Help", lambda: app.show("help"),
                                        bg=theme.ACCENT_GREEN, hover=theme.ACCENT_GREEN)
        self.help_button.pack(pady=12, ipadx=30)
        self.admin_button = _make_button(p, "🔧  Admin", lambda: app.show("admin"),
                                         bg=theme.ACCENT_PINK, hover=theme.ACCENT_PINK)
        self.admin_button.pack(pady=12, ipadx=25)
        self.exit_button = _make_button(p, "✖  Exit", self.exit_app, bg=theme.ERROR,
                                        hover=theme.ERROR)
        self.exit_button.pack(pady=12, ipadx=30)

    def start_play(self):
        self.app.show("name")

    def exit_app(self):
        self.app.root.destroy()


# ---------------------------------------------------------------------------
# Name entry (UserComponent)
# ---------------------------------------------------------------------------
class NameScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        p = self.add_panel()
        self.title_label = tk.Label(p, text="What's your name, cadet?",
                                    font=theme.F(34, "bold"), fg=theme.TEXT,
                                    bg=theme.SURFACE)
        self.title_label.pack(pady=(60, 20))
        self.name_entry = tk.Entry(p, font=theme.F(24), justify="center",
                                   bg=theme.SURFACE_LIGHT, fg=theme.TEXT,
                                   insertbackground=theme.TEXT, relief="flat")
        self.name_entry.pack(pady=10, ipady=10, ipadx=20)
        self.feedback = tk.Label(p, text="", font=theme.F(18), fg=theme.ERROR,
                                 bg=theme.SURFACE)
        self.feedback.pack(pady=8)
        self.start_button = _make_button(p, "Blast off!  🚀", self.submit)
        self.start_button.pack(pady=20)
        self.back_button = _make_button(p, "←  Back", lambda: app.show("menu"),
                                        bg=theme.SURFACE_LIGHT, hover=theme.SURFACE_LIGHT)
        self.back_button.pack(pady=6)

    def on_show(self):
        self.name_entry.delete(0, "end")
        self.feedback.config(text="")
        self.name_entry.focus_set()

    def submit(self, event=None):
        name = self.name_entry.get().strip()
        if not name:
            self.feedback.config(text="Please enter a name to continue.")
            return
        self.app.player_name = name
        self.app.start_game()


# ---------------------------------------------------------------------------
# Question flow (Play Game)
# ---------------------------------------------------------------------------
class QuestionScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        p = self.add_panel()

        self.progress_label = tk.Label(p, text="Question 1 of 10", font=theme.F(20),
                                       fg=theme.TEXT_MUTED, bg=theme.SURFACE)
        self.progress_label.pack(pady=(24, 6), anchor="w", padx=30)
        self.progress_bar = ttk.Progressbar(p, maximum=ROUND_SIZE, length=600)
        self.progress_bar.pack(pady=(0, 6), padx=30, fill="x")

        self.score_label = tk.Label(p, text="Score: 0", font=theme.F(22, "bold"),
                                    fg=theme.ACCENT_GREEN, bg=theme.SURFACE)
        self.score_label.pack(anchor="e", padx=30)

        self.question_label = tk.Label(p, text="", font=theme.QUESTION_FONT,
                                       fg=theme.TEXT, bg=theme.SURFACE,
                                       wraplength=900, justify="center")
        self.question_label.pack(pady=16, padx=30)

        # choice layout (2x2 grid)
        self.choice_frame = tk.Frame(p, bg=theme.SURFACE)
        self.choice_buttons = []
        # typed layout
        self.type_frame = tk.Frame(p, bg=theme.SURFACE)
        self.answer_entry = tk.Entry(self.type_frame, font=theme.F(24),
                                     justify="center", bg=theme.SURFACE_LIGHT,
                                     fg=theme.TEXT, insertbackground=theme.TEXT,
                                     relief="flat")
        self.answer_entry.pack(ipady=10, ipadx=20)
        self.answer_entry.bind("<Return>", self.submit_typed)

        self.feedback = tk.Label(p, text="", font=theme.F(26, "bold"),
                                 fg=theme.SUCCESS, bg=theme.SURFACE)
        self.feedback.pack(pady=14)

        self.pause_button = _make_button(p, "⏸  Pause", self.pause,
                                         bg=theme.SURFACE_LIGHT,
                                         hover=theme.SURFACE_LIGHT)
        self.pause_button.pack(side="bottom", pady=18, anchor="s", padx=30)

        self._game = None
        self._next_after = None

        # pause overlay
        self.overlay = tk.Frame(p, bg=theme.BG)
        ol = tk.Label(self.overlay, text="⏸  Paused", font=theme.F(40, "bold"),
                      fg=theme.ACCENT_CYAN, bg=theme.BG)
        ol.pack(pady=40)
        self.resume_button = _make_button(self.overlay, "▶  Resume", self.resume)
        self.resume_button.pack(pady=10)

    def on_show(self):
        self._cancel_pending()
        game = self.app.game
        if game is None or game.state is GameState.GAMEOVER:
            self._show_advisory("No active game.")
            return
        self._game = game
        self._render_question()
        self._sync_overlay()

    def _show_advisory(self, text):
        self.progress_label.config(text="")
        self.score_label.config(text="")
        self.feedback.config(text=text, fg=theme.TEXT_MUTED)
        self.question_label.config(text="")
        self.choice_frame.pack_forget()
        self.type_frame.pack_forget()

    def _render_question(self):
        self._cancel_pending()
        game = self._game
        q = game.current_question
        self.progress_label.config(
            text=f"Question {game.question_number} of {game.total_questions}")
        self.progress_bar["value"] = game.question_number - 1
        self.score_label.config(text=f"Score: {game.viewScore()}")
        self.feedback.config(text="", fg=theme.SUCCESS)
        if q is None:
            self._finish()
            return
        self.question_label.config(text=q.getPrompt())

        if q.is_choice:
            self.type_frame.pack_forget()
            self.choice_frame.pack(pady=10)
            for b in self.choice_buttons:
                b.destroy()
            self.choice_buttons = []
            opts = q.getOptions()
            for i, opt in enumerate(opts):
                colour = theme.CHOICE_COLORS[i % len(theme.CHOICE_COLORS)]
                b = _make_button(self.choice_frame, opt,
                                 lambda opt=opt: self.submit_answer(opt),
                                 bg=colour, hover=colour)
                b.grid(row=i // 2, column=i % 2, padx=12, pady=12,
                       ipadx=40, ipady=6, sticky="nsew")
                self.choice_buttons.append(b)
        else:
            self.choice_frame.pack_forget()
            self.type_frame.pack(pady=18)
            self.answer_entry.delete(0, "end")
            self.answer_entry.focus_set()

    def submit_typed(self, event=None):
        answer = self.answer_entry.get().strip()
        self.submit_answer(answer)

    def submit_answer(self, answer):
        if self._game is None or self._game.state is not GameState.PLAYING:
            return
        correct, expected = self._game.submit(answer)
        if correct:
            self.feedback.config(text="Correct! 🎉", fg=theme.SUCCESS)
        else:
            self.feedback.config(
                text=f"Not quite — the answer is {expected}", fg=theme.ERROR)
        # clear input automatically (always after a typed submission)
        self.answer_entry.delete(0, "end")
        if self._game.state is GameState.GAMEOVER:
            self._next_after = self.after(900, self._finish)
        else:
            self._next_after = self.after(900, self._render_question)

    def _finish(self):
        self._cancel_pending()
        self.app.finish_game()

    def pause(self):
        if self._game and self._game.state is GameState.PLAYING:
            try:
                self._game.pause()
            except ValueError:
                return
            self._sync_overlay()

    def resume(self):
        if self._game and self._game.state is GameState.PAUSED:
            try:
                self._game.resume()
            except ValueError:
                return
            self._sync_overlay()
            if self._game.current_question and not self._game.current_question.is_choice:
                self.answer_entry.focus_set()

    def _sync_overlay(self):
        if self._game and self._game.state is GameState.PAUSED:
            self.overlay.place(relx=0.5, rely=0.5, anchor="center",
                               relwidth=0.6, relheight=0.45)
        else:
            self.overlay.place_forget()

    def _cancel_pending(self):
        if self._next_after is not None:
            self.after_cancel(self._next_after)
            self._next_after = None


# ---------------------------------------------------------------------------
# High scores (View Score)
# ---------------------------------------------------------------------------
class ScoresScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        p = self.add_panel()
        self.title_label = tk.Label(p, text="🏆  High Scores", font=theme.F(38, "bold"),
                                    fg=theme.TEXT, bg=theme.SURFACE)
        self.title_label.pack(pady=(40, 10))
        self.scores_text = tk.Text(p, font=theme.F(18), bg=theme.SURFACE_LIGHT,
                                   fg=theme.TEXT, relief="flat", height=14,
                                   width=70)
        self.scores_text.pack(pady=10, padx=30)
        self.scores_text.config(state="disabled")
        self.back_button = _make_button(p, "←  Main Menu", lambda: app.show("menu"))
        self.back_button.pack(pady=16)

    def on_show(self):
        rows = self.app.get_high_scores()
        self.scores_text.config(state="normal")
        self.scores_text.delete("1.0", "end")
        if not rows:
            self.scores_text.insert("1.0", "No scores yet — be the first! 🚀")
        else:
            for name, score, pct, stars in rows[:20]:
                star = "★" * stars + "☆" * (3 - stars)
                self.scores_text.insert(
                    "end", f"{name:<20} {score}/{self.app.round_size}  {pct}%  {star}\n")
        self.scores_text.config(state="disabled")


# ---------------------------------------------------------------------------
# Help (View Help)
# ---------------------------------------------------------------------------
class HelpScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        p = self.add_panel()
        self.title_label = tk.Label(p, text="❓  How to Play", font=theme.F(38, "bold"),
                                    fg=theme.TEXT, bg=theme.SURFACE)
        self.title_label.pack(pady=(40, 12))
        help_lines = (
            "Answer fraction questions to earn points!",
            "",
            "• Equivalent fractions: pick the fraction that is the same value.",
            "• Compare: choose which fraction is bigger or smaller.",
            "• Add / Subtract: solve fraction sums and differences.",
            "• Simplify: reduce the fraction to its simplest form.",
            "",
            "Equivalent answers count too — 2/4 is the same as 1/2!",
            "Press ⏸ to pause and ▶ to resume any time.",
        )
        self.help_text = tk.Label(p, text="\n".join(help_lines), font=theme.F(20),
                                  fg=theme.TEXT_MUTED, bg=theme.SURFACE,
                                  justify="left", wraplength=900)
        self.help_text.pack(pady=12, padx=40, anchor="w")
        self.back_button = _make_button(p, "←  Main Menu", lambda: app.show("menu"))
        self.back_button.pack(pady=20)


# ---------------------------------------------------------------------------
# Admin (Update Questions)
# ---------------------------------------------------------------------------
class AdminScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        p = self.add_panel()
        self.title_label = tk.Label(p, text="🔧  Admin", font=theme.F(38, "bold"),
                                    fg=theme.TEXT, bg=theme.SURFACE)
        self.title_label.pack(pady=(40, 12))

        self.pass_entry = tk.Entry(p, font=theme.F(22), show="•", justify="center",
                                   bg=theme.SURFACE_LIGHT, fg=theme.TEXT,
                                   insertbackground=theme.TEXT, relief="flat")
        self.pass_entry.pack(pady=8, ipady=8, ipadx=16)
        self.pass_entry.bind("<Return>", self.unlock)
        self.feedback = tk.Label(p, text="Enter passcode to manage questions.",
                                 font=theme.F(18), fg=theme.TEXT_MUTED, bg=theme.SURFACE)
        self.feedback.pack(pady=8)
        self.unlock_button = _make_button(p, "Unlock", self.unlock)
        self.unlock_button.pack(pady=10)

        # question list (shown after unlock)
        self.list_frame = tk.Frame(p, bg=theme.SURFACE)
        self.admin_back = _make_button(p, "←  Main Menu", lambda: app.show("menu"))
        self.admin_back.pack(side="bottom", pady=16)

    def on_show(self):
        self.pass_entry.delete(0, "end")
        self.feedback.config(text="Enter passcode to manage questions.",
                             fg=theme.TEXT_MUTED)

    def unlock(self, event=None):
        code = self.pass_entry.get().strip()
        if not self.app.admin.authenticate(code):
            self.feedback.config(text="Wrong passcode — try again.", fg=theme.ERROR)
            return
        self.feedback.config(text="Unlocked ✓", fg=theme.SUCCESS)
        self._render_list()

    def _render_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.list_frame.pack(pady=8, fill="both", expand=True)
        header = tk.Label(self.list_frame,
                          text=f"Question bank ({self.app.repository.count()} questions)",
                          font=theme.F(18), fg=theme.ACCENT_CYAN, bg=theme.SURFACE)
        header.pack(pady=4)
        canvas = tk.Canvas(self.list_frame, bg=theme.SURFACE, highlightthickness=0)
        scroll = ttk.Scrollbar(self.list_frame, orient="vertical",
                               command=canvas.yview)
        inner = tk.Frame(canvas, bg=theme.SURFACE)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        for q in self.app.repository.all():
            row = tk.Frame(inner, bg=theme.SURFACE)
            row.pack(fill="x", padx=8, pady=2)
            lbl = tk.Label(row, text=f"{q.prompt}", font=theme.F(16),
                           fg=theme.TEXT, bg=theme.SURFACE, anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            del_btn = _make_button(row, "✖", lambda qid=q.id: self.delete(qid),
                                   bg=theme.ERROR, hover=theme.ERROR, font=theme.F(14))
            del_btn.pack(side="right")

    def delete(self, question_id):
        if self.app.admin.deleteQuestion(question_id):
            self.app.repository.save()
            self.feedback.config(
                text=f"Deleted question {question_id}", fg=theme.SUCCESS)
            self._render_list()


# ---------------------------------------------------------------------------
# End scene (ending scene with feedback)
# ---------------------------------------------------------------------------
class EndScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        p = self.add_panel()
        self.title_label = tk.Label(p, text="", font=theme.F(42, "bold"),
                                    fg=theme.ACCENT_CYAN, bg=theme.SURFACE)
        self.title_label.pack(pady=(50, 8))
        self.score_label = tk.Label(p, text="", font=theme.F(30, "bold"),
                                    fg=theme.TEXT, bg=theme.SURFACE)
        self.score_label.pack(pady=8)
        self.stars_label = tk.Label(p, text="", font=theme.F(40),
                                    fg=theme.PRIMARY, bg=theme.SURFACE)
        self.stars_label.pack(pady=6)
        self.feedback = tk.Label(p, text="", font=theme.F(22),
                                 fg=theme.TEXT_MUTED, bg=theme.SURFACE,
                                 wraplength=900)
        self.feedback.pack(pady=10)

        self.canvas = tk.Canvas(p, bg=theme.SURFACE, highlightthickness=0,
                                height=140)
        self.canvas.pack(fill="x", pady=10)
        self._confetti_after = None

        btn_row = tk.Frame(p, bg=theme.SURFACE)
        btn_row.pack(pady=16)
        self.replay_button = _make_button(btn_row, "🔄  Play again", self.replay)
        self.replay_button.pack(side="left", padx=12)
        self.menu_button = _make_button(btn_row, "🏠  Main menu",
                                        lambda: app.show("menu"),
                                        bg=theme.ACCENT_CYAN, hover=theme.ACCENT_CYAN)
        self.menu_button.pack(side="left", padx=12)

    def on_show(self):
        self._stop_confetti()
        game = self.app.game
        name = self.app.player_name
        if game is None:
            self.title_label.config(text="Game over")
            self.score_label.config(text="")
            self.stars_label.config(text="")
            self.feedback.config(text="")
            return
        res = game.result()
        self.title_label.config(text=f"Congratulations, {name}!")
        self.score_label.config(
            text=f"You scored {res.score} out of {res.total} ({res.percentage}%)")
        self.stars_label.config(text="★" * res.stars + "☆" * (3 - res.stars))
        self.feedback.config(text=self._feedback_text(res))
        self._confetti_after = self.after(40, self._confetti)

    def _feedback_text(self, res):
        if res.stars == 3:
            return "Out of this world! You're a fractions superstar! 🌟"
        if res.stars == 2:
            return "Great flying! Just a little more practice and you'll soar! 🚀"
        if res.stars == 1:
            return "Good effort! Keep exploring those fractions! 🛰️"
        return "Don't give up, cadet — try again and reach for the stars! 🌌"

    def _confetti(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 600
        import random
        rng = random.Random()
        for _ in range(40):
            x = rng.randint(0, w)
            y = rng.randint(0, 120)
            colour = rng.choice([theme.ACCENT_CYAN, theme.ACCENT_PINK,
                                 theme.ACCENT_GREEN, theme.PRIMARY])
            c.create_oval(x, y, x + 6, y + 6, fill=colour, outline="")
        self._confetti_after = self.after(350, self._confetti)

    def _stop_confetti(self):
        if self._confetti_after is not None:
            self.after_cancel(self._confetti_after)
            self._confetti_after = None

    def replay(self):
        self._stop_confetti()
        self.app.start_game()
