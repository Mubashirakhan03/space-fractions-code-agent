"""Question persistence: SQLite-backed repository seeded from data/questions.json."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from questions.model import Question


class QuestionRepository:
    """Load, query and mutate questions in a SQLite database."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS questions ("
                "id TEXT PRIMARY KEY, prompt TEXT NOT NULL, answer TEXT NOT NULL,"
                "options TEXT NOT NULL DEFAULT '', qtype TEXT NOT NULL DEFAULT 'choice')"
            )
            conn.commit()
        finally:
            conn.close()

    def seed_from_file(self, json_path: Path) -> None:
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        questions = [Question.from_dict(d) for d in data["questions"]]
        self.replace_all(questions)

    def replace_all(self, questions: List[Question]) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM questions")
            for q in questions:
                conn.execute(
                    "INSERT OR REPLACE INTO questions (id, prompt, answer, options, qtype)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (q.id, q.prompt, q.answer, json.dumps(q.options), q.qtype),
                )
            conn.commit()
        finally:
            conn.close()

    def all(self) -> List[Question]:
        conn = self._connect()
        try:
            rows = conn.execute("SELECT * FROM questions").fetchall()
        finally:
            conn.close()
        return [self._row_to_question(r) for r in rows]

    def get(self, question_id: str) -> Optional[Question]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM questions WHERE id = ?", (question_id,)
            ).fetchone()
        finally:
            conn.close()
        return self._row_to_question(row) if row else None

    def upsert(self, question: Question) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO questions (id, prompt, answer, options, qtype)"
                " VALUES (?, ?, ?, ?, ?)",
                (question.id, question.prompt, question.answer,
                 json.dumps(question.options), question.qtype),
            )
            conn.commit()
        finally:
            conn.close()

    def delete(self, question_id: str) -> bool:
        conn = self._connect()
        try:
            cur = conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def _row_to_question(row) -> Question:
        if row is None:
            return None
        options = []
        raw = row["options"] or ""
        if raw:
            options = json.loads(raw)
        return Question(
            id=row["id"],
            prompt=row["prompt"],
            answer=row["answer"],
            options=options,
            qtype=row["qtype"],
        )
