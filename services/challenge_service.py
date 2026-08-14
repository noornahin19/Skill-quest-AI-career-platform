from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from database import models
from schemas.challenge import ChallengeCreate


def create_challenge(db: Session, payload: ChallengeCreate) -> models.Challenges:
    challenge = models.Challenges(**payload.model_dump())
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


def get_challenge(db: Session, challenge_id: str) -> models.Challenges:
    challenge = db.query(models.Challenges).filter(models.Challenges.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Challenge not found")
    return challenge


def list_challenges(
    db: Session, skill_id: str | None = None, difficulty: str | None = None
) -> list[models.Challenges]:
    query = db.query(models.Challenges)
    if skill_id:
        query = query.filter(models.Challenges.skill_id == skill_id)
    if difficulty:
        query = query.filter(models.Challenges.difficulty == difficulty)
    return query.all()


def list_user_attempts(db: Session, user_id: str) -> list[models.ChallengeAttempts]:
    return (
        db.query(models.ChallengeAttempts)
        .filter(models.ChallengeAttempts.user_id == user_id)
        .order_by(models.ChallengeAttempts.created_at.desc())
        .all()
    )
