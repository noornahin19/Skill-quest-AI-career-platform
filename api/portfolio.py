from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.database import get_db
from database import models
from services import portfolio_service
from core.security import get_current_user

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


class PortfolioUpdateRequest(BaseModel):
    headline: str | None = None
    summary: str | None = None
    featured_projects: list[str] | None = None
    featured_achievements: list[str] | None = None


@router.get("/me")
def get_my_portfolio(
    current_user: models.UserProfile = Depends(get_current_user), db: Session = Depends(get_db)
):
    return portfolio_service.get_or_create_portfolio(db, current_user.id)


@router.patch("/me")
def update_my_portfolio(
    payload: PortfolioUpdateRequest,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return portfolio_service.update_portfolio(db, current_user.id, **payload.model_dump())


@router.get("/public/{slug}")
def get_public_portfolio(slug: str, db: Session = Depends(get_db)):
    return portfolio_service.get_public_portfolio(db, slug)
