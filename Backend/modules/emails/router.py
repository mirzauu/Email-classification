"""Email router for account linking."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import get_database_session
from core.config import settings
from core.security import create_state_token, verify_state_token
from modules.auth.dependencies import get_current_user
from modules.auth.models import User
from modules.auth.google_oauth import get_google_auth_url, exchange_code_for_tokens, get_user_info
from modules.emails.models import EmailAccount

router = APIRouter(prefix="/emails", tags=["emails"])

@router.get("/google/link")
async def link_google_account(user: User = Depends(get_current_user)):
    """Redirect to Google to link a new Gmail account."""
    state_token = create_state_token(user.id)
    url = get_google_auth_url(settings.GOOGLE_LINK_REDIRECT_URI, state=state_token)
    return RedirectResponse(url)

from fastapi import BackgroundTasks

async def sync_gmail_background(user_id: str, access_token: str):
    from core.database import SessionLocal
    from modules.emails.gmail_service import GmailSyncService
    
    db = SessionLocal()
    try:
        service = GmailSyncService(db, user_id)
        await service.initial_sync(access_token, limit=50)
    finally:
        db.close()

@router.get("/google/link-callback")
async def link_google_callback(
    code: str, 
    state: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database_session)
):
    """Handle callback for linking a Gmail account."""
    user_id = verify_state_token(state)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired state token.")

    # 1. Exchange code for tokens
    tokens = await exchange_code_for_tokens(code, settings.GOOGLE_LINK_REDIRECT_URI)
    
    access_token = tokens.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received.")
        
    # 2. Get user info (email address) from Google
    user_info = await get_user_info(access_token)
    email_address = user_info.get("email")
    if not email_address:
        raise HTTPException(status_code=400, detail="No email address received from Google.")
    
    # 3. Create or update EmailAccount record
    email_account = db.query(EmailAccount).filter(
        EmailAccount.user_id == user_id,
        EmailAccount.email_address == email_address
    ).first()
    
    if not email_account:
        email_account = EmailAccount(
            id=uuid.uuid4(),
            user_id=user_id,
            provider="google",
            email_address=email_address,
            access_token=access_token,
            refresh_token=tokens.get("refresh_token"),
            scopes=tokens.get("scope")
        )
        if "expires_in" in tokens:
            from datetime import timedelta
            email_account.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
        db.add(email_account)
    else:
        email_account.access_token = access_token
        if tokens.get("refresh_token"):
            email_account.refresh_token = tokens.get("refresh_token")
        email_account.scopes = tokens.get("scope")
        if "expires_in" in tokens:
            from datetime import timedelta
            email_account.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
            
    db.commit()
    
    # 4. Trigger Background Sync task
    background_tasks.add_task(sync_gmail_background, user_id, access_token)
    
    # Redirect to a frontend success page
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings?account_linked=true&email={email_address}")
