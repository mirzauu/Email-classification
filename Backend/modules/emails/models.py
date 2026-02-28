"""Email module models."""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Double
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from core.database import Base

class EmailAccount(Base):
    __tablename__ = "email_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    provider = Column(String, nullable=False)
    email_address = Column(String, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime(timezone=True))
    scopes = Column(Text)
    last_synced_at = Column(DateTime(timezone=True))
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Email(Base):
    __tablename__ = "emails"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    body = Column(Text)
    classification = Column(String)
    user_id = Column(String, ForeignKey("user.id"))
    gmail_id = Column(String)
    thread_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed = Column(Boolean, default=False)
    classification_confidence = Column(Double)
    classification_reason = Column(Text)

    events = relationship("EmailEvent", back_populates="email")

class EmailEvent(Base):
    __tablename__ = "email_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False, unique=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    event_type = Column(String, nullable=False)
    provider_hint = Column(String)
    confidence = Column(Integer, nullable=False)
    extracted_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    email = relationship(Email, back_populates="events")
