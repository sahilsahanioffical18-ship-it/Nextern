"""
models/attempt.py  — Repository pattern for the `attempts` table.
"""
import logging
from backend.database.db import get_db

logger = logging.getLogger(__name__)


class AttemptModel:
    def insert(
        self,
        user_id: int,
        question_id: int,
        correct: bool,
        user_answer: str = "",
        mock_session_id: int | None = None,
    ) -> int:
        with get_db() as conn:
            cur = conn.execute(
                """
                INSERT INTO attempts
                    (user_id, question_id, correct, user_answer, mock_session_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, question_id, int(correct), user_answer, mock_session_id),
            )
            return cur.lastrowid

    def get_user_stats(self, user_id: int) -> dict:
        with get_db() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM attempts WHERE user_id = ?", (user_id,)
            ).fetchone()[0]
            correct = conn.execute(
                "SELECT COUNT(*) FROM attempts WHERE user_id = ? AND correct = 1",
                (user_id,),
            ).fetchone()[0]
        accuracy = round((correct / total * 100) if total else 0, 1)
        return {
            "total_attempted": total,
            "correct_answers": correct,
            "accuracy": accuracy,
        }

    def get_weak_topics(self, user_id: int, limit: int = 3) -> list[dict]:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT question_id, COUNT(*) AS incorrect_count
                FROM attempts
                WHERE user_id = ? AND correct = 0
                GROUP BY question_id
                ORDER BY incorrect_count DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_practice_dates(self, user_id: int) -> list[str]:
        """Return a list of distinct practice date strings (YYYY-MM-DD) desc."""
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT DATE(timestamp) AS practice_date
                FROM attempts
                WHERE user_id = ?
                GROUP BY DATE(timestamp)
                ORDER BY practice_date DESC
                """,
                (user_id,),
            ).fetchall()
        return [r["practice_date"] for r in rows]

    def get_recent(self, user_id: int, limit: int = 20) -> list[dict]:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT id, question_id, correct, user_answer, timestamp
                FROM attempts WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]
