"""
middlewares/auth_guard.py
login_required decorator — replaces the repeated
  if 'user_id' not in session: ...
pattern found in every protected route.
"""
import logging
from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify

logger = logging.getLogger(__name__)


def login_required(f):
    """
    Decorator for page routes that require an authenticated session.
    Redirects to /login with a flash message if not logged in.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def api_login_required(f):
    """
    Decorator for JSON API endpoints that require authentication.
    Returns a 401 JSON response if not logged in.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "data": None, "error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated
