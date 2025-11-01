"""Parsing Pydantic schemas."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class EmailBase(BaseModel):
    """Base email schema."""
    subject: str
    sender: str
    recipient: str
    body: Optional[str] = None


class EmailCreate(EmailBase):
    """Schema for creating an email."""
    pass


class EmailUpdate(BaseModel):
    """Schema for updating email classification."""
    classification: Optional[str] = None


class EmailResponse(EmailBase):
    """Schema for email response."""
    id: int
    classification: Optional[str] = None
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
