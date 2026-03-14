"""
routes/auth.py
Authentication routes: login, register, logout, Google OAuth.
Controllers only — business logic lives in services/auth_service.py.
"""
import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from backend.services.user_service import register_user, login_user, google_upsert

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        result = login_user(
            request.form.get("email", ""),
            request.form.get("password", ""),
        )
        if result["success"]:
            user = result["user"]
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Login successful!", "success")
            return redirect(url_for("pages.dashboard"))
        flash(result["message"], "error")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = register_user(
            request.form.get("name", ""),
            request.form.get("email", ""),
            request.form.get("password", ""),
        )
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("auth.login"))
        flash(result["message"], "error")
    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("pages.home"))


# ─── Google OAuth ─────────────────────────────────────────────────────────────

@auth_bp.route("/login/google")
def login_google():
    """Redirect user to Google OAuth."""
    # Access oauth via app extensions to avoid circular import
    oauth = current_app.extensions.get("authlib.integrations.flask_client")
    if oauth is None or "google" not in oauth._clients:
        flash("Google Sign-In is not configured.", "error")
        return redirect(url_for("auth.login"))
    base_url = os.environ.get("PUBLIC_URL", "http://localhost:8081")
    redirect_uri = f"{base_url}/auth/google/callback"
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/auth/google/callback")
def auth_google_callback():
    """Handle the Google OAuth redirect."""
    oauth = current_app.extensions.get("authlib.integrations.flask_client")
    if oauth is None or "google" not in oauth._clients:
        flash("Google Sign-In is not configured.", "error")
        return redirect(url_for("auth.login"))
    if "error" in request.args:
        flash(request.args.get("error_description", "Google sign-in cancelled."), "error")
        return redirect(url_for("auth.login"))
    if "code" not in request.args:
        flash("Invalid OAuth response. Please try again.", "error")
        return redirect(url_for("auth.login"))

    token = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo") or oauth.google.parse_id_token(token)
    if not userinfo:
        flash("Failed to fetch profile from Google.", "error")
        return redirect(url_for("auth.login"))

    email = userinfo.get("email", "")
    name = userinfo.get("name") or email.split("@")[0]
    result = google_upsert(name, email)
    user = result["user"]
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    flash("Logged in with Google!", "success")
    return redirect(url_for("pages.dashboard"))
