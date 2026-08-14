from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class RoadmapStepBase(BaseModel):
    step_order: int
    title: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    status: str = "locked"


class RoadmapStepOut(RoadmapStepBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    career_id: str
    created_at: datetime
    updated_at: datetime


class RoadmapGenerateRequest(BaseModel):
    user_id: str
    career_id: str


class RoadmapStepStatusUpdate(BaseModel):
    status: str  # locked/available/in_progress/completed


class LearningProgressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    skill_id: Optional[str] = None
    roadmap_step_id: Optional[str] = None
    progress_percent: float
    notes: Optional[str] = None
    updated_at: datetime
