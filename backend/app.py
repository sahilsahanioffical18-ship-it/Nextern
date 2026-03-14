"""
backend/app.py
Application factory — the single source of truth for creating the Flask app.

Usage:
    from app import create_app
    app = create_app()
"""
import logging
import sys
import os

# Ensure the project root is on the path so 'from backend.*' works
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import render_template
from authlib.integrations.flask_client import OAuth
from backend.config.settings import get_config
from backend.database.db import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# OAuth object exported so route modules can reference it
oauth = OAuth()


def create_app() -> "Flask":  # noqa: F821
    from flask import Flask

    config = get_config()

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    # ── Core config ────────────────────────────────────────────────────────
    app.secret_key = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG
    app.config["GOOGLE_CLIENT_ID"] = config.GOOGLE_CLIENT_ID
    app.config["GOOGLE_CLIENT_SECRET"] = config.GOOGLE_CLIENT_SECRET

    # ── OAuth ──────────────────────────────────────────────────────────────
    oauth.init_app(app)
    if config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET:
        oauth.register(
            name="google",
            client_id=config.GOOGLE_CLIENT_ID,
            client_secret=config.GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    # ── Database ───────────────────────────────────────────────────────────
    init_db()

    # ── Blueprints ─────────────────────────────────────────────────────────
    from backend.routes import auth_bp, pages_bp, api_bp, mock_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(mock_bp)

    # ── Centralised error handlers ─────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("500 error: %s", error)
        return render_template("errors/500.html"), 500

    logger.info("App created in %s mode.", "debug" if config.DEBUG else "production")
    return app


# ── Dev entrypoint ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)