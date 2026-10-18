import logging
from sqlalchemy.orm import Session
from app.models.models import Lead, Reply
from app.services.nemotron_service import nemotron_service

logger = logging.getLogger(__name__)

def analyze_lead_reply_service(lead_id: str, reply_body: str, db: Session) -> Reply:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise ValueError(f"Lead not found with id {lead_id}")

    # Call Nemotron Fast Model for classification & next-action recommendation
    ai_reply = nemotron_service.classify_reply(reply_body)

    reply = Reply(
        lead_id=lead.id,
        body=reply_body,
        classification=ai_reply.classification,
        intent=ai_reply.intent,
        sentiment=ai_reply.sentiment,
        urgency=ai_reply.urgency,
        meeting_requested=ai_reply.meeting_requested,
        confidence=ai_reply.confidence,
        detected_intent=ai_reply.detected_intent,
        recommended_action=ai_reply.recommended_action,
        reason=ai_reply.reason,
        summary=ai_reply.summary
    )
    db.add(reply)

    # Update lead status based on classification & safety rules
    if ai_reply.classification in ("UNSUBSCRIBE", "NOT_INTERESTED") or ai_reply.intent in ("unsubscribe", "not_interested") or ai_reply.recommended_action == "STOP_CONTACT":
        lead.status = "CLOSED"
        logger.info(f"Lead {lead_id} marked CLOSED due to opt-out classification '{ai_reply.classification}'")
    else:
        lead.status = "ACTION_REQUIRED"

    db.commit()
    db.refresh(reply)
    return reply
