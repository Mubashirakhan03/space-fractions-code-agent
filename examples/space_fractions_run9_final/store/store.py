"""SQLite persistence for questions and game state (ASR-1 data durability)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from question.question import Question

SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'identify',
    correct_value TEXT NOT NULL,
    choices TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state TEXT NOT NULL
);
"""


class QuestionStore:
    """Persists the question pool in a local SQLite file."""

    def __init__(self, db_path: Path, seed_path: Optional[Path] = None,
                 seed_json: Optional[str] = None) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.seed_path = seed_path
        self._seed_json = seed_json
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.executescript(SCHEMA)
        self._conn.commit()
        if self.count() == 0:
            self._load_seed()

    def _load_seed(self) -> None:
        seed_questions = self.load_seed_questions()
        for q in seed_questions:
            self.add_question(q)

    def load_seed_questions(self) -> List[Question]:
        if self._seed_json is not None:
            raw = json.loads(self._seed_json)
        elif self.seed_path is not None and self.seed_path.exists():
            raw = json.loads(self.seed_path.read_text(encoding="utf-8"))
        else:
            raw = []
        return [Question(**item) for item in raw]

    def count(self) -> int:
        cur = self._conn.execute("SELECT COUNT(*) FROM questions")
        return cur.fetchone()[0]

    def list_questions(self) -> List[Question]:
        cur = self._conn.execute(
            "SELECT id, prompt, kind, correct_value, choices FROM questions"
        )
        return [
            Question(
                id=row[0],
                prompt=row[1],
                kind=row[2],
                correct_value=row[3],
                choices=json.loads(row[4]),
            )
            for row in cur.fetchall()
        ]

    def get_question(self, question_id: str) -> Optional[Question]:
        cur = self._conn.execute(
            "SELECT id, prompt, kind, correct_value, choices FROM questions WHERE id=?",
            (question_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return Question(
            id=row[0],
            prompt=row[1],
            kind=row[2],
            correct_value=row[3],
            choices=json.loads(row[4]),
        )

    def add_question(self, question: Question) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO questions (id, prompt, kind, correct_value, choices) "
            "VALUES (?, ?, ?, ?, ?)",
            (question.id, question.prompt, question.kind,
             question.correct_value, json.dumps(question.choices)),
        )
        self._conn.commit()

    def update_question(self, question: Question) -> None:
        self.add_question(question)

    def delete_question(self, question_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM questions WHERE id=?", (question_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def replace_all(self, questions: List[Question]) -> None:
        self._conn.execute("DELETE FROM questions")
        for q in questions:
            self.add_question(q)

    def close(self) -> None:
        self._conn.close()
