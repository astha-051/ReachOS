import logging
from sqlalchemy.orm import Session
from app.models.models import Lead, LeadQualification, ResearchReport
from app.services.research_service import run_lead_research
from app.services.nemotron_service import nemotron_service, LeadIntelligenceAI

logger = logging.getLogger(__name__)

def qualify_lead_service(lead_id: str, db: Session) -> LeadQualification:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise ValueError(f"Lead not found with id {lead_id}")

    # Ensure research exists
    report = db.query(ResearchReport).filter(ResearchReport.lead_id == lead_id).first()
    if not report:
        report = run_lead_research(lead_id, db)

    # Convert report to LeadIntelligenceAI schema
    intelligence = LeadIntelligenceAI(
        company_name=lead.company_name,
        industry=lead.industry or "B2B Technology",
        company_size=report.company.company_size if report.company and report.company.company_size else "UNKNOWN",
        summary=report.summary or "",
        recent_signals=report.recent_signals or [],
        pain_points=report.pain_points or [],
        opportunities=report.opportunities or [],
        confidence=report.research_confidence
    )

    # Call Nemotron Reasoning Model
    ai_qual = nemotron_service.qualify_lead(
        lead_name=lead.name,
        job_title=lead.job_title or "Executive",
        company_name=lead.company_name,
        website=lead.website,
        intelligence=intelligence
    )

    # Determine priority threshold safely
    score = max(0, min(100, ai_qual.score))
    if score >= 80:
        priority = "HIGH"
    elif score >= 50:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # Save to DB
    existing_qual = db.query(LeadQualification).filter(LeadQualification.lead_id == lead_id).first()
    if existing_qual:
        db.delete(existing_qual)
        db.commit()

    qualification = LeadQualification(
        lead_id=lead.id,
        score=score,
        priority=priority,
        fit_score=ai_qual.fit_score,
        intent_score=ai_qual.intent_score,
        timing_score=ai_qual.timing_score,
        evidence=ai_qual.evidence,
        reason=ai_qual.reason
    )
    db.add(qualification)
    
    lead.status = "QUALIFIED"
    db.commit()
    db.refresh(qualification)

    return qualification
