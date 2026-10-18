import logging
import uuid
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class BaseEmailProvider:
    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        raise NotImplementedError

class MockEmailProvider(BaseEmailProvider):
    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        message_id = f"mock_{uuid.uuid4().hex[:12]}"
        logger.info(f"[MOCK EMAIL PROVIDER] Sending email to '{to_email}' with subject '{subject}'. Message ID: {message_id}")
        return {
            "status": "SENT",
            "provider": "mock",
            "provider_message_id": message_id,
            "demo_mode": True,
            "message": "Demo/Mock email logged successfully. No real email was sent to external network."
        }

class ResendEmailProvider(BaseEmailProvider):
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.EMAIL_FROM

    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("RESEND_API_KEY not configured. Falling back to MockEmailProvider.")
            return MockEmailProvider().send_email(to_email, subject, body)

        try:
            import resend
            resend.api_key = self.api_key
            response = resend.Emails.send({
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "text": body
            })
            return {
                "status": "SENT",
                "provider": "resend",
                "provider_message_id": response.get("id", f"resend_{uuid.uuid4().hex[:8]}"),
                "demo_mode": False,
                "message": "Real email dispatched via Resend API."
            }
        except Exception as e:
            logger.error(f"Resend email sending failed: {str(e)}")
            raise e

def get_email_provider() -> BaseEmailProvider:
    provider_type = settings.EMAIL_PROVIDER.lower()
    if provider_type == "resend" and settings.RESEND_API_KEY:
        return ResendEmailProvider()
    return MockEmailProvider()

email_service = get_email_provider()
