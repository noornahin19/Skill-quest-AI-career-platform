from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.database import get_db
from services import interview_service

router = APIRouter(prefix="/api/interview", tags=["interview"])


class AnswerSubmission(BaseModel):
    question: str
    answer: str


@router.get("/questions")
def get_questions(career_id: str | None = None, db: Session = Depends(get_db)):
    return interview_service.get_interview_questions(db, career_id)


@router.post("/score")
def score_answer(payload: AnswerSubmission):
    return interview_service.score_answer(payload.question, payload.answer)
