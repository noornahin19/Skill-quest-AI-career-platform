"""
recommendation_service.py
---------------------------
Ranks all careers by how well a user's current Skill DNA matches them,
using skill_gap_service's weighted match score.
"""

from sqlalchemy.orm import Session

from database import models
from services.skill_gap_service import compute_skill_gap, compute_match_percent


def recommend_careers(db: Session, user_id: str, top_n: int = 5) -> list[dict]:
    careers = db.query(models.Careers).all()
    results = []

    for career in careers:
        match_percent = compute_match_percent(db, user_id, career.id)
        gaps = compute_skill_gap(db, user_id, career.id)
        missing = [g["skill_name"] for g in gaps if g["gap"] > 0]
        results.append(
            {
                "career": career,
                "match_percent": match_percent,
                "missing_skills": missing,
            }
        )

    results.sort(key=lambda r: r["match_percent"], reverse=True)
    return results[:top_n]
