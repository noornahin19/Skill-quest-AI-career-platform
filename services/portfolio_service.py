import re
import uuid

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from database import models


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{base}-{uuid.uuid4().hex[:6]}"


def get_or_create_portfolio(db: Session, user_id: str) -> models.Portfolio:
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).first()
    if portfolio:
        return portfolio

    user = db.query(models.UserProfile).filter(models.UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    portfolio = models.Portfolio(
        user_id=user_id,
        headline=f"{user.full_name} — {user.experience_level.title()}",
        public_slug=_slugify(user.full_name),
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


def update_portfolio(
    db: Session,
    user_id: str,
    headline: str | None = None,
    summary: str | None = None,
    featured_projects: list[str] | None = None,
    featured_achievements: list[str] | None = None,
) -> models.Portfolio:
    portfolio = get_or_create_portfolio(db, user_id)

    if headline is not None:
        portfolio.headline = headline
    if summary is not None:
        portfolio.summary = summary
    if featured_projects is not None:
        portfolio.featured_projects = featured_projects
    if featured_achievements is not None:
        portfolio.featured_achievements = featured_achievements

    db.commit()
    db.refresh(portfolio)
    return portfolio


def get_public_portfolio(db: Session, slug: str) -> models.Portfolio:
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.public_slug == slug).first()
    if not portfolio:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Portfolio not found")
    return portfolio
