"""ScoreRepository — persist game scores / high scores (View Score use case)."""
from __future__ import annotations

import datetime
import sqlite3
from typing import List


class ScoreRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def init_schema(self, conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                percentage REAL NOT NULL,
                stars INTEGER NOT NULL,
                played_at TEXT NOT NULL
            );
            """
        )

    def add_score(self, conn, name, score, total, percentage, stars) -> None:
        conn.execute(
            "INSERT INTO scores (name, score, total, percentage, stars, played_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, score, total, percentage, stars,
             datetime.datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()

    def top_scores(self, limit: int = 10) -> List[tuple]:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "SELECT name, score, total, percentage, stars, played_at "
                "FROM scores ORDER BY percentage DESC, score DESC, played_at DESC LIMIT ?",
                (limit,),
            )
            return cur.fetchall()
        finally:
            conn.close()
