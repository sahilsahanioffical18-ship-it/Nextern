"""
routes/api.py
JSON API endpoints: stats, submit-answer, roadmap, Gemini AI, resume.
All responses use utils/response.py for a consistent envelope.
"""
import json
import logging
from datetime import datetime
from flask import Blueprint, request, session
from backend.middlewares.auth_guard import api_login_required
from backend.models.attempt import AttemptModel
from backend.services import stats_service, gemini_service
from backend.utils.response import success_response, error_response

logger = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__)

_attempt_model = AttemptModel()


# ─── Stats ────────────────────────────────────────────────────────────────────

@api_bp.route("/api/stats")
@api_login_required
def api_stats():
    data = stats_service.get_api_stats(session["user_id"])
    return success_response(data)


# ─── Practice answer submission ───────────────────────────────────────────────

@api_bp.route("/submit-answer", methods=["POST"])
@api_login_required
def submit_answer():
    body = request.get_json(silent=True) or {}
    question_id = body.get("question_id")
    correct = bool(body.get("correct", False))
    user_answer = body.get("user_answer", "")
    _attempt_model.insert(session["user_id"], question_id, correct, user_answer)
    return success_response({"message": "Answer submitted successfully."})


# ─── Career Roadmap ───────────────────────────────────────────────────────────

@api_bp.route("/api/roadmap", methods=["POST"])
def api_roadmap():
    body = request.get_json(force=True, silent=True) or {}
    html = gemini_service.generate_roadmap_html(
        job_role=body.get("jobRole", ""),
        experience=body.get("experience", ""),
        target_company=body.get("targetCompany", ""),
        skills=body.get("skills", ""),
    )
    return success_response({"html": html})


# ─── Gemini Q&A ───────────────────────────────────────────────────────────────

@api_bp.route("/api/gemini/qa", methods=["POST"])
def gemini_qa():
    body = request.get_json(force=True, silent=True) or {}
    prompt = body.get("prompt", "").strip()
    if not prompt:
        return error_response("Prompt is required.", 400)
    answer = gemini_service.ask_gemini(prompt)
    return success_response({"answer": answer})


# ─── DSA Solver ───────────────────────────────────────────────────────────────

@api_bp.route("/api/gemini/solve", methods=["POST"])
@api_login_required
def gemini_solve():
    body = request.get_json(force=True, silent=True) or {}
    title = body.get("title", "").strip()
    if not title:
        return error_response("Problem title is required.", 400)
    solution = gemini_service.solve_dsa_problem(
        title=title,
        description=body.get("description", ""),
        topics=body.get("topics", []),
        language=body.get("language", "Python"),
    )
    return success_response({"solution": solution})


# ─── AI Interview ─────────────────────────────────────────────────────────────

@api_bp.route("/api/ai-interview/start", methods=["POST"])
@api_login_required
def ai_interview_start():
    from backend.models.mock_session import MockSessionModel
    body = request.get_json(force=True, silent=True) or {}
    role = body.get("role", "Software Engineer").strip()
    level = body.get("level", "Fresher").strip()
    company = body.get("company", "Any").strip()
    topic = body.get("topic", "technical").strip()
    question_count = int(body.get("questionCount", 5))
    time_limit = int(body.get("timeLimit", 30))

    mock_session_id = MockSessionModel().create(session["user_id"])
    session.update({
        "mock_session_id": mock_session_id,
        "ai_round": 1,
        "ai_question_count": question_count,
        "ai_time_limit": time_limit,
        "ai_topic": topic,
    })
    qobj = gemini_service.generate_interview_question(role, level, company, topic)
    return success_response({
        "session_id": mock_session_id,
        "question": qobj.get("question", ""),
        "topic": qobj.get("topic", "General"),
    })


@api_bp.route("/api/ai-interview/answer", methods=["POST"])
@api_login_required
def ai_interview_answer():
    if "mock_session_id" not in session:
        return error_response("No active interview session.", 400)
    body = request.get_json(silent=True) or {}
    question_text = body.get("question", "").strip()
    user_answer = body.get("answer", "").strip()
    if not question_text or not user_answer:
        return error_response("Question and answer are required.", 400)

    evaluation = gemini_service.evaluate_answer(question_text, user_answer)

    # Persist attempt
    try:
        _attempt_model.insert(
            session["user_id"], 0,
            int(evaluation.get("score_10", 0)) >= 7,
            json.dumps({"q": question_text, "a": user_answer, "feedback": evaluation}),
            session["mock_session_id"],
        )
    except Exception as exc:
        logger.error("DB insert failed in ai_interview_answer: %s", exc)

    current_round = int(session.get("ai_round", 1))
    question_count = int(session.get("ai_question_count", 5))
    if current_round >= question_count:
        return success_response({
            "evaluation": evaluation,
            "interview_complete": True,
            "final_score": evaluation.get("score_10", 0),
            "total_questions": current_round,
        })

    session["ai_round"] = current_round + 1
    topic = session.get("ai_topic", "technical")
    nxt = gemini_service.generate_next_question(question_text, topic)
    return success_response({
        "evaluation": evaluation,
        "next_question": nxt.get("question", ""),
        "next_topic": nxt.get("topic", "General"),
        "round": session["ai_round"],
    })


# ─── Resume ───────────────────────────────────────────────────────────────────

@api_bp.route("/api/gemini/resume", methods=["POST"])
@api_login_required
def gemini_resume():
    body = request.get_json(force=True, silent=True) or {}
    result = gemini_service.generate_resume_content(
        profile=body.get("profile", {}),
        skills=body.get("skills", []),
        projects=body.get("projects", []),
        experience=body.get("experience", []),
        education=body.get("education", []),
        target=body.get("target", "Software Engineer"),
        seniority=body.get("seniority", "Fresher"),
    )
    return success_response({"result": result})


@api_bp.route("/api/resume/ai-generate", methods=["POST"])
def resume_ai_generate():
    body = request.get_json(force=True, silent=True) or {}
    first_name = body.get("firstName", "John").strip()
    last_name = body.get("lastName", "Doe").strip()
    email = body.get("email", "john.doe@example.com").strip()
    phone = body.get("phone", "+1-555-555-5555").strip()
    target_role = body.get("role", "Software Engineer").strip()

    resume_data = gemini_service.generate_resume_from_minimal(first_name, last_name, email, phone, target_role)
    if resume_data:
        resume_data.setdefault("firstName", first_name)
        resume_data.setdefault("lastName", last_name)
        resume_data.setdefault("email", email)
        resume_data.setdefault("phone", phone)
        return success_response({"resume": resume_data})

    # Local fallback template
    year = datetime.utcnow().year
    fallback = {
        "firstName": first_name, "lastName": last_name, "email": email, "phone": phone,
        "location": "Your City, Country", "linkedin": "https://www.linkedin.com/in/your-profile",
        "summary": f"Aspiring {target_role} with strong CS fundamentals.",
        "experience": [{"jobTitle": target_role, "company": "Demo Company", "startDate": f"06/{year-1}", "endDate": "Present", "description": "Built features and collaborated with team."}],
        "education": [{"degree": "B.Tech in Computer Science", "school": "ABC University", "gradYear": str(year), "gpa": "8.0/10"}],
        "skills": ["Python", "Flask", "JavaScript", "SQL"],
        "projects": [{"name": "Portfolio Website", "url": "https://example.com", "description": "Personal portfolio with responsive UI."}],
    }
    return success_response({"resume": fallback})


@api_bp.route("/api/resume/generate", methods=["POST"])
def generate_resume():
    body = request.get_json(force=True, silent=True) or {}
    personal_info = {
        "name": f"{body.get('firstName','')} {body.get('lastName','')}".strip(),
        "email": body.get("email", ""), "phone": body.get("phone", ""),
        "location": body.get("location", ""), "linkedin": body.get("linkedin", ""),
        "summary": body.get("summary", ""),
    }
    analysis = gemini_service.analyze_resume_ats(
        personal_info=personal_info,
        experience=body.get("experience", []),
        education=body.get("education", []),
        skills=body.get("skills", []),
        projects=body.get("projects", []),
    )
    return success_response(analysis)


@api_bp.route("/api/resume/test", methods=["GET"])
def test_resume():
    return success_response({"message": "Resume API is working."})
