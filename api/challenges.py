from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas.challenge import ChallengeCreate, ChallengeOut, ChallengeAttemptOut
from services import challenge_service, adaptive_learning_service
from core.security import get_current_user

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


@router.post("/", response_model=ChallengeOut, status_code=status.HTTP_201_CREATED)
def create_challenge(payload: ChallengeCreate, db: Session = Depends(get_db)):
    return challenge_service.create_challenge(db, payload)


@router.get("/", response_model=list[ChallengeOut])
def list_challenges(
    skill_id: str | None = None, difficulty: str | None = None, db: Session = Depends(get_db)
):
    return challenge_service.list_challenges(db, skill_id, difficulty)


@router.get("/{challenge_id}", response_model=ChallengeOut)
def get_challenge(challenge_id: str, db: Session = Depends(get_db)):
    return challenge_service.get_challenge(db, challenge_id)


@router.post("/{challenge_id}/submit", response_model=ChallengeAttemptOut)
def submit_challenge(
    challenge_id: str,
    submitted_answer: str,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Runs the full adaptive-learning pipeline: grade -> Skill DNA -> roadmap -> readiness."""
    return adaptive_learning_service.process_challenge_result(
        db, current_user.id, challenge_id, submitted_answer
    )


@router.get("/me/attempts", response_model=list[ChallengeAttemptOut])
def my_attempts(
    current_user: models.UserProfile = Depends(get_current_user), db: Session = Depends(get_db)
):
    return challenge_service.list_user_attempts(db, current_user.id)
