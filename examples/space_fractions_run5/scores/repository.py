"""Score persistence for the high-scores table."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


class ScoreRepository:
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
                "CREATE TABLE IF NOT EXISTS scores ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,"
                "score INTEGER NOT NULL, total INTEGER NOT NULL,"
                "percentage REAL NOT NULL, played_at TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_scores_percentage "
                "ON scores (percentage DESC, score DESC, played_at DESC)"
            )
            conn.commit()
        finally:
            conn.close()

    def save(self, username: str, score: int, total: int, percentage: float) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO scores (username, score, total, percentage, played_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (username, score, total, percentage, datetime.now().isoformat()),
            )
            conn.commit()
        finally:
            conn.close()

    def top(self, limit: int = 10) -> List[Tuple[str, int, int, float]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT username, score, total, percentage FROM scores "
                "ORDER BY percentage DESC, score DESC, played_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        finally:
            conn.close()
        return [(r["username"], r["score"], r["total"], r["percentage"]) for r in rows]
