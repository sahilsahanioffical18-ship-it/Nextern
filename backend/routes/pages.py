"""
routes/pages.py
HTML page routes — all protected pages use the @login_required decorator.
"""
import logging
from flask import Blueprint, render_template, redirect, url_for, session, flash
from backend.middlewares.auth_guard import login_required
from backend.services.stats_service import get_dashboard_stats

logger = logging.getLogger(__name__)
pages_bp = Blueprint("pages", __name__)

RESOURCES_DATA = {
    "technical": [
        {"title": "LeetCode", "description": "Practice coding problems and algorithms", "url": "https://leetcode.com", "type": "Practice Platform"},
        {"title": "Cracking the Coding Interview", "description": "Comprehensive interview preparation book", "url": "https://www.crackingthecodinginterview.com", "type": "Book"},
        {"title": "System Design Primer", "description": "Learn system design concepts and patterns", "url": "https://github.com/donnemartin/system-design-primer", "type": "GitHub Repository"},
    ],
    "behavioral": [
        {"title": "STAR Method Guide", "description": "Structure your behavioral interview answers", "url": "https://www.indeed.com/career-advice/interviewing/how-to-use-the-star-interview-response-technique", "type": "Article"},
        {"title": "Common Behavioral Questions", "description": "Prepare for typical behavioral interview questions", "url": "https://www.glassdoor.com/blog/behavioral-interview-questions/", "type": "Article"},
    ],
    "general": [
        {"title": "Interview Tips and Strategies", "description": "General advice for interview success", "url": "https://www.indeed.com/career-advice/interviewing", "type": "Resource Hub"},
        {"title": "Salary Negotiation Guide", "description": "Learn how to negotiate your offer", "url": "https://www.kalzumeus.com/2012/01/23/salary-negotiation/", "type": "Article"},
    ],
}


# ─── Public pages ─────────────────────────────────────────────────────────────

@pages_bp.route("/")
def home():
    return render_template("home.html")


@pages_bp.route("/features")
def features():
    return render_template("features.html")


@pages_bp.route("/resources")
def resources():
    return render_template("resources.html", resources=RESOURCES_DATA)


@pages_bp.route("/career_roadmap")
def career_roadmap():
    return render_template("career_roadmap.html")


# ─── Protected pages ─────────────────────────────────────────────────────────

@pages_bp.route("/dashboard")
@login_required
def dashboard():
    try:
        stats = get_dashboard_stats(session["user_id"])
    except Exception as exc:
        logger.error("Dashboard stats error: %s", exc)
        stats = {
            "total_attempted": 0, "correct_answers": 0, "accuracy": 0,
            "score_out_of_10": 0, "total_interviews": 0, "total_study_time": 0,
            "current_streak": 0, "weak_topics": [], "recent_interviews": [],
        }
    return render_template("dashboard.html", stats=stats)


@pages_bp.route("/practice")
@login_required
def practice_page():
    return render_template("practice.html")


@pages_bp.route("/resume")
@login_required
def resume():
    return render_template("resume.html")


@pages_bp.route("/ai-interview")
@login_required
def ai_interview():
    return render_template("ai_interview.html")


@pages_bp.route("/calendar")
@login_required
def calendar():
    return render_template("calendar.html")


@pages_bp.route("/custom")
@login_required
def custom_practice():
    return render_template("custom_practice.html")


@pages_bp.route("/feedback")
@login_required
def feedback():
    from backend.models.attempt import AttemptModel
    from backend.utils.questions import load_questions

    attempts = AttemptModel().get_recent(session["user_id"])
    questions_dict = {q["id"]: q for q in load_questions()}
    feedback_data = [
        {
            "attempt_id": a["id"],
            "question": questions_dict.get(a["question_id"]),
            "correct": a["correct"],
            "user_answer": a["user_answer"],
            "timestamp": a["timestamp"],
        }
        for a in attempts
        if a["question_id"] in questions_dict
    ]
    return render_template("feedback.html", feedback_data=feedback_data)
