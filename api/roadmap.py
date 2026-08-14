from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas.roadmap import RoadmapStepOut, RoadmapStepStatusUpdate
from services import roadmap_service, readiness_service
from core.security import get_current_user

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


@router.post("/{career_id}/generate", response_model=list[RoadmapStepOut])
def generate_roadmap(
    career_id: str,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    steps = roadmap_service.generate_roadmap(db, current_user.id, career_id)
    readiness_service.recalculate_readiness(db, current_user.id, career_id)
    return steps


@router.get("/{career_id}", response_model=list[RoadmapStepOut])
def get_roadmap(
    career_id: str,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Roadmap)
        .filter(models.Roadmap.user_id == current_user.id, models.Roadmap.career_id == career_id)
        .order_by(models.Roadmap.step_order)
        .all()
    )


@router.patch("/step/{step_id}", response_model=RoadmapStepOut)
def update_step_status(
    step_id: str,
    payload: RoadmapStepStatusUpdate,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    step = db.query(models.Roadmap).filter(models.Roadmap.id == step_id).first()
    step.status = payload.status
    db.commit()
    db.refresh(step)

    if payload.status == "completed":
        roadmap_service.advance_roadmap(db, current_user.id, step.career_id, step.id)
        readiness_service.recalculate_readiness(db, current_user.id, step.career_id)

    return step
