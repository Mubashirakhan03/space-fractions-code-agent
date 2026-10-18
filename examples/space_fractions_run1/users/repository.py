"""Score repository (SQLite) for the View Score / High Scores use case."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List


class ScoreRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        schema = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"
        if schema.exists():
            self._conn.executescript(schema.read_text(encoding="utf-8"))
        self._conn.commit()

    def add_score(
        self, username: str, score: int, total: int, percentage: float, stars: int
    ) -> int:
        cur = self._conn.execute(
            "INSERT INTO scores (username, score, total, percentage, stars, timestamp)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                username,
                score,
                total,
                percentage,
                stars,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def high_scores(self, limit: int = 10) -> List[dict]:
        rows = self._conn.execute(
            "SELECT username, score, total, percentage, stars, timestamp"
            " FROM scores ORDER BY percentage DESC, timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        self._conn.close()
