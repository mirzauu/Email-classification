"""Authentication service logic."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from core.security import verify_password, get_password_hash, create_access_token
from core.config import settings
from modules.auth.models import FastAPIUser
from modules.auth.schemas import UserCreate, UserLogin


def get_user_by_username(db: Session, username: str) -> FastAPIUser | None:
    """Get user by username."""
    return db.query(FastAPIUser).filter(FastAPIUser.username == username).first()


def get_user_by_email(db: Session, email: str) -> FastAPIUser | None:
    """Get user by email."""
    return db.query(FastAPIUser).filter(FastAPIUser.email == email).first()


def create_user(db: Session, user: UserCreate) -> FastAPIUser:
    """Create a new user."""
    # Check if user exists
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = FastAPIUser(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> FastAPIUser | None:
    """Authenticate a user."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
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
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def handle_google_login(db: Session, user_info: dict, tokens: dict) -> dict:
    """Handle Google Login - create or update User and Account, then return JWT."""
    from modules.auth.models import User, Account
    import uuid
    from datetime import datetime, timedelta

    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="No email provided by Google")
    
    # Find existing user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=user_info.get("name"),
            picture=user_info.get("picture"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create or update Account
    account = db.query(Account).filter(
        Account.provider_id == "google",
        Account.user_id == user.id
    ).first()
    
    if not account:
        account = Account(
            id=str(uuid.uuid4()),
            account_id=user_info.get("id"),
            provider_id="google",
            user_id=user.id,
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            id_token=tokens.get("id_token"),
            scope=tokens.get("scope")
        )
        if "expires_in" in tokens:
            account.access_token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
        db.add(account)
    else:
        # Update existing account tokens
        account.access_token = tokens.get("access_token")
        if tokens.get("refresh_token"):
            account.refresh_token = tokens.get("refresh_token")
        account.id_token = tokens.get("id_token")
        account.scope = tokens.get("scope")
        if "expires_in" in tokens:
            account.access_token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
    
    db.commit()

    # Create internal access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Using user.id as the sub claim for internal JWT
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }

