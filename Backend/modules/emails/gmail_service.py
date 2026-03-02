import asyncio
import logging
import httpx
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from modules.emails.models import Email
from modules.parsing.service import get_parsing_service

logger = logging.getLogger(__name__)


class GmailSyncService:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    async def initial_sync(self, access_token: str, limit: int = 50):
        """Check if user has emails; if not, fetch, store, then batch classify."""
        logger.info("=" * 60)
        logger.info(f"📬 [GMAIL SYNC] Starting initial sync for user_id={self.user_id}")

        existing_count = self.db.query(Email).filter(Email.user_id == self.user_id).count()
        logger.info(f"[GMAIL SYNC] Existing emails in DB: {existing_count}")

        if existing_count > 0:
            logger.info("[GMAIL SYNC] ⏩ User already has emails — skipping initial sync.")
            logger.info("=" * 60)
            return

        logger.info(f"[GMAIL SYNC] 📥 Fetching up to {limit} emails from Gmail API...")
        fetched = await self._fetch_emails(access_token, limit)
        logger.info(f"[GMAIL SYNC] ✅ Fetched {len(fetched)} emails from Gmail")

        if not fetched:
            logger.info("[GMAIL SYNC] ⚠️  No emails found in Gmail inbox.")
            logger.info("=" * 60)
            return

        # ── Save raw emails to DB ────────────────────────────────────
        new_ids = []
        for em in fetched:
            db_email = Email(
                user_id=self.user_id,
                gmail_id=em.get("id"),
                thread_id=em.get("threadId"),
                subject=em.get("subject", "No Subject")[:250],
                sender=em.get("sender", "Unknown")[:250],
                recipient=em.get("recipient", "Unknown")[:250],
                body=em.get("body", ""),
            )
            self.db.add(db_email)
            self.db.flush()
            new_ids.append(db_email.id)

        self.db.commit()
        logger.info(f"[GMAIL SYNC] 💾 Saved {len(new_ids)} emails to DB | IDs: {new_ids[:5]}{'...' if len(new_ids) > 5 else ''}")

        # ── Batch Classify ───────────────────────────────────────────
        logger.info(f"[GMAIL SYNC] 🤖 Handing off {len(new_ids)} emails to classification service...")
        parsing_svc = get_parsing_service(self.db, self.user_id)
        result = await parsing_svc.classify_emails_batch(new_ids)
        logger.info(
            f"[GMAIL SYNC] ✅ Classification done | "
            f"success={result.successful_classifications}, "
            f"failed={result.failed_classifications}"
        )
        logger.info("=" * 60)

    async def _fetch_emails(self, access_token: str, limit: int) -> List[Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {access_token}"}
        base_url = "https://gmail.googleapis.com/gmail/v1/users/me"

        async with httpx.AsyncClient(timeout=30) as client:
            logger.info("[GMAIL SYNC] → Calling Gmail list API...")
            list_res = await client.get(
                f"{base_url}/messages",
                headers=headers,
                params={"maxResults": limit, "labelIds": "INBOX"}
            )
            logger.info(f"[GMAIL SYNC] ← Gmail list response: HTTP {list_res.status_code}")
            if list_res.status_code != 200:
                logger.error(f"[GMAIL SYNC] ❌ Failed to list messages: {list_res.text[:300]}")
                return []

            messages = list_res.json().get("messages", [])
            logger.info(f"[GMAIL SYNC] Found {len(messages)} message IDs in inbox")
            if not messages:
                return []

            sem = asyncio.Semaphore(10)

            async def wrapped(msg_id: str):
                async with sem:
                    return await self._fetch_single_email(client, base_url, headers, msg_id)

            results = await asyncio.gather(
                *(wrapped(m["id"]) for m in messages),
                return_exceptions=True
            )

            good = [r for r in results if r and not isinstance(r, Exception)]
            bad  = [r for r in results if isinstance(r, Exception)]
            if bad:
                logger.warning(f"[GMAIL SYNC] ⚠️  {len(bad)} emails failed to fetch individually")
            return good

    async def _fetch_single_email(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        headers: dict,
        msg_id: str
    ) -> Dict[str, Any] | None:
        res = await client.get(f"{base_url}/messages/{msg_id}", headers=headers, params={"format": "full"})
        if res.status_code != 200:
            logger.debug(f"[GMAIL SYNC] Could not fetch message {msg_id}: HTTP {res.status_code}")
            return None

        data = res.json()
        payload = data.get("payload", {})
        hdrs = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}

        subject   = hdrs.get("subject", "")[:250]
        sender    = hdrs.get("from", "")[:250]
        recipient = hdrs.get("to", "")[:250]
        body      = self._extract_body(payload)

        logger.debug(f"[GMAIL SYNC] Fetched msg {msg_id} | subject='{subject[:50]}'")
        return {
            "id": data.get("id"),
            "threadId": data.get("threadId"),
            "subject": subject,
            "sender": sender,
            "recipient": recipient,
            "body": body,
        }

    def _extract_body(self, payload: dict) -> str:
        import base64
        body_data = payload.get("body", {}).get("data", "")
        if body_data:
            return base64.urlsafe_b64decode(
                body_data + "=" * (4 - len(body_data) % 4)
            ).decode("utf-8", errors="ignore")

        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    return self._extract_body(part)
            if payload["parts"]:
                return self._extract_body(payload["parts"][0])
        return ""
