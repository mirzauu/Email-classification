from sqlalchemy import Column, String, JSON, ForeignKey
from core.database import Base

class UserPreferences(Base):
    """User preferences for AI models and other settings."""
    __tablename__ = "user_preferences"
    
    user_id = Column(String, ForeignKey("user.id"), primary_key=True)
    preferences = Column(JSON, default={})
