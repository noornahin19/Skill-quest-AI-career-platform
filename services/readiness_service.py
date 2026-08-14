"""
readiness_service.py
----------------------
Rolls up skill-gap match percentage plus roadmap completion into a
single "career readiness" score, persisted on CareerReadiness.
"""

from sqlalchemy.orm import Session

from database import models
from services.skill_gap_service import compute_match_percent, compute_skill_gap

# How much weight skill match vs roadmap completion carries in the final score
SKILL_WEIGHT = 0.7
ROADMAP_WEIGHT = 0.3


def _roadmap_completion_percent(db: Session, user_id: str, career_id: str) -> float:
    steps = (
        db.query(models.Roadmap)
        .filter(models.Roadmap.user_id == user_id, models.Roadmap.career_id == career_id)
        .all()
    )
    if not steps:
        return 0.0
    completed = sum(1 for s in steps if s.status == "completed")
    return round(100 * completed / len(steps), 2)


def recalculate_readiness(db: Session, user_id: str, career_id: str) -> models.CareerReadiness:
    skill_match = compute_match_percent(db, user_id, career_id)
    roadmap_completion = _roadmap_completion_percent(db, user_id, career_id)
    overall = round(SKILL_WEIGHT * skill_match + ROADMAP_WEIGHT * roadmap_completion, 2)

    gaps = compute_skill_gap(db, user_id, career_id)

    row = (
        db.query(models.CareerReadiness)
        .filter(models.CareerReadiness.user_id == user_id, models.CareerReadiness.career_id == career_id)
        .first()
    )
    if row:
        row.readiness_percent = overall
        row.skill_gap_summary = gaps
    else:
        row = models.CareerReadiness(
            user_id=user_id, career_id=career_id, readiness_percent=overall, skill_gap_summary=gaps
        )
        db.add(row)

    db.commit()
    db.refresh(row)
    return row
