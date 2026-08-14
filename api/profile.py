from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas.profile import ProfileCreate, ProfileOut, ProfileUpdate, LoginRequest, TokenResponse
from core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("/signup", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def signup(payload: ProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(models.UserProfile).filter(models.UserProfile.email == payload.email).first()
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    user = models.UserProfile(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        bio=payload.bio,
        avatar_url=payload.avatar_url,
        experience_level=payload.experience_level,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.UserProfile).filter(models.UserProfile.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=ProfileOut)
def get_me(current_user: models.UserProfile = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=ProfileOut)
def update_me(
    payload: ProfileUpdate,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=ProfileOut)
def get_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.UserProfile).filter(models.UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user
