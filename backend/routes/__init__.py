"""
routes/__init__.py  — exposes all blueprints for registration.
"""
from backend.routes.auth import auth_bp
from backend.routes.pages import pages_bp
from backend.routes.api import api_bp
from backend.routes.mock import mock_bp

__all__ = ["auth_bp", "pages_bp", "api_bp", "mock_bp"]
