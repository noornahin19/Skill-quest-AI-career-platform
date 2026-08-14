"""
adaptive_learning_service.py
------------------------------
Implements the adaptive-difficulty flow from the architecture diagram:

    Student completes challenge -> Get score
        <50%       -> Prerequisite (needs foundational review)
        50-75%      -> Practice (reinforce at current level)
        >75%       -> Advanced (ready to level up)
    -> Update Roadmap -> Save Learning Progress -> Update Skill DNA
    -> Recalculate Readiness
"""

from sqlalchemy.orm import Session

from database import models
from services import skill_dna_service, roadmap_service, readiness_service


def recommend_next_difficulty(score: float) -> str:
    if score < 50:
        return "prerequisite"
    elif score <= 75:
        return "practice"
    return "advanced"


def process_challenge_result(
    db: Session, user_id: str, challenge_id: str, submitted_answer: str
) -> models.ChallengeAttempts:
    """
    Full pipeline for a challenge submission, following the diagram end to end.
    """
    challenge = db.query(models.Challenges).filter(models.Challenges.id == challenge_id).first()
    if not challenge:
        raise ValueError("Challenge not found")

    score = _grade_submission(challenge, submitted_answer)
    next_difficulty = recommend_next_difficulty(score)
    passed = score >= 50

    attempt = models.ChallengeAttempts(
        user_id=user_id,
        challenge_id=challenge_id,
        submitted_answer=submitted_answer,
        score=score,
        passed=passed,
        next_recommended_difficulty=next_difficulty,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # -- Update Skill DNA --
    skill_dna_service.bump_proficiency_from_challenge_score(
        db, user_id, challenge.skill_id, score
    )

    # -- Save Learning Progress --
    progress = models.LearningProgress(
        user_id=user_id,
        skill_id=challenge.skill_id,
        progress_percent=score,
        notes=f"Challenge '{challenge.title}' scored {score:.0f}% -> next: {next_difficulty}",
    )
    db.add(progress)
    db.commit()

    # -- Update Roadmap (unlock next step if this challenge was tied to one) --
    roadmap_step = (
        db.query(models.Roadmap)
        .filter(models.Roadmap.resource_type == "challenge", models.Roadmap.resource_id == challenge_id)
        .filter(models.Roadmap.user_id == user_id)
        .first()
    )
    if roadmap_step and passed:
        roadmap_service.advance_roadmap(db, user_id, roadmap_step.career_id, roadmap_step.id)

    # -- Recalculate Readiness --
    if roadmap_step:
        readiness_service.recalculate_readiness(db, user_id, roadmap_step.career_id)

    return attempt


def _grade_submission(challenge: models.Challenges, submitted_answer: str) -> float:
    """
    Simple rubric-based grading. `solution_criteria` may contain a list of
    required keywords/keys; score = % of criteria matched. Falls back to a
    neutral score if no rubric is defined (e.g. open-ended/manual review).
    """
    criteria = challenge.solution_criteria or {}
    keywords = criteria.get("keywords") if isinstance(criteria, dict) else None

    if not keywords:
        return 60.0  # neutral default pending manual/AI review

    answer_lower = submitted_answer.lower()
    matched = sum(1 for kw in keywords if kw.lower() in answer_lower)
    return round(100 * matched / len(keywords), 2)
