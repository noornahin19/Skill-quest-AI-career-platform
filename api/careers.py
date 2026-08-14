from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas.career import CareerCreate, CareerOut, CareerMatch
from services import career_service, recommendation_service, skill_gap_service
from core.security import get_current_user

router = APIRouter(prefix="/api/careers", tags=["careers"])


@router.post("/", response_model=CareerOut, status_code=status.HTTP_201_CREATED)
def create_career(payload: CareerCreate, db: Session = Depends(get_db)):
    return career_service.create_career(db, payload)


@router.get("/", response_model=list[CareerOut])
def list_careers(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return career_service.list_careers(db, skip, limit)


@router.get("/recommendations", response_model=list[CareerMatch])
def get_recommendations(
    top_n: int = 5,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return recommendation_service.recommend_careers(db, current_user.id, top_n)


@router.get("/{career_id}", response_model=CareerOut)
def get_career(career_id: str, db: Session = Depends(get_db)):
    return career_service.get_career(db, career_id)


@router.get("/{career_id}/skill-gap")
def get_skill_gap(
    career_id: str,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return skill_gap_service.compute_skill_gap(db, current_user.id, career_id)
