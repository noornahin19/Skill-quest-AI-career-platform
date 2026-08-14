from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
    title: str
    career_id: Optional[str] = None
    description: str
    required_skills: Optional[list[str]] = None
    difficulty: str = "medium"


class ProjectCreate(ProjectBase):
    pass


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class ProjectSubmissionCreate(BaseModel):
    user_id: str
    project_id: str
    repo_url: Optional[str] = None


class ProjectSubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    project_id: str
    repo_url: Optional[str] = None
    file_path: Optional[str] = None
    status: str
    feedback: Optional[str] = None
    score: Optional[float] = None
    created_at: datetime


class ProjectReviewRequest(BaseModel):
    status: str  # reviewed/accepted/rejected
    feedback: Optional[str] = None
    score: Optional[float] = None
