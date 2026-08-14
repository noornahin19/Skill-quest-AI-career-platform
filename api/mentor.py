from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.database import get_db
from database import models
from services.ai_service import generate_ai_response
from core.security import get_current_user

router = APIRouter(prefix="/api/mentor", tags=["mentor"])


class ChatRequest(BaseModel):
    message: str


@router.get("/history")
def get_history(
    current_user: models.UserProfile = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(models.ChatMessages)
        .filter(models.ChatMessages.user_id == current_user.id)
        .order_by(models.ChatMessages.created_at)
        .all()
    )


@router.post("/chat")
def chat(
    payload: ChatRequest,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_msg = models.ChatMessages(user_id=current_user.id, role="user", content=payload.message)
    db.add(user_msg)
    db.commit()

    # Give the mentor a little context: name + current experience level
    prompt = (
        f"You are a friendly, encouraging career mentor. The student is "
        f"{current_user.full_name}, experience level: {current_user.experience_level}.\n"
        f"Student says: {payload.message}"
    )
    reply_text = generate_ai_response(prompt)

    assistant_msg = models.ChatMessages(user_id=current_user.id, role="assistant", content=reply_text)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg
