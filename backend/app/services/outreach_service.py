import logging
import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.models.models import Lead, OutreachDraft, LeadQualification, ResearchReport, EmailEvent
from app.services.qualification_service import qualify_lead_service
from app.services.nemotron_service import nemotron_service, LeadIntelligenceAI, QualificationAI
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

def generate_outreach_draft_service(lead_id: str, db: Session) -> OutreachDraft:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise ValueError(f"Lead not found with id {lead_id}")

    # Ensure research & qualification exist
    if not lead.qualification:
        qualify_lead_service(lead_id, db)
        db.refresh(lead)

    report = lead.research_report
    qual = lead.qualification

    intelligence = LeadIntelligenceAI(
        company_name=lead.company_name,
        industry=lead.industry or "B2B Technology",
        company_size=report.company.company_size if report and report.company and report.company.company_size else "UNKNOWN",
        summary=report.summary if report else "",
        recent_signals=report.recent_signals if report else [],
        pain_points=report.pain_points if report else [],
        opportunities=report.opportunities if report else [],
        confidence=report.research_confidence if report else 0.8
    )

    qualification_ai = QualificationAI(
        score=qual.score,
        priority=qual.priority,
        fit_score=qual.fit_score,
        intent_score=qual.intent_score,
        timing_score=qual.timing_score,
        reason=qual.reason or "",
        evidence=qual.evidence or []
    )

    # Call Nemotron model for personalized outreach
    ai_outreach = nemotron_service.generate_outreach_email(
        lead_name=lead.name,
        job_title=lead.job_title or "Executive",
        company_name=lead.company_name,
        website=lead.website,
        intelligence=intelligence,
        qualification=qualification_ai
    )

    # Collect grounding evidence IDs
    grounding_ids = [src.id for src in report.sources] if report and report.sources else []

    # Save to DB
    existing_draft = db.query(OutreachDraft).filter(OutreachDraft.lead_id == lead_id).first()
    if existing_draft:
        db.delete(existing_draft)
        db.commit()

    model_name = settings.NEMOTRON_REASONING_MODEL if settings.NEBIUS_API_KEY else "nvidia/nemotron-3-super-120b-a12b"

    draft = OutreachDraft(
        lead_id=lead.id,
        subject=ai_outreach.subject,
        body=ai_outreach.body,
        personalization_points=ai_outreach.personalization_points,
        grounding_evidence_ids=grounding_ids,
        model_used=model_name,
        confidence=ai_outreach.confidence,
        status="PENDING_APPROVAL",
        generated_at=datetime.datetime.utcnow()
    )
    db.add(draft)
    
    lead.status = "AWAITING_APPROVAL"
    db.commit()
    db.refresh(draft)

    return draft

def approve_or_update_draft_service(draft_id: str, action: str, subject: str = None, body: str = None, db: Session = None) -> OutreachDraft:
    draft = db.query(OutreachDraft).filter(OutreachDraft.id == draft_id).first()
    if not draft:
        raise ValueError(f"Outreach draft not found with id {draft_id}")

    if draft.status == "SENT":
        raise ValueError("Cannot modify or approve an email that has already been SENT.")

    if subject:
        draft.subject = subject
    if body:
        draft.body = body

    action_upper = action.upper()
    if action_upper == "APPROVE":
        draft.status = "APPROVED"
        draft.lead.status = "APPROVED"
    elif action_upper == "REJECT":
        draft.status = "REJECTED"
        draft.lead.status = "CLOSED"
    elif action_upper == "EDIT":
        draft.status = "PENDING_APPROVAL"

    db.commit()
    db.refresh(draft)
    return draft

def send_approved_outreach_service(draft_id: str, db: Session) -> EmailEvent:
    draft = db.query(OutreachDraft).filter(OutreachDraft.id == draft_id).first()
    if not draft:
        raise ValueError(f"Outreach draft not found with id {draft_id}")

    if draft.status == "SENT":
        raise ValueError("This email draft has already been SENT.")

    if draft.status != "APPROVED":
        raise ValueError("Outreach draft must be in APPROVED state before sending.")

    lead = draft.lead
    draft.status = "SENDING"
    db.commit()

    try:
        result = email_service.send_email(
            to_email=lead.email,
            subject=draft.subject,
            body=draft.body
        )

        draft.status = "SENT"
        lead.status = "SENT"

        email_event = EmailEvent(
            lead_id=lead.id,
            outreach_draft_id=draft.id,
            provider=result.get("provider", "mock"),
            provider_message_id=result.get("provider_message_id"),
            status=result.get("status", "SENT"),
            sent_at=datetime.datetime.utcnow()
        )
        db.add(email_event)
        db.commit()
        db.refresh(email_event)

        return email_event
    except Exception as e:
        draft.status = "FAILED"
        db.commit()
        raise e
