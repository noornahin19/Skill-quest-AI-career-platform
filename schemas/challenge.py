from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ChallengeBase(BaseModel):
    title: str
    skill_id: str
    difficulty: str = "practice"  # prerequisite/practice/advanced
    prompt: str
    max_score: float = 100.0


class ChallengeCreate(ChallengeBase):
    solution_criteria: Optional[dict[str, Any]] = None


class ChallengeOut(ChallengeBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class ChallengeSubmission(BaseModel):
    user_id: str
    challenge_id: str
    submitted_answer: str


class ChallengeAttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    challenge_id: str
    score: float
    passed: bool
    next_recommended_difficulty: Optional[str] = None
    created_at: datetime
