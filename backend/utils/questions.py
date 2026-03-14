"""
utils/questions.py
Loads the static questions bank from data/questions.json.
"""
import json
import logging
import os

logger = logging.getLogger(__name__)

_QUESTIONS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "questions.json")
_cache: list | None = None


def load_questions() -> list[dict]:
    """Return all questions. Result is cached after first load."""
    global _cache
    if _cache is not None:
        return _cache
    try:
        with open(_QUESTIONS_PATH, "r") as f:
            data = json.load(f)
            _cache = data.get("questions", [])
            logger.info("Loaded %d questions.", len(_cache))
            return _cache
    except Exception as exc:
        logger.error("Failed to load questions: %s", exc)
        return []
