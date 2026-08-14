from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SkillBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillOut(SkillBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class UserSkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_id: str
    proficiency: float
    verified: bool
    last_practiced: Optional[datetime] = None
    updated_at: datetime


class UserSkillUpsert(BaseModel):
    skill_id: str
    proficiency: float  # 0-100
    verified: Optional[bool] = False


class SkillDNAResponse(BaseModel):
    """Aggregated skill-proficiency vector for a user, keyed by category."""
    user_id: str
    dna: dict[str, float]  # category -> average proficiency
    top_skills: list[UserSkillOut]
