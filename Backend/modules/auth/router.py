"""Authentication router endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import get_database_session
from modules.auth.schemas import UserCreate, UserResponse, UserLogin, Token
from modules.auth.service import create_user, login_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_database_session)):
    """Register a new user."""
    return create_user(db, user)


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_database_session)):
    """Login and get access token."""
    return login_user(db, user_login)


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """Get current authenticated user."""
    # TODO: Implement authentication dependency
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented yet"
    )
