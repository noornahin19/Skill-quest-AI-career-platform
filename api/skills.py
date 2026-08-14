from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas.skill import SkillCreate, SkillOut, UserSkillOut, UserSkillUpsert, SkillDNAResponse
from services import skill_dna_service
from core.security import get_current_user

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.post("/", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
def create_skill(payload: SkillCreate, db: Session = Depends(get_db)):
    skill = models.Skills(**payload.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("/", response_model=list[SkillOut])
def list_skills(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Skills)
    if category:
        query = query.filter(models.Skills.category == category)
    return query.all()


@router.get("/me", response_model=list[UserSkillOut])
def get_my_skills(
    current_user: models.UserProfile = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(models.UserSkills).filter(models.UserSkills.user_id == current_user.id).all()
    )


@router.put("/me", response_model=UserSkillOut)
def upsert_my_skill(
    payload: UserSkillUpsert,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return skill_dna_service.upsert_user_skill(
        db, current_user.id, payload.skill_id, payload.proficiency, payload.verified
    )


@router.get("/me/dna", response_model=SkillDNAResponse)
def get_my_skill_dna(
    current_user: models.UserProfile = Depends(get_current_user), db: Session = Depends(get_db)
):
    dna = skill_dna_service.compute_skill_dna(db, current_user.id)
    top_skills = (
        db.query(models.UserSkills)
        .filter(models.UserSkills.user_id == current_user.id)
        .order_by(models.UserSkills.proficiency.desc())
        .limit(5)
        .all()
    )
    return SkillDNAResponse(user_id=current_user.id, dna=dna, top_skills=top_skills)
