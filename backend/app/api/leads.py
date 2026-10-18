from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import Lead, Campaign, ResearchReport, LeadQualification, OutreachDraft, Reply
from app.schemas.schemas import LeadCreate, LeadUpdate, LeadDetailResponse
from app.services.lead_service import validate_lead_data

router = APIRouter()

@router.get("", response_model=List[LeadDetailResponse])
def list_leads(
    campaign_id: Optional[str] = None,
    validation_status: Optional[str] = None,
    priority: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Lead).options(
        joinedload(Lead.research_report),
        joinedload(Lead.qualification),
        joinedload(Lead.outreach_draft),
        joinedload(Lead.replies)
    )

    if campaign_id:
        query = query.filter(Lead.campaign_id == campaign_id)
    
    if validation_status:
        query = query.filter(Lead.validation_status == validation_status)

    if status_filter:
        query = query.filter(Lead.status == status_filter)

    if priority:
        query = query.join(LeadQualification, isouter=True).filter(LeadQualification.priority == priority)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_pattern)) |
            (Lead.email.ilike(search_pattern)) |
            (Lead.company_name.ilike(search_pattern)) |
            (Lead.job_title.ilike(search_pattern))
        )

    leads = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()
    return leads

@router.get("/{lead_id}", response_model=LeadDetailResponse)
def get_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).options(
        joinedload(Lead.research_report),
        joinedload(Lead.qualification),
        joinedload(Lead.outreach_draft),
        joinedload(Lead.replies)
    ).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.post("", response_model=LeadDetailResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == lead_in.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    lead_dict = lead_in.model_dump()
    lead_dict["company"] = lead_dict.get("company_name", "")
    val_status, errors = validate_lead_data(lead_dict)

    lead = Lead(
        campaign_id=lead_in.campaign_id,
        name=lead_in.name,
        email=lead_in.email,
        company_name=lead_in.company_name,
        website=lead_in.website,
        job_title=lead_in.job_title,
        industry=lead_in.industry,
        notes=lead_in.notes,
        validation_status=val_status,
        validation_errors=errors,
        status="VALIDATED" if val_status == "VALID" else "NEW"
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.put("/{lead_id}", response_model=LeadDetailResponse)
def update_lead(lead_id: str, lead_in: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = lead_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(lead, field, val)

    db.commit()
    db.refresh(lead)
    return lead

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()
    return None
