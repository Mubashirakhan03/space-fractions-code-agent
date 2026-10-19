"""Question persistence: load seed JSON and sync to SQLite."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import List, Optional

from .question import Question, QType

DEFAULT_QUESTIONS_PATH = Path(__file__).resolve().parent.parent / "data" / "questions.json"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


class QuestionRepository:
    """Backs QuestionComponent: question management + data persistence."""

    def __init__(self, db_path: str = "data/spacefractions.db",
                 seed_path: Optional[str] = None):
        self.db_path = db_path
        self.seed_path = seed_path or str(DEFAULT_QUESTIONS_PATH)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        self._ensure_schema(conn)
        return conn

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        if SCHEMA_PATH.exists():
            with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
                conn.executescript(fh.read())
        else:
            conn.execute("CREATE TABLE IF NOT EXISTS questions (id TEXT PRIMARY KEY, qtype TEXT, prompt TEXT, options TEXT, answer TEXT, created_at TEXT)")
        conn.commit()

    def load_all(self) -> List[Question]:
        """Return all questions from the in-memory cache (rebuilt lazily)."""
        return self._load_from_db() or self.load_seed()

    def load_seed(self) -> List[Question]:
        """Load questions from the seed JSON file."""
        path = Path(self.seed_path)
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return [Question.from_dict(item) for item in data]

    def _load_from_db(self) -> List[Question]:
        conn = self._connect()
        try:
            rows = conn.execute("SELECT id, qtype, prompt, options, answer FROM questions").fetchall()
        finally:
            conn.close()
        if not rows:
            return []
        out = []
        for r in rows:
            options = json.loads(r["options"]) if r["options"] else None
            out.append(Question(
                id=r["id"], prompt=r["prompt"], answer=r["answer"],
                qtype=r["qtype"], options=options))
        return out

    def seed_database(self) -> int:
        """Insert seed questions into SQLite (idempotent) and return the count."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            for q in self.load_seed():
                cur.execute(
                    "INSERT OR IGNORE INTO questions (id, qtype, prompt, options, answer) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (q.id, q.qtype.value, q.getPrompt(),
                     json.dumps(q.getOptions()), str(q.answer)))
            conn.commit()
            return cur.rowcount if cur.rowcount > 0 else len(self.load_seed())
        finally:
            conn.close()

    def add(self, question: Question) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO questions (id, qtype, prompt, options, answer) "
                "VALUES (?, ?, ?, ?, ?)",
                (question.id, question.qtype.value, question.getPrompt(),
                 json.dumps(question.getOptions()), str(question.answer)))
            conn.commit()
        finally:
            conn.close()

    def update(self, question: Question) -> None:
        self.add(question)

    def delete(self, question_id: str) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            conn.commit()
        finally:
            conn.close()

    def next_id(self) -> str:
        existing = [q.id for q in self.load_all()]
        i = 1
        while f"q{i}" in existing:
            i += 1
        return f"q{i}"
