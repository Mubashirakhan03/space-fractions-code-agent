"""Question persistence (SQLite) with first-start seeding."""
from __future__ import annotations

import json
import os
import sqlite3
from typing import List, Optional

from questions.question import Question


class QuestionRepository:
    """CRUD for questions, backed by a SQLite file.

    Adapts the PostgreSQL persistence (ASR-1 data durability) to a local
    SQLite file. On open, if the questions table is empty and a seed data file
    exists, seed questions are loaded automatically.
    """

    def __init__(self, db_path: str, seed_path: Optional[str] = None) -> None:
        self._db_path = db_path
        self._seed_path = seed_path
        self._conn: Optional[sqlite3.Connection] = None
        self.open()

    def open(self) -> None:
        if self._conn is not None:
            return
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        schema = _SCHEMA
        self._conn.executescript(schema)
        if self.count() == 0 and self._seed_path and os.path.exists(self._seed_path):
            self.seed_from_file(self._seed_path)
        self._conn.commit()

    # -- queries -----------------------------------------------------------
    def list_all(self) -> List[Question]:
        rows = self._conn.execute(
            "SELECT id, prompt, correct, kind, options FROM questions ORDER BY rowid"
        ).fetchall()
        return [self._row_to_question(r) for r in rows]

    def get(self, question_id: str) -> Optional[Question]:
        row = self._conn.execute(
            "SELECT id, prompt, correct, kind, options FROM questions WHERE id = ?",
            (question_id,),
        ).fetchone()
        return self._row_to_question(row) if row else None

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS n FROM questions").fetchone()
        return int(row["n"])

    # -- mutations ---------------------------------------------------------
    def insert(self, question: Question) -> None:
        self._conn.execute(
            "INSERT INTO questions (id, prompt, correct, kind, options) VALUES (?, ?, ?, ?, ?)",
            (question.id, question.prompt, question.correct, question.kind,
             json.dumps(question.options)),
        )
        self._conn.commit()

    def update(self, question: Question) -> None:
        cur = self._conn.execute(
            "UPDATE questions SET prompt=?, correct=?, kind=?, options=? WHERE id=?",
            (question.prompt, question.correct, question.kind,
             json.dumps(question.options), question.id),
        )
        self._conn.commit()
        if cur.rowcount == 0:
            raise KeyError(f"No question with id {question.id!r}")

    def delete(self, question_id: str) -> None:
        cur = self._conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        self._conn.commit()
        if cur.rowcount == 0:
            raise KeyError(f"No question with id {question_id!r}")

    def replace_all(self, questions: List[Question]) -> None:
        """Atomic replace of the full question set (Admin.updateQuestions)."""
        with self._conn:
            self._conn.execute("DELETE FROM questions")
            for q in questions:
                self._conn.execute(
                    "INSERT INTO questions (id, prompt, correct, kind, options) VALUES (?, ?, ?, ?, ?)",
                    (q.id, q.prompt, q.correct, q.kind, json.dumps(q.options)),
                )

    def seed_from_file(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for item in data:
            q = Question(
                id=item["id"],
                prompt=item["prompt"],
                correct=item["correct"],
                kind=item.get("kind", "choice"),
                options=item.get("options", []),
            )
            self.insert(q)

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def _row_to_question(row: sqlite3.Row) -> Question:
        return Question(
            id=row["id"],
            prompt=row["prompt"],
            correct=row["correct"],
            kind=row["kind"],
            options=json.loads(row["options"]) if row["options"] else [],
        )


_SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    id       TEXT PRIMARY KEY,
    prompt   TEXT NOT NULL,
    correct  TEXT NOT NULL,
    kind     TEXT NOT NULL CHECK (kind IN ('choice', 'typed')),
    options  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS games (
    id         TEXT PRIMARY KEY,
    game_state TEXT NOT NULL,
    score      INTEGER NOT NULL,
    played_at  TEXT NOT NULL
);
"""
