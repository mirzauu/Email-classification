"""Parsing service logic."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from modules.parsing.models import Email
from modules.parsing.schemas import EmailCreate, EmailUpdate


def create_email(db: Session, email: EmailCreate, user_id: int = None) -> Email:
    """Create a new email record."""
    db_email = Email(**email.dict(), user_id=user_id)
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email


def get_email_by_id(db: Session, email_id: int) -> Email | None:
    """Get email by ID."""
    return db.query(Email).filter(Email.id == email_id).first()


def get_all_emails(db: Session, skip: int = 0, limit: int = 100):
    """Get all emails with pagination."""
    return db.query(Email).offset(skip).limit(limit).all()


def update_email_classification(
    db: Session,
    email_id: int,
    email_update: EmailUpdate
) -> Email:
    """Update email classification."""
    email = get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    if email_update.classification:
        email.classification = email_update.classification
    
    db.commit()
    db.refresh(email)
    return email


def classify_email(db: Session, email_id: int) -> Email:
    """Classify an email (placeholder for classification logic)."""
    email = get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # TODO: Implement actual classification logic
    # This is a placeholder
    email.classification = "unclassified"
    
    db.commit()
    db.refresh(email)
    return email
