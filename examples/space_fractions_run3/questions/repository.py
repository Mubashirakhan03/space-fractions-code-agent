"""QuestionRepository — persistence for questions (SQLite) and in-memory cache."""
from __future__ import annotations

import json
import sqlite3
from typing import List, Optional

from questions.question import Question


class QuestionRepository:
    """Loads / stores Questions, backed by SQLite and a JSON seed file."""

    def __init__(self, db_path: str, seed_path: Optional[str] = None) -> None:
        self.db_path = db_path
        self.seed_path = seed_path

    # -- schema ------------------------------------------------------------
    def init_schema(self, conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                qtype TEXT NOT NULL,
                prompt TEXT NOT NULL,
                options TEXT NOT NULL,
                answer TEXT NOT NULL,
                explanation TEXT NOT NULL DEFAULT ''
            );
            """
        )

    # -- seed --------------------------------------------------------------
    def seed_from_json(self, conn: sqlite3.Connection) -> int:
        """Load questions from a JSON seed file into the DB; returns count."""
        if not self.seed_path:
            return 0
        with open(self.seed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            self.upsert(
                conn,
                Question(
                    id=item["id"],
                    prompt=item["prompt"],
                    options=list(item.get("options", [])),
                    answer=item.get("answer", ""),
                    qtype=item.get("qtype", "equivalent"),
                    explanation=item.get("explanation", ""),
                ),
            )
            count += 1
        return count

    # -- CRUD --------------------------------------------------------------
    def upsert(self, conn: sqlite3.Connection, q: Question) -> None:
        conn.execute(
            """
            INSERT INTO questions (id, qtype, prompt, options, answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                qtype=excluded.qtype,
                prompt=excluded.prompt,
                options=excluded.options,
                answer=excluded.answer,
                explanation=excluded.explanation
            """,
            (q.id, q.qtype, q.prompt, json.dumps(q.options), q.answer, q.explanation),
        )

    def delete(self, conn: sqlite3.Connection, question_id: str) -> bool:
        cur = conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        return cur.rowcount > 0

    def get(self, conn: sqlite3.Connection, question_id: str) -> Optional[Question]:
        cur = conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return self._row_to_question(row)

    def list_all(self, conn: sqlite3.Connection) -> List[Question]:
        cur = conn.execute("SELECT * FROM questions ORDER BY id")
        return [self._row_to_question(r) for r in cur.fetchall()]

    def count(self, conn: sqlite3.Connection) -> int:
        return conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]

    @staticmethod
    def _row_to_question(row) -> Question:
        _id, qtype, prompt, options, answer, explanation = row
        return Question(
            id=_id,
            prompt=prompt,
            options=json.loads(options or "[]"),
            answer=answer,
            qtype=qtype,
            explanation=explanation,
        )
