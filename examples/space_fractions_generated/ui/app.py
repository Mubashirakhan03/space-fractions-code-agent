"""Application controller: builds screens, coordinates game flow, persistence.

Contract: create_app(root) -> App (no mainloop); App.screens dict; App.show(name).
"""
from __future__ import annotations

import json
import os
import sqlite3
import tkinter as tk

from game.game import Game
from questions.repository import QuestionRepository

from .intro_screen import IntroScreen
from .menu_screen import MenuScreen
from .name_screen import NameScreen
from .question_screen import QuestionScreen
from .end_screen import EndScreen
from .high_scores_screen import HighScoresScreen
from .help_screen import HelpScreen
from .admin_screen import AdminScreen

SCREENS_ORDER = ["intro", "menu", "name", "question", "end",
                 "high_scores", "help", "admin"]


class App:
    def __init__(self, root, db_path="data/spacefractions.db"):
        self.root = root
        self.db_path = db_path
        self.repository = QuestionRepository(db_path=db_path)
        self._ensure_schema()
        self.repository.seed_database()

        self.game: Game | None = None
        self._player_name = ""

        self.screens = {
            "intro": IntroScreen(root, self),
            "menu": MenuScreen(root, self),
            "name": NameScreen(root, self),
            "question": QuestionScreen(root, self),
            "end": EndScreen(root, self),
            "high_scores": HighScoresScreen(root, self),
            "help": HelpScreen(root, self),
            "admin": AdminScreen(root, self),
        }
        for screen in self.screens.values():
            screen.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _ensure_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql")
        conn = sqlite3.connect(self.db_path)
        try:
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as fh:
                    conn.executescript(fh.read())
            else:
                conn.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, player_name TEXT, score INTEGER, total INTEGER, percentage REAL, stars INTEGER, played_at TEXT)")
                conn.execute("CREATE TABLE IF NOT EXISTS questions (id TEXT PRIMARY KEY, qtype TEXT, prompt TEXT, options TEXT, answer TEXT, created_at TEXT)")
                conn.execute("CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY AUTOINCREMENT, player_name TEXT, game_state TEXT, created_at TEXT)")
            conn.commit()
        finally:
            conn.close()

    # -- helpers -------------------------------------------------------
    def show(self, name):
        if name not in self.screens:
            name = "menu"
        self.screens[name].tkraise()

    def set_player_name(self, name):
        self._player_name = name

    def start_game(self):
        questions = self.repository.load_all()
        self.game = Game(questions, player_name=self._player_name)

    def pause_game(self):
        if self.game:
            try:
                self.game.pause()
            except Exception:
                return
            self.screens["question"].show_pause_overlay(True)

    def resume_game(self):
        if self.game:
            try:
                self.game.resume()
            except Exception:
                return
            self.screens["question"].show_pause_overlay(False)

    def finish_game(self):
        """Persist the result to the scores table."""
        if self.game is None:
            return
        result = self.game.result()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT INTO scores (player_name, score, total, percentage, stars) "
                "VALUES (?, ?, ?, ?, ?)",
                (result["player_name"], result["score"], result["total"],
                 result["percentage"], result["stars"]))
            conn.commit()
        finally:
            conn.close()


def create_app(root) -> App:
    root.minsize(1100, 750)
    return App(root)
