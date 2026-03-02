"""Authentication service logic."""
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from core.security import verify_password, get_password_hash, create_access_token
from core.config import settings
from modules.auth.models import FastAPIUser
from modules.auth.schemas import UserCreate, UserLogin

logger = logging.getLogger(__name__)


def get_user_by_username(db: Session, username: str) -> FastAPIUser | None:
    """Get user by username."""
    return db.query(FastAPIUser).filter(FastAPIUser.username == username).first()


def get_user_by_email(db: Session, email: str) -> FastAPIUser | None:
    """Get user by email."""
    return db.query(FastAPIUser).filter(FastAPIUser.email == email).first()


def create_user(db: Session, user: UserCreate) -> FastAPIUser:
    """Create a new user."""
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = FastAPIUser(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> FastAPIUser | None:
    """Authenticate a user."""
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def login_user(db: Session, user_login: UserLogin) -> dict:
    """Login a user and return access token."""
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


def handle_google_login(db: Session, user_info: dict, tokens: dict) -> dict:
    """Handle Google Login - create or update User and Account, then return JWT."""
    from modules.auth.models import User, Account
    import uuid
    from datetime import datetime, timedelta

    email = user_info.get("email")
    name  = user_info.get("name")
    logger.info("=" * 60)
    logger.info("🔐 [AUTH] Google Login started")
    logger.info(f"   Email    : {email}")
    logger.info(f"   Name     : {name}")
    logger.info(f"   Picture  : {user_info.get('picture', 'N/A')}")
    logger.info("=" * 60)

    if not email:
        raise HTTPException(status_code=400, detail="No email provided by Google")

    # ── Step 1: Find or create User ──────────────────────────────────
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.info(f"[AUTH] 🆕 New user — creating record for {email}")
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            picture=user_info.get("picture"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"[AUTH] ✅ User created  | id={user.id}")
    else:
        logger.info(f"[AUTH] 🔄 Existing user | id={user.id}")

    # ── Step 2: Create or update OAuth Account ───────────────────────
    account = db.query(Account).filter(
        Account.provider_id == "google",
        Account.user_id == user.id
    ).first()

    if not account:
        logger.info("[AUTH] 🆕 Creating new OAuth account record")
        account = Account(
            id=str(uuid.uuid4()),
            account_id=user_info.get("id"),
            provider_id="google",
            user_id=user.id,
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            id_token=tokens.get("id_token"),
            scope=tokens.get("scope"),
        )
        if "expires_in" in tokens:
            account.access_token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
        db.add(account)
    else:
        logger.info("[AUTH] 🔄 Refreshing existing OAuth account tokens")
        account.access_token = tokens.get("access_token")
        if tokens.get("refresh_token"):
            account.refresh_token = tokens.get("refresh_token")
        account.id_token   = tokens.get("id_token")
        account.scope      = tokens.get("scope")
        if "expires_in" in tokens:
            account.access_token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])

    db.commit()
    logger.info("[AUTH] ✅ OAuth account saved to DB")

    # ── Step 3: Issue internal JWT ────────────────────────────────────
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    logger.info(f"[AUTH] 🎟️  JWT issued | expires_in={settings.ACCESS_TOKEN_EXPIRE_MINUTES}m")
    logger.info("=" * 60)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }
