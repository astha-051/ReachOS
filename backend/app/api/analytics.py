from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Campaign, Lead, ResearchReport, LeadQualification, OutreachDraft, EmailEvent, Reply
from app.schemas.schemas import DashboardStatsResponse

router = APIRouter()

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_campaigns = db.query(Campaign).count()
    total_leads = db.query(Lead).count()
    validated_leads = db.query(Lead).filter(Lead.validation_status == "VALID").count()
    research_completed = db.query(ResearchReport).filter(ResearchReport.status == "COMPLETED").count()
    
    high_priority = db.query(LeadQualification).filter(LeadQualification.priority == "HIGH").count()
    medium_priority = db.query(LeadQualification).filter(LeadQualification.priority == "MEDIUM").count()
    low_priority = db.query(LeadQualification).filter(LeadQualification.priority == "LOW").count()

    emails_approved = db.query(OutreachDraft).filter(OutreachDraft.status == "APPROVED").count()
    emails_sent = db.query(EmailEvent).count()

    replies_received = db.query(Reply).count()
    interested_replies = db.query(Reply).filter(Reply.classification == "INTERESTED").count()

    return DashboardStatsResponse(
        total_campaigns=total_campaigns,
        total_leads=total_leads,
        validated_leads=validated_leads,
        research_completed=research_completed,
        high_priority_leads=high_priority,
        medium_priority_leads=medium_priority,
        low_priority_leads=low_priority,
        emails_approved=emails_approved,
        emails_sent=emails_sent,
        replies_received=replies_received,
        interested_replies=interested_replies
    )
