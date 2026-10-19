"""SQLite persistence for questions, games and settings.

Adapts the spec's PostgreSQL DDL (`games`, `question_ddl.sql`) to SQLite.
"""
import json
import os
import sqlite3
from pathlib import Path
from typing import List, Optional

from question.question import Question


class Database:
    def __init__(self, path: str = "game.db"):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        with self.conn:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS questions (
                    id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    options TEXT NOT NULL,
                    correct_index INTEGER NOT NULL,
                    explanation TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    total INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    rating TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def seed(self, questions: List[Question]) -> int:
        """Insert seed questions only if the store is empty."""
        if self.count_questions() > 0:
            return 0
        for q in questions:
            self.add_question(q)
        return len(questions)

    def count_questions(self) -> int:
        cur = self.conn.execute("SELECT COUNT(*) AS c FROM questions")
        return cur.fetchone()["c"]

    def add_question(self, q: Question) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO questions (id, prompt, kind, options, correct_index, explanation) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (q.id, q.prompt, q.kind.value, json.dumps(q.getOptions()),
                 q.correct_index, q.explanation),
            )

    def update_question(self, q: Question) -> None:
        self.add_question(q)

    def delete_question(self, qid: str) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM questions WHERE id = ?", (qid,))

    def delete_all_questions(self) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM questions")

    def get_question(self, qid: str) -> Optional[Question]:
        cur = self.conn.execute("SELECT * FROM questions WHERE id = ?", (qid,))
        row = cur.fetchone()
        return self._row_to_question(row) if row else None

    def all_questions(self) -> List[Question]:
        cur = self.conn.execute("SELECT * FROM questions ORDER BY prompt")
        return [self._row_to_question(r) for r in cur.fetchall()]

    @staticmethod
    def _row_to_question(row) -> Question:
        from question.question import QuestionKind
        return Question(
            prompt=row["prompt"],
            options=json.loads(row["options"]),
            correct_index=row["correct_index"],
            kind=QuestionKind(row["kind"]),
            explanation=row["explanation"] or "",
            qid=row["id"],
        )

    def record_game(self, game) -> None:
        from datetime import datetime
        with self.conn:
            self.conn.execute(
                "INSERT INTO games (id, total, score, rating, created_at) VALUES (?, ?, ?, ?, ?)",
                (game.id, game.total, game.score, game.rating(),
                 datetime.now().isoformat(timespec="seconds")),
            )

    def all_games(self) -> list:
        cur = self.conn.execute("SELECT * FROM games ORDER BY created_at DESC")
        return [dict(r) for r in cur.fetchall()]

    def get_setting(self, key: str, default: str = "") -> str:
        cur = self.conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )

    def close(self) -> None:
        self.conn.close()
