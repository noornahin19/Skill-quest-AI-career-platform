from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class ProfileBase(BaseModel):
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    experience_level: Optional[str] = "beginner"


class ProfileCreate(ProfileBase):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    experience_level: Optional[str] = None
    target_career_id: Optional[str] = None


class ProfileOut(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    target_career_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
