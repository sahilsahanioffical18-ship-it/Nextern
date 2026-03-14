"""
models/mock_session.py  — Repository pattern for the `mock_sessions` table.
"""
import logging
from backend.database.db import get_db

logger = logging.getLogger(__name__)


class MockSessionModel:
    def create(self, user_id: int) -> int:
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO mock_sessions (user_id) VALUES (?)", (user_id,)
            )
            return cur.lastrowid

    def end_session(
        self, session_id: int, total_questions: int, correct_answers: int
    ) -> None:
        with get_db() as conn:
            conn.execute(
                """
                UPDATE mock_sessions
                SET end_time = CURRENT_TIMESTAMP,
                    total_questions = ?,
                    correct_answers = ?
                WHERE id = ?
                """,
                (total_questions, correct_answers, session_id),
            )

    def get_latest(self, user_id: int) -> dict | None:
        with get_db() as conn:
            row = conn.execute(
                """
                SELECT total_questions, correct_answers, start_time, end_time
                FROM mock_sessions WHERE user_id = ?
                ORDER BY start_time DESC LIMIT 1
                """,
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    def count_for_user(self, user_id: int) -> int:
        with get_db() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM mock_sessions WHERE user_id = ?", (user_id,)
            ).fetchone()[0]

    def recent_performance(self, user_id: int, limit: int = 5) -> list[dict]:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT total_questions, correct_answers, start_time
                FROM mock_sessions
                WHERE user_id = ? AND total_questions > 0
                ORDER BY start_time DESC LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def correct_in_session(self, user_id: int, session_id: int) -> int:
        with get_db() as conn:
            return conn.execute(
                """
                SELECT COUNT(*) FROM attempts
                WHERE user_id = ? AND correct = 1 AND mock_session_id = ?
                """,
                (user_id, session_id),
            ).fetchone()[0]
