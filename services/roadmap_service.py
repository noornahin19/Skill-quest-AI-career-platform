"""
roadmap_service.py
--------------------
Turns a skill gap analysis into an ordered, actionable roadmap:
biggest/most-weighted gaps first, each resolved via the best matching
challenge or project. First step is unlocked; the rest start "locked"
and unlock sequentially as prior steps complete.
"""

from sqlalchemy.orm import Session

from database import models
from services.skill_gap_service import compute_skill_gap


def generate_roadmap(db: Session, user_id: str, career_id: str) -> list[models.Roadmap]:
    # Wipe any previous roadmap for this user/career so regeneration is idempotent
    db.query(models.Roadmap).filter(
        models.Roadmap.user_id == user_id, models.Roadmap.career_id == career_id
    ).delete()

    gaps = [g for g in compute_skill_gap(db, user_id, career_id) if g["gap"] > 0]

    steps: list[models.Roadmap] = []
    for i, gap in enumerate(gaps):
        # Prefer a "prerequisite" challenge for large gaps, else "practice"
        difficulty = "prerequisite" if gap["gap"] > 50 else "practice"
        challenge = (
            db.query(models.Challenges)
            .filter(
                models.Challenges.skill_id == gap["skill_id"],
                models.Challenges.difficulty == difficulty,
            )
            .first()
        )

        step = models.Roadmap(
            user_id=user_id,
            career_id=career_id,
            step_order=i + 1,
            title=f"Level up: {gap['skill_name']}",
            description=(
                f"Close a {gap['gap']:.0f}-point gap in {gap['skill_name']} "
                f"(currently {gap['current']:.0f}/{gap['required']:.0f})."
            ),
            resource_type="challenge" if challenge else None,
            resource_id=challenge.id if challenge else None,
            status="available" if i == 0 else "locked",
        )
        db.add(step)
        steps.append(step)

    db.commit()
    for step in steps:
        db.refresh(step)
    return steps


def advance_roadmap(db: Session, user_id: str, career_id: str, completed_step_id: str) -> None:
    """Marks a step completed and unlocks the next one in sequence."""
    step = db.query(models.Roadmap).filter(models.Roadmap.id == completed_step_id).first()
    if not step:
        return
    step.status = "completed"

    next_step = (
        db.query(models.Roadmap)
        .filter(
            models.Roadmap.user_id == user_id,
            models.Roadmap.career_id == career_id,
            models.Roadmap.step_order == step.step_order + 1,
        )
        .first()
    )
    if next_step and next_step.status == "locked":
        next_step.status = "available"

    db.commit()
