"""
services/mock_service.py
Business logic for mock interview sessions.
"""
import logging
import random
from flask import session
from datetime import datetime
from backend.models.attempt import AttemptModel
from backend.models.mock_session import MockSessionModel
from backend.utils.questions import load_questions

logger = logging.getLogger(__name__)
_attempt_model = AttemptModel()
_mock_model = MockSessionModel()


def start_session(user_id: int) -> int:
    """Create a new mock session row and return its id."""
    session_id = _mock_model.create(user_id)
    return session_id


def get_random_question() -> dict | None:
    questions = load_questions()
    if not questions:
        return None
    return random.choice(questions)


def submit_answer(
    user_id: int,
    mock_session_id: int,
    question_id: int,
    user_answer: str,
) -> dict:
    """Record a mock answer. Correctness = answer is at least 10 chars."""
    correct = len(user_answer.strip()) > 10
    _attempt_model.insert(user_id, question_id, correct, user_answer, mock_session_id)
    return {"correct": correct}


def end_session(user_id: int, mock_session_id: int, questions_answered: int) -> dict:
    """Finalise the mock session and return summary stats."""
    correct_answers = _mock_model.correct_in_session(user_id, mock_session_id)
    _mock_model.end_session(mock_session_id, questions_answered, correct_answers)
    score = round((correct_answers / questions_answered * 100) if questions_answered > 0 else 0, 1)
    return {
        "total_questions": questions_answered,
        "correct_answers": correct_answers,
        "score": score,
    }


def get_latest_results(user_id: int) -> dict | None:
    """Fetch most recent completed mock session for the results page."""
    result = _mock_model.get_latest(user_id)
    if not result:
        return None

    total = result["total_questions"]
    correct = result["correct_answers"]
    score = round((correct / total * 100) if total > 0 else 0, 1)

    start_dt = _parse_ts(result.get("start_time"))
    end_dt = _parse_ts(result.get("end_time"))
    duration = str(end_dt - start_dt).split(".")[0] if (start_dt and end_dt) else "Unknown"

    return {
        "total_questions": total,
        "correct_answers": correct,
        "score": score,
        "duration": duration,
    }


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return None
