"""User Pydantic schemas."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


class UserProfile(BaseModel):
    """Schema for user profile."""
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
