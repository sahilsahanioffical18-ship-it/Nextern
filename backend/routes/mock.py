"""
routes/mock.py
Mock interview session routes: start, get question, submit answer, end, results.
"""
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.middlewares.auth_guard import login_required
from backend.services import mock_service
from backend.utils.response import success_response, error_response

logger = logging.getLogger(__name__)
mock_bp = Blueprint("mock", __name__, url_prefix="/mock")


@mock_bp.route("")
@login_required
def mock_interview():
    session_id = mock_service.start_session(session["user_id"])
    session["mock_session_id"] = session_id
    session["mock_start_time"] = datetime.now().isoformat()
    session["mock_questions_answered"] = 0
    return render_template("mock_interview.html", session_id=session_id)


@mock_bp.route("/question")
@login_required
def mock_question():
    if "mock_session_id" not in session:
        return error_response("No active mock session.", 400)
    question = mock_service.get_random_question()
    if not question:
        return error_response("No questions available.", 404)
    return success_response({"question": question})


@mock_bp.route("/submit", methods=["POST"])
@login_required
def mock_submit_answer():
    if "mock_session_id" not in session:
        return error_response("No active mock session.", 400)
    body = request.get_json(silent=True) or {}
    question_id = body.get("question_id")
    user_answer = body.get("user_answer", "")
    result = mock_service.submit_answer(
        session["user_id"],
        session["mock_session_id"],
        question_id,
        user_answer,
    )
    session["mock_questions_answered"] = session.get("mock_questions_answered", 0) + 1
    return success_response({**result, "questions_answered": session["mock_questions_answered"]})


@mock_bp.route("/end", methods=["POST"])
@login_required
def end_mock_interview():
    if "mock_session_id" not in session:
        return error_response("No active mock session.", 400)
    result = mock_service.end_session(
        session["user_id"],
        session["mock_session_id"],
        session.get("mock_questions_answered", 0),
    )
    session.pop("mock_session_id", None)
    session.pop("mock_start_time", None)
    session.pop("mock_questions_answered", None)
    return success_response(result)


@mock_bp.route("/results")
@login_required
def mock_results():
    results = mock_service.get_latest_results(session["user_id"])
    if not results:
        flash("No mock interview session found.", "error")
        return redirect(url_for("pages.dashboard"))
    return render_template("mock_results.html", results=results)
