from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from database import models
from schemas.career import CareerCreate


def create_career(db: Session, payload: CareerCreate) -> models.Careers:
    career = models.Careers(**payload.model_dump())
    db.add(career)
    db.commit()
    db.refresh(career)
    return career


def get_career(db: Session, career_id: str) -> models.Careers:
    career = db.query(models.Careers).filter(models.Careers.id == career_id).first()
    if not career:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Career not found")
    return career


def list_careers(db: Session, skip: int = 0, limit: int = 50) -> list[models.Careers]:
    return db.query(models.Careers).offset(skip).limit(limit).all()


def get_career_requirements(db: Session, career_id: str) -> list[models.CareerSkills]:
    return db.query(models.CareerSkills).filter(models.CareerSkills.career_id == career_id).all()
