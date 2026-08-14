from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class AssessmentBase(BaseModel):
    title: str
    career_id: Optional[str] = None
    questions: list[dict[str, Any]]  # [{question, options, answer, skill_id}]


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentOut(BaseModel):
    """Public-facing version — never leak the `answer` key to the client."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    career_id: Optional[str] = None
    questions: list[dict[str, Any]]


class AssessmentSubmission(BaseModel):
    user_id: str
    assessment_id: str
    answers: dict[str, str]  # question_index (as str) -> chosen answer


class AssessmentResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    assessment_id: str
    score: float
    result_summary: Optional[dict[str, Any]] = None
    created_at: datetime
