"""
database/db.py
Database connection manager and schema initializer.
Provides a context-manager helper get_db() so connections
are always properly closed, even when exceptions occur.
"""
import sqlite3
import logging
from contextlib import contextmanager
from backend.config.settings import Config

logger = logging.getLogger(__name__)


@contextmanager
def get_db():
    """
    Context-manager that yields an open sqlite3 connection
    and commits + closes it on exit.

    Usage:
        with get_db() as conn:
            conn.execute(...)
    """
    db_path = Config.get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create all required tables if they don't already exist."""
    try:
        with get_db() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    name          TEXT    NOT NULL,
                    email         TEXT    UNIQUE NOT NULL,
                    password_hash TEXT    NOT NULL,
                    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS attempts (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id         INTEGER NOT NULL,
                    question_id     INTEGER NOT NULL,
                    correct         BOOLEAN NOT NULL,
                    user_answer     TEXT,
                    mock_session_id INTEGER,
                    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );

                CREATE TABLE IF NOT EXISTS mock_sessions (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id         INTEGER NOT NULL,
                    start_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time        TIMESTAMP,
                    total_questions INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
            """)
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.warning("Database initialization warning: %s", exc)
