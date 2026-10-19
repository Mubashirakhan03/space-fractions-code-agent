"""Question and score persistence (SQLite) + seed loading.

ASR-1 (data durability): question data and score history survive restarts.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import List, Optional

from question.question import Question, QuestionKind

SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    correct TEXT NOT NULL,
    options TEXT NOT NULL,
    kind TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    played_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    role TEXT NOT NULL
);
"""


def _data_dir() -> Path:
    base = Path(os.environ.get("SPACE_FRACTIONS_HOME", Path.home() / ".space_fractions"))
    base.mkdir(parents=True, exist_ok=True)
    return base


def _seed_file() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "questions.json"


class QuestionRepository:
    """CRUD for persisted questions plus seed auto-load on empty store."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(_data_dir() / "space_fractions.db")
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.executescript(SCHEMA)
        self._conn.commit()
        self._seed_if_empty()

    def close(self) -> None:
        self._conn.close()

    def _seed_if_empty(self) -> None:
        cur = self._conn.execute("SELECT COUNT(*) FROM questions")
        if cur.fetchone()[0] > 0:
            return
        seed = _seed_file()
        if seed.exists():
            data = json.loads(seed.read_text(encoding="utf-8"))
            for item in data.get("questions", []):
                self._insert(Question.from_kwargs(**item))
            self._ensure_default_user()

    def _ensure_default_user(self) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO users (id, username, role) VALUES (?, ?, ?)",
            ("u-default", "Player", "user"),
        )
        self._conn.execute(
            "INSERT OR IGNORE INTO users (id, username, role) VALUES (?, ?, ?)",
            ("u-admin", "Admin", "admin"),
        )
        self._conn.commit()

    def _insert(self, q: Question) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO questions (id, prompt, correct, options, kind) "
            "VALUES (?, ?, ?, ?, ?)",
            (q.id, q.prompt, q.correct, json.dumps(q.options), q.kind.value),
        )

    def list_all(self) -> List[Question]:
        rows = self._conn.execute(
            "SELECT id, prompt, correct, options, kind FROM questions ORDER BY id"
        ).fetchall()
        out = []
        for rid, prompt, correct, options, kind in rows:
            out.append(
                Question(
                    id=rid,
                    prompt=prompt,
                    correct=correct,
                    options=json.loads(options),
                    kind=QuestionKind(kind),
                )
            )
        return out

    def add(self, q: Question) -> List[str]:
        errors = q.validate()
        if errors:
            return errors
        self._insert(q)
        self._conn.commit()
        return []

    def update(self, q: Question) -> List[str]:
        errors = q.validate()
        if errors:
            return errors
        self._insert(q)
        self._conn.commit()
        return []

    def delete(self, question_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def record_score(self, username: str, score: int, total: int) -> None:
        import uuid
        from datetime import datetime

        self._conn.execute(
            "INSERT INTO games (id, username, score, total, played_at) VALUES (?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                username,
                score,
                total,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        self._conn.commit()

    def list_scores(self) -> List[dict]:
        rows = self._conn.execute(
            "SELECT username, score, total, played_at FROM games ORDER BY played_at DESC"
        ).fetchall()
        return [
            {"username": u, "score": s, "total": t, "played_at": p}
            for u, s, t, p in rows
        ]


__all__ = ["QuestionRepository"]
