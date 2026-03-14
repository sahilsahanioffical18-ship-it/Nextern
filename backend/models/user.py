"""
models/user.py  — Repository pattern for the `users` table.
"""
import sqlite3
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database.db import get_db

logger = logging.getLogger(__name__)


class UserModel:
    # ---------- reads ----------

    def find_by_email(self, email: str) -> dict | None:
        with get_db() as conn:
            row = conn.execute(
                "SELECT id, name, email, password_hash FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        return dict(row) if row else None

    def find_by_id(self, user_id: int) -> dict | None:
        with get_db() as conn:
            row = conn.execute(
                "SELECT id, name, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    # ---------- writes ----------

    def create(self, name: str, email: str, password: str) -> int | None:
        """Hash the password and insert a new user. Returns new row id or None."""
        password_hash = generate_password_hash(password)
        try:
            with get_db() as conn:
                cur = conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, password_hash),
                )
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None  # email already exists

    def upsert_google_user(self, name: str, email: str) -> tuple[int, str]:
        """
        Find or create a user that authenticated via Google OAuth.
        Returns (user_id, user_name).
        """
        existing = self.find_by_email(email)
        if existing:
            return existing["id"], existing["name"]
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, "google-oauth"),
            )
            return cur.lastrowid, name

    # ---------- auth ----------

    def authenticate(self, email: str, password: str) -> dict | None:
        """Return the user dict if credentials are valid, else None."""
        user = self.find_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            return {"id": user["id"], "name": user["name"], "email": user["email"]}
        return None
