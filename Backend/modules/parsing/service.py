import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from modules.emails.models import Email
from modules.parsing.schemas import EmailCreate, EmailUpdate, EmailClassificationBase, ClassificationBatchResponse
from modules.provider.service import ProviderService

logger = logging.getLogger(__name__)

CATEGORIES = [
    "finance", "travel", "work", "personal", "newsletters", "alerts", 
    "promotions", "social", "spam", "medical", "education", "other"
]

def load_prompt() -> str:
    return f"""You are an advanced email classification agent. Your task is to analyze the following email content and classify it accurately into one of the following predefined categories: {', '.join(CATEGORIES)}.

In addition to the primary category:
1. Provide a concise 1-2 sentence summary of the email.
2. Provide a confidence score between 0.0 and 1.0 representing your certainty in the classification.
3. Provide a list of 1-5 sub-labels or keywords that capture the nuance of the email (e.g., 'invoice', 'meeting', 'flight updates').

If the email does not clearly fit into any specific category, classify it as 'other'.
"""

class EmailParsingService:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        # Initialize the global ProviderService
        self.provider = ProviderService.create(db=self.db, user_id=self.user_id)

    def create_email(self, email_data: EmailCreate, user_id: int = None) -> Email:
        db_email = Email(**email_data.model_dump(), user_id=user_id)
        self.db.add(db_email)
        self.db.commit()
        self.db.refresh(db_email)
        return db_email

    def get_email_by_id(self, email_id: int) -> Optional[Email]:
        return self.db.query(Email).filter(Email.id == email_id).first()

    def get_all_emails(self, skip: int = 0, limit: int = 100) -> List[Email]:
        return self.db.query(Email).offset(skip).limit(limit).all()

    def update_email_classification(self, email_id: int, email_update: EmailUpdate) -> Email:
        email = self.get_email_by_id(email_id)
        if not email:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
        
        if email_update.classification is not None:
            email.classification = email_update.classification
        if email_update.summary is not None:
            email.summary = email_update.summary
        if email_update.labels is not None:
            email.labels = json.dumps(email_update.labels)
            
        self.db.commit()
        self.db.refresh(email)
        return email

    async def _classify_single_email(self, email: Email) -> Dict[str, Any]:
        """Calls the LLM provider to classify a single email."""
        logger.debug(f"[CLASSIFY] 🤖 email_id={email.id} | subject='{email.subject[:60]}'")
        content = f"Subject: {email.subject}\nSender: {email.sender}\nBody: {email.body or ''}"
        system_msg = {"role": "system", "content": load_prompt()}
        user_msg = {"role": "user", "content": content}

        try:
            result: EmailClassificationBase = await self.provider.call_llm_with_structured_output(
                messages=[system_msg, user_msg],
                output_schema=EmailClassificationBase,
                config_type="inference",
            )

            category = (result.category or "other").strip().lower()
            if category not in CATEGORIES:
                logger.warning(f"[CLASSIFY] Unknown category '{category}' → falling back to 'other'")
                category = "other"

            email.classification = category
            email.classification_confidence = float(result.confidence) if result.confidence is not None else 0.5
            email.summary = result.summary
            email.labels = json.dumps(result.labels) if result.labels else "[]"
            email.processed = True

            logger.info(
                f"[CLASSIFY] ✅ email_id={email.id} | "
                f"category={category} | "
                f"confidence={email.classification_confidence:.2f} | "
                f"summary='{(result.summary or '')[:80]}'"
            )
            return {
                "id": email.id,
                "status": "success",
                "category": category,
                "summary": result.summary,
                "confidence": result.confidence
            }
        except Exception as e:
            logger.error(f"[CLASSIFY] ❌ email_id={email.id} failed: {e}")
            email.classification = "other"
            email.classification_confidence = 0.0
            email.summary = "Failed to classify due to error."
            email.labels = "[]"
            return {
                "id": email.id,
                "status": "error",
                "error": str(e)
            }

    async def classify_emails_batch(self, email_ids: List[int]) -> ClassificationBatchResponse:
        """Classifies a batch of emails asynchronously."""
        logger.info(f"[CLASSIFY BATCH] 📋 Starting batch | total={len(email_ids)} emails")

        emails = self.db.query(Email).filter(Email.id.in_(email_ids)).all()
        if not emails:
            logger.warning("[CLASSIFY BATCH] ⚠️  No emails found for given IDs.")
            raise HTTPException(status_code=404, detail="No valid emails found for the provided IDs.")

        logger.info(f"[CLASSIFY BATCH] Found {len(emails)} emails in DB. Concurrency limit=5")
        sem = asyncio.Semaphore(5)

        async def process_one(email: Email):
            async with sem:
                return await self._classify_single_email(email)

        results = await asyncio.gather(*[process_one(e) for e in emails])

        self.db.commit()

        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count  = len(email_ids) - success_count
        logger.info(
            f"[CLASSIFY BATCH] ✅ Done | success={success_count}, failed={failed_count} | "
            f"total_requested={len(email_ids)}"
        )
        return ClassificationBatchResponse(
            total_requested=len(email_ids),
            successful_classifications=success_count,
            failed_classifications=failed_count,
            results=results
        )

# For backward compatibility with existing router signatures, wrapping logic
def get_parsing_service(db: Session, user_id: str = "system") -> EmailParsingService:
    return EmailParsingService(db, user_id)

def create_email(db: Session, email: EmailCreate, user_id: int = None) -> Email:
    svc = get_parsing_service(db)
    return svc.create_email(email, user_id)

def get_email_by_id(db: Session, email_id: int) -> Optional[Email]:
    return get_parsing_service(db).get_email_by_id(email_id)

def get_all_emails(db: Session, skip: int = 0, limit: int = 100):
    return get_parsing_service(db).get_all_emails(skip, limit)

def update_email_classification(db: Session, email_id: int, email_update: EmailUpdate) -> Email:
    return get_parsing_service(db).update_email_classification(email_id, email_update)

async def classify_email_batch(db: Session, email_ids: List[int]) -> ClassificationBatchResponse:
    svc = get_parsing_service(db)
    return await svc.classify_emails_batch(email_ids)
