"""
utils/response.py
Standardized JSON response helpers for consistent API output.

All JSON endpoints should use these helpers:
    return success_response(data)
    return error_response("Not found", 404)
"""
from flask import jsonify


def success_response(data: dict | list | None = None, status: int = 200):
    """Return a uniform success envelope."""
    return jsonify({"success": True, "data": data, "error": None}), status


def error_response(message: str, status: int = 400):
    """Return a uniform error envelope."""
    return jsonify({"success": False, "data": None, "error": message}), status
