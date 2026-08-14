"""
skill_dna_service.py
---------------------
Computes a user's "Skill DNA": an aggregated proficiency vector across
skill categories, derived from UserSkills rows. Used by career matching,
readiness scoring, and the profile dashboard.
"""

from collections import defaultdict
from sqlalchemy.orm import Session

from database import models


def get_user_skill_map(db: Session, user_id: str) -> dict[str, models.UserSkills]:
    """Returns {skill_id: UserSkills row} for quick lookups."""
    rows = db.query(models.UserSkills).filter(models.UserSkills.user_id == user_id).all()
    return {row.skill_id: row for row in rows}


def compute_skill_dna(db: Session, user_id: str) -> dict[str, float]:
    """
    Aggregates proficiency by skill category, e.g.:
        {"backend": 62.5, "frontend": 40.0, "soft-skill": 80.0}
    """
    rows = (
        db.query(models.UserSkills, models.Skills)
        .join(models.Skills, models.UserSkills.skill_id == models.Skills.id)
        .filter(models.UserSkills.user_id == user_id)
        .all()
    )

    category_totals: dict[str, float] = defaultdict(float)
    category_counts: dict[str, int] = defaultdict(int)

    for user_skill, skill in rows:
        category_totals[skill.category] += user_skill.proficiency
        category_counts[skill.category] += 1

    return {
        category: round(category_totals[category] / category_counts[category], 2)
        for category in category_totals
    }


def upsert_user_skill(
    db: Session, user_id: str, skill_id: str, proficiency: float, verified: bool = False
) -> models.UserSkills:
    """Creates or updates a user's proficiency for a given skill (clamped 0-100)."""
    proficiency = max(0.0, min(100.0, proficiency))

    row = (
        db.query(models.UserSkills)
        .filter(models.UserSkills.user_id == user_id, models.UserSkills.skill_id == skill_id)
        .first()
    )
    if row:
        row.proficiency = proficiency
        row.verified = verified or row.verified
    else:
        row = models.UserSkills(
            user_id=user_id, skill_id=skill_id, proficiency=proficiency, verified=verified
        )
        db.add(row)

    db.commit()
    db.refresh(row)
    return row


def bump_proficiency_from_challenge_score(
    db: Session, user_id: str, skill_id: str, challenge_score: float
) -> models.UserSkills:
    """
    Nudges proficiency toward a challenge result using a simple exponential
    moving average, so a single bad/good attempt doesn't swing the score wildly.
    """
    ALPHA = 0.35  # weight given to the new observation
    row = (
        db.query(models.UserSkills)
        .filter(models.UserSkills.user_id == user_id, models.UserSkills.skill_id == skill_id)
        .first()
    )
    current = row.proficiency if row else 0.0
    new_value = round((1 - ALPHA) * current + ALPHA * challenge_score, 2)
    return upsert_user_skill(db, user_id, skill_id, new_value, verified=challenge_score >= 75)
