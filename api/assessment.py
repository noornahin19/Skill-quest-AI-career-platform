from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas.assessment import (
    AssessmentCreate, AssessmentOut, AssessmentSubmission, AssessmentResultOut,
)
from services import assessment_service
from core.security import get_current_user

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


@router.post("/", response_model=AssessmentOut, status_code=status.HTTP_201_CREATED)
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    return assessment_service.create_assessment(db, payload.title, payload.career_id, payload.questions)


@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    assessment = assessment_service.get_assessment(db, assessment_id)
    # Strip answer keys before returning to the client
    sanitized_questions = [
        {k: v for k, v in q.items() if k != "answer"} for q in assessment.questions
    ]
    assessment.questions = sanitized_questions
    return assessment


@router.post("/{assessment_id}/submit", response_model=AssessmentResultOut)
def submit_assessment(
    assessment_id: str,
    payload: AssessmentSubmission,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return assessment_service.grade_assessment(db, current_user.id, assessment_id, payload.answers)
