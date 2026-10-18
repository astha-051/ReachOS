from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Lead, ResearchReport
from app.schemas.schemas import ResearchReportSchema
from app.services.research_service import run_lead_research

router = APIRouter()

@router.post("/leads/{lead_id}/research", response_model=ResearchReportSchema)
def trigger_research(
    lead_id: str,
    force_refresh: bool = Query(False),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    try:
        report = run_lead_research(lead_id, db, force_refresh=force_refresh)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@router.get("/leads/{lead_id}/research", response_model=ResearchReportSchema)
def get_research(lead_id: str, db: Session = Depends(get_db)):
    report = db.query(ResearchReport).filter(ResearchReport.lead_id == lead_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="No research report found for this lead")
    return report
