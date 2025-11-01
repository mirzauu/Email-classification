"""User router endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.dependencies import get_database_session
from modules.users.schemas import UserProfile, UserUpdate
from modules.users.service import get_all_users, get_user_by_id, update_user, delete_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserProfile])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database_session)
):
    """Get all users."""
    return get_all_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserProfile)
async def get_user(user_id: int, db: Session = Depends(get_database_session)):
    """Get user by ID."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserProfile)
async def update_user_endpoint(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_database_session)
):
    """Update user information."""
    return update_user(db, user_id, user_update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_database_session)
):
    """Delete a user."""
    delete_user(db, user_id)
    return None
