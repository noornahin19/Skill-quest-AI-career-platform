from typing import Optional
from pydantic import BaseModel, ConfigDict


class CareerBase(BaseModel):
    title: str
    description: Optional[str] = None
    average_salary: Optional[float] = None
    growth_outlook: Optional[str] = None


class CareerCreate(CareerBase):
    pass


class CareerOut(CareerBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class CareerSkillRequirement(BaseModel):
    skill_id: str
    skill_name: Optional[str] = None
    required_proficiency: float
    weight: float


class CareerMatch(BaseModel):
    """Career recommendation with a match score against the user's Skill DNA."""
    career: CareerOut
    match_percent: float
    missing_skills: list[str]
