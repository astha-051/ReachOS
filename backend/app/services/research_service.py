import logging
import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Lead, Company, ResearchReport, ResearchSource, AIJob
from app.services.tavily_service import tavily_service
from app.services.nemotron_service import nemotron_service

logger = logging.getLogger(__name__)

def run_lead_research(lead_id: str, db: Session, force_refresh: bool = False) -> ResearchReport:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise ValueError(f"Lead not found with id {lead_id}")

    # Check for existing research report if not force_refresh (Caching mechanism)
    existing_report = db.query(ResearchReport).filter(ResearchReport.lead_id == lead_id).first()
    if existing_report and not force_refresh:
        logger.info(f"Returning cached research report for lead {lead_id}")
        return existing_report

    # Update lead status
    lead.status = "RESEARCH_PENDING"
    db.commit()

    try:
        # Step 1: Tavily Search Evidence Gathering with Relevance Filtering
        evidence_sources = tavily_service.research_company(
            company_name=lead.company_name,
            website=lead.website,
            industry=lead.industry
        )

        # Step 2: Nemotron Deep Model Synthesis
        ai_intel = nemotron_service.synthesize_lead_intelligence(
            company_name=lead.company_name,
            website=lead.website,
            industry=lead.industry,
            research_sources=evidence_sources
        )

        # Step 3: Find or Create Company record in DB
        company = db.query(Company).filter(Company.name == lead.company_name).first()
        if not company:
            company = Company(
                name=ai_intel.company_name or lead.company_name,
                website=lead.website,
                industry=ai_intel.industry,
                company_size=ai_intel.company_size,
                description=ai_intel.summary
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        
        lead.company_id = company.id

        # Step 4: Store ResearchReport & ResearchSources
        if existing_report:
            db.delete(existing_report)
            db.commit()

        report = ResearchReport(
            lead_id=lead.id,
            company_id=company.id,
            summary=ai_intel.summary,
            recent_signals=ai_intel.recent_signals,
            pain_points=ai_intel.pain_points,
            opportunities=ai_intel.opportunities,
            research_confidence=ai_intel.confidence,
            status="COMPLETED"
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        for src in evidence_sources:
            db_source = ResearchSource(
                research_report_id=report.id,
                title=src.get("title"),
                url=src.get("url"),
                domain=src.get("domain"),
                snippet=src.get("snippet"),
                source_type=src.get("source_type", "web"),
                published_date=src.get("published_date"),
                relevance_score=src.get("relevance_score", 1.0)
            )
            db.add(db_source)

        lead.status = "RESEARCHED"
        db.commit()
        db.refresh(report)
        return report

    except Exception as e:
        logger.error(f"Error running research for lead {lead_id}: {str(e)}")
        if existing_report:
            existing_report.status = "FAILED"
            db.commit()
        raise e
