from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Lead, OutreachDraft, LeadQualification
from app.schemas.schemas import (
    LeadQualificationSchema, OutreachDraftSchema, OutreachApprovalRequest
)
from app.services.qualification_service import qualify_lead_service
from app.services.outreach_service import (
    generate_outreach_draft_service,
    approve_or_update_draft_service,
    send_approved_outreach_service
)

router = APIRouter()

@router.post("/leads/{lead_id}/qualify", response_model=LeadQualificationSchema)
def qualify_lead(lead_id: str, db: Session = Depends(get_db)):
    try:
        qual = qualify_lead_service(lead_id, db)
        return qual
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qualification failed: {str(e)}")

@router.post("/leads/{lead_id}/outreach", response_model=OutreachDraftSchema)
def generate_outreach(lead_id: str, db: Session = Depends(get_db)):
    try:
        draft = generate_outreach_draft_service(lead_id, db)
        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outreach generation failed: {str(e)}")

@router.post("/outreach/{draft_id}/approve", response_model=OutreachDraftSchema)
def approve_outreach(draft_id: str, req: OutreachApprovalRequest, db: Session = Depends(get_db)):
    try:
        draft = approve_or_update_draft_service(
            draft_id=draft_id,
            action=req.action,
            subject=req.subject,
            body=req.body,
            db=db
        )
        return draft
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/outreach/{draft_id}/send")
def send_outreach(draft_id: str, db: Session = Depends(get_db)):
    try:
        email_event = send_approved_outreach_service(draft_id, db)
        return {
            "status": "success",
            "message_id": email_event.provider_message_id,
            "provider": email_event.provider,
            "sent_at": email_event.sent_at
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
