"""App controller: builds all screens and routes between them.

Contract (harness):
  create_app(root) -> App
  App.screens: dict[str, tk.Frame]
  App.show(name)
"""
from __future__ import annotations

import json
import os
import sqlite3
import tkinter as tk

from admin.admin import Admin
from game.game import Game
from game.game_service import GameService
from questions.catalog import build_round
from questions.repository import QuestionRepository
from ui.score_repository import ScoreRepository
from ui.theme import Theme
from users.user import User


class App:
    def __init__(self, root, db_path=None, seed_path=None):
        self.root = root
        root.minsize(1100, 750)
        self.theme = Theme(root)

        # Paths
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(here, "data", "space_fractions.db")
        self.seed_path = seed_path or os.path.join(here, "data", "questions.json")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Data layer
        self.conn = sqlite3.connect(self.db_path)
        self.question_repo = QuestionRepository(self.db_path, self.seed_path)
        self.question_repo.init_schema(self.conn)
        if self.question_repo.count(self.conn) == 0 and os.path.exists(self.seed_path):
            self.question_repo.seed_from_json(self.conn)
        self.conn.commit()
        self.score_repo = ScoreRepository(self.db_path)
        self.score_repo.init_schema(self.conn)

        # Domain
        self.admin = Admin(id="a1", username="admin")
        self.player_user = None
        self.player_name = ""
        self.game_service = None

        # Build screens (imported lazily to avoid circular imports)
        from ui.intro import IntroScreen
        from ui.menu import MenuScreen
        from ui.name_entry import NameEntryScreen
        from ui.question_screen import QuestionScreen
        from ui.end_screen import EndScreen
        from ui.high_scores import HighScoresScreen
        from ui.help_screen import HelpScreen
        from ui.admin_screen import AdminScreen

        self.screens = {
            "intro": IntroScreen(self),
            "menu": MenuScreen(self),
            "name": NameEntryScreen(self),
            "question": QuestionScreen(self),
            "end": EndScreen(self),
            "scores": HighScoresScreen(self),
            "help": HelpScreen(self),
            "admin": AdminScreen(self),
        }

        # Fullscreen / Esc bindings
        root.bind("<F11>", self._toggle_fullscreen)
        root.bind("<Escape>", self._leave_fullscreen)

        # Show the intro screen so the window is never blank on startup.
        self.show("intro")

    # -- navigation -------------------------------------------------------
    def show(self, name):
        screen = self.screens[name]
        for s in self.screens.values():
            s.pack_forget()
        screen.pack(fill="both", expand=True)
        screen.on_show()
        if name == "question":
            screen._layout_on_show()

    # -- game flow --------------------------------------------------------
    def start_round(self, name):
        self.player_name = name
        self.player_user = User(id="u1", username=name)
        questions = self.question_repo.list_all(self.conn)
        round_qs = build_round(questions)
        self.game_service = GameService(game_id="g1", questions=round_qs)
        self.game_service.play()
        self.screens["question"].start_round(name, self.game_service)
        self.show("question")

    def record_score(self, name, score, total, percentage, stars):
        self.score_repo.add_score(self.conn, name, score, total, percentage, stars)

    def _toggle_fullscreen(self, _event=None):
        current = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current)

    def _leave_fullscreen(self, _event=None):
        self.root.attributes("-fullscreen", False)


# Global counter to avoid duplicate seeding on repeated create_app calls.
def create_app(root, db_path=None, seed_path=None):
    return App(root, db_path=db_path, seed_path=seed_path)
