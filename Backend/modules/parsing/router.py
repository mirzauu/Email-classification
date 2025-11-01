"""Parsing router endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.dependencies import get_database_session
from modules.parsing.schemas import EmailCreate, EmailResponse, EmailUpdate
from modules.parsing.service import (
    create_email,
    get_all_emails,
    get_email_by_id,
    update_email_classification,
    classify_email
)

router = APIRouter(prefix="/parsing", tags=["parsing"])


@router.post("/", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def create_email_endpoint(
    email: EmailCreate,
    db: Session = Depends(get_database_session)
):
    """Create a new email record."""
    return create_email(db, email)


@router.get("/", response_model=List[EmailResponse])
async def get_emails(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database_session)
):
    """Get all emails."""
    return get_all_emails(db, skip=skip, limit=limit)


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: int,
    db: Session = Depends(get_database_session)
):
    """Get email by ID."""
    email = get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    return email


@router.put("/{email_id}/classify", response_model=EmailResponse)
async def classify_email_endpoint(
    email_id: int,
    db: Session = Depends(get_database_session)
):
    """Classify an email."""
    return classify_email(db, email_id)


@router.patch("/{email_id}", response_model=EmailResponse)
async def update_email(
    email_id: int,
    email_update: EmailUpdate,
    db: Session = Depends(get_database_session)
):
    """Update email classification."""
    return update_email_classification(db, email_id, email_update)

