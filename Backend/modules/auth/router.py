"""Authentication router endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
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

from fastapi import BackgroundTasks

async def sync_gmail_background(user_id: str, access_token: str):
    from core.database import SessionLocal
    from modules.emails.gmail_service import GmailSyncService
    logger.info(f"[BACKGROUND] 🚀 Starting Gmail sync task for user_id={user_id}")
    db = SessionLocal()
    try:
        service = GmailSyncService(db, user_id)
        await service.initial_sync(access_token, limit=50)
        logger.info(f"[BACKGROUND] ✅ Gmail sync task complete for user_id={user_id}")
    except Exception as e:
        logger.error(f"[BACKGROUND] ❌ Gmail sync task failed for user_id={user_id}: {e}")
    finally:
        db.close()

@router.get("/google/callback")
async def google_callback(
    code: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database_session)
):
    """Handle Google Login callback, then redirect to frontend with JWT."""
    logger.info("[ROUTER] ── Google callback received ──────────────────────")

    # 1. Exchange code for tokens
    logger.info("[ROUTER] Step 1/4: Exchanging auth code for tokens...")
    tokens = await exchange_code_for_tokens(code, settings.GOOGLE_REDIRECT_URI)
    access_token = tokens.get("access_token")
    if not access_token:
        logger.error("[ROUTER] ❌ No access_token in token response")
        raise HTTPException(status_code=400, detail="No access token received from Google.")
    logger.info(f"[ROUTER] ✅ Tokens received | scopes={tokens.get('scope', 'N/A')[:80]}")

    # 2. Fetch Google user profile
    logger.info("[ROUTER] Step 2/4: Fetching Google user profile...")
    user_info = await get_user_info(access_token)
    logger.info(f"[ROUTER] ✅ User profile received | email={user_info.get('email')} | name={user_info.get('name')}")

    # 3. Create/update DB records & issue internal JWT
    logger.info("[ROUTER] Step 3/4: Calling handle_google_login (DB upsert + JWT)...")
    token_response = handle_google_login(db, user_info, tokens)
    logger.info(f"[ROUTER] ✅ JWT issued for user_id={token_response.get('user_id')}")

    # 4. Enqueue background Gmail sync
    user_id = token_response.get("user_id")
    if user_id and access_token:
        logger.info(f"[ROUTER] Step 4/4: Enqueuing Gmail background sync for user_id={user_id}")
        background_tasks.add_task(sync_gmail_background, user_id, access_token)

    frontend_redirect_url = (
        f"{settings.FRONTEND_URL}/login"
        f"?token={token_response['access_token']}"
        f"&email={token_response.get('email', '')}"
    )
    logger.info(f"[ROUTER] ↩️  Redirecting to frontend: {frontend_redirect_url[:80]}")
    logger.info("[ROUTER] ────────────────────────────────────────────────────")
    return RedirectResponse(url=frontend_redirect_url)


