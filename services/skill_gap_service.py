"""
skill_gap_service.py
---------------------
Computes the gap between a user's current skills and what a target
career requires. Powers the roadmap generator and readiness score.
"""

from sqlalchemy.orm import Session

from database import models
from services.skill_dna_service import get_user_skill_map


def compute_skill_gap(db: Session, user_id: str, career_id: str) -> list[dict]:
    """
    Returns a list of gap entries:
        [{skill_id, skill_name, current, required, gap, weight}, ...]
    `gap` is max(0, required - current) — 0 means the requirement is met.
    """
    requirements = (
        db.query(models.CareerSkills, models.Skills)
        .join(models.Skills, models.CareerSkills.skill_id == models.Skills.id)
        .filter(models.CareerSkills.career_id == career_id)
        .all()
    )
    user_skills = get_user_skill_map(db, user_id)

    gaps = []
    for req, skill in requirements:
        current = user_skills[skill.id].proficiency if skill.id in user_skills else 0.0
        gaps.append(
            {
                "skill_id": skill.id,
                "skill_name": skill.name,
                "current": current,
                "required": req.required_proficiency,
                "gap": max(0.0, req.required_proficiency - current),
                "weight": req.weight,
            }
        )
    # Biggest gaps first — that's what the roadmap should tackle first
    return sorted(gaps, key=lambda g: g["gap"] * g["weight"], reverse=True)


def compute_match_percent(db: Session, user_id: str, career_id: str) -> float:
    """
    Weighted percentage of career requirements the user currently satisfies.
    100% only if every required skill is at/above its required proficiency.
    """
    gaps = compute_skill_gap(db, user_id, career_id)
    if not gaps:
        return 0.0

    total_weight = sum(g["weight"] for g in gaps)
    if total_weight == 0:
        return 0.0

    satisfied_weight = sum(
        g["weight"] * min(1.0, g["current"] / g["required"]) if g["required"] > 0 else g["weight"]
        for g in gaps
    )
    return round(100 * satisfied_weight / total_weight, 2)
