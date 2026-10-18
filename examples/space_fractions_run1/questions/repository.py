"""Question repository: load from JSON seed + persist in SQLite (QuestionComponent)."""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import List, Optional

from .question import Question


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _apply_schema(conn: sqlite3.Connection) -> None:
    schema = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"
    if schema.exists():
        conn.executescript(schema.read_text(encoding="utf-8"))
    conn.commit()


class QuestionRepository:
    """Loads seed questions from data/questions.json and persists admin edits to SQLite."""

    def __init__(self, db_path: str, seed_path: Optional[str] = None):
        self.db_path = db_path
        self.seed_path = seed_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = _connect(db_path)
        _apply_schema(self._conn)
        self._seed_if_empty()

    def _seed_if_empty(self) -> None:
        cur = self._conn.execute("SELECT COUNT(*) AS n FROM questions")
        if cur.fetchone()["n"] > 0:
            return
        questions = self._load_seed()
        for q in questions:
            self.add(q)

    def _load_seed(self) -> List[Question]:
        path = self.seed_path
        if path is None:
            default = Path(__file__).resolve().parents[1] / "data" / "questions.json"
            path = str(default)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as fh:
            rows = json.load(fh)
        return [
            Question(
                id=str(r.get("id", uuid.uuid4().hex)),
                prompt=r["prompt"],
                type=r["type"],
                options=list(r.get("options", [])),
                answer=r["answer"],
            )
            for r in rows
        ]

    def add(self, question: Question) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO questions (id, prompt, type, options, answer)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                question.id,
                question.prompt,
                question.type,
                json.dumps(question.options),
                question.answer,
            ),
        )
        self._conn.commit()

    def update(self, question: Question) -> None:
        self.add(question)

    def delete(self, question_id: str) -> None:
        self._conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        self._conn.commit()

    def get(self, question_id: str) -> Optional[Question]:
        row = self._conn.execute(
            "SELECT * FROM questions WHERE id = ?", (question_id,)
        ).fetchone()
        return self._row_to_question(row) if row else None

    def all(self) -> List[Question]:
        rows = self._conn.execute("SELECT * FROM questions ORDER BY id").fetchall()
        return [self._row_to_question(r) for r in rows]

    def sample(self, count: int) -> List[Question]:
        import random

        rows = self._conn.execute("SELECT * FROM questions").fetchall()
        if len(rows) <= count:
            return [self._row_to_question(r) for r in rows]
        picked = random.sample(rows, count)
        return [self._row_to_question(r) for r in picked]

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) AS n FROM questions").fetchone()["n"]

    @staticmethod
    def _row_to_question(row) -> Question:
        return Question(
            id=row["id"],
            prompt=row["prompt"],
            type=row["type"],
            options=json.loads(row["options"] or "[]"),
            answer=row["answer"],
        )

    def close(self) -> None:
        self._conn.close()
