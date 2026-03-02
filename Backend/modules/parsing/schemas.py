from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class EmailBase(BaseModel):
    subject: str
    sender: str
    recipient: str
    body: Optional[str] = None

class EmailCreate(EmailBase):
    pass

class EmailUpdate(BaseModel):
    classification: Optional[str] = None
    summary: Optional[str] = None
    labels: Optional[List[str]] = None

class EmailResponse(EmailBase):
    id: int
    classification: Optional[str] = None
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EmailClassificationBase(BaseModel):
    category: str = Field(description="The primary category of the email (e.g., finance, travel, personal, work, newsletters, alerts, other).", examples=["finance", "travel"])
    summary: str = Field(description="A concise summary of the email's content (1-2 sentences).")
    confidence: float | None = Field(default=None, description="Confidence score from 0.0 to 1.0.")
    labels: List[str] = Field(default_factory=list, description="A list of helpful sub-labels or keywords for the email.")

class ClassificationBatchRequest(BaseModel):
    email_ids: List[int] = Field(..., description="List of email IDs to classify in a batch.")

class ClassificationBatchResponse(BaseModel):
    total_requested: int
    successful_classifications: int
    failed_classifications: int
    results: List[dict] # Contains email_id, category, summary, confidence, etc
