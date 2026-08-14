"""
interview_service.py
----------------------
Mock-interview flow: pulls career-relevant questions and scores free-text
answers via ai_service (demo mode or an external LLM).
"""

from sqlalchemy.orm import Session

from database import models
from services.ai_service import generate_ai_response

DEFAULT_QUESTIONS = [
    "Tell me about a challenging project you worked on and how you approached it.",
    "How do you stay current with developments in your field?",
    "Describe a time you disagreed with a teammate. How did you resolve it?",
    "Walk me through how you would debug a production issue you've never seen before.",
]


def get_interview_questions(db: Session, career_id: str | None = None) -> list[str]:
    if not career_id:
        return DEFAULT_QUESTIONS

    career = db.query(models.Careers).filter(models.Careers.id == career_id).first()
    if not career:
        return DEFAULT_QUESTIONS

    return [
        f"What draws you to a career as a {career.title}?",
        f"What's the hardest technical problem you'd expect to face as a {career.title}, and why?",
    ] + DEFAULT_QUESTIONS


def score_answer(question: str, answer: str) -> dict:
    """Returns {feedback, score} using the AI service (demo-mode safe)."""
    prompt = (
        f"You are a hiring manager. Interview question: '{question}'\n"
        f"Candidate answer: '{answer}'\n"
        "Give a score 0-100 and one sentence of constructive feedback, "
        "formatted as 'SCORE: <n> | FEEDBACK: <text>'."
    )
    raw = generate_ai_response(prompt)
    return _parse_score_feedback(raw)


def _parse_score_feedback(raw: str) -> dict:
    score = 60.0
    feedback = raw
    try:
        if "SCORE:" in raw and "FEEDBACK:" in raw:
            score_part = raw.split("SCORE:")[1].split("|")[0].strip()
            score = float("".join(c for c in score_part if c.isdigit() or c == "."))
            feedback = raw.split("FEEDBACK:")[1].strip()
    except (ValueError, IndexError):
        pass
    return {"score": min(100.0, max(0.0, score)), "feedback": feedback}
