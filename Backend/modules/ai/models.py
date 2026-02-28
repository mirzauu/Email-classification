"""AI specific models."""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text
from core.database import Base

class BackgroundTask(Base):
    __tablename__ = "background_tasks"
    
    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False)
    name = Column(String)
    user_id = Column(String, ForeignKey("user.id"))
    status = Column(String)
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))

class EmbeddingRecord(Base):
    __tablename__ = "embedding_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    source_type = Column(String, nullable=False)
    source_id = Column(UUID(as_uuid=True), nullable=False)
    pinecone_id = Column(String, nullable=False)
    text_snippet = Column(Text)
    extra_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
