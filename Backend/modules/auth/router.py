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

from fastapi.responses import RedirectResponse
from core.config import settings
from modules.auth.google_oauth import get_google_auth_url, exchange_code_for_tokens, get_user_info
from modules.auth.service import handle_google_login

@router.get("/google/login")
async def google_login():
    """Redirect to Google Login consent screen."""
    url = get_google_auth_url(settings.GOOGLE_REDIRECT_URI)
    return RedirectResponse(url)

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_database_session)):
    """Handle Google Login callback, then redirect to frontend with JWT."""
    # 1. Exchange code for tokens
    tokens = await exchange_code_for_tokens(code, settings.GOOGLE_REDIRECT_URI)
    
    # 2. Extract access token and fetch user profile
    access_token = tokens.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received from Google.")
    
    user_info = await get_user_info(access_token)
    
    # 3. Create/update DB records & return internal JWT
    token_response = handle_google_login(db, user_info, tokens)
    
    # 4. Redirect to Frontend
    frontend_redirect_url = f"{settings.FRONTEND_URL}/login?token={token_response['access_token']}&email={token_response.get('email', '')}"
    return RedirectResponse(url=frontend_redirect_url)

