"""Authentication models."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class FastAPIUser(Base):
    """Legacy/FastAPI user model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    """NextAuth user model, acts as primary foreign key target for logic."""
    __tablename__ = "user"
    
    id = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String)
    picture = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    accounts = relationship("Account", back_populates="user")
    connections = relationship("Connection", back_populates="user")

class Account(Base):
    """OAuth account linking table."""
    __tablename__ = "account"
    id = Column(String, primary_key=True)
    account_id = Column(String, nullable=False)
    provider_id = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    id_token = Column(Text)
    access_token_expires_at = Column(DateTime)
    refresh_token_expires_at = Column(DateTime)
    scope = Column(Text)
    password = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="accounts")

class Connection(Base):
    """External API connections."""
    __tablename__ = "connection"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    email = Column(String, nullable=False)
    name = Column(String)
    picture = Column(String)
    access_token = Column(Text)
    refresh_token = Column(Text)
    scope = Column(Text, nullable=False)
    provider_id = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="connections")
