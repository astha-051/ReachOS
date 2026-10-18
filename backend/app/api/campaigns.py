from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.models import Campaign, Lead, LeadQualification
from app.schemas.schemas import (
    CampaignCreate, CampaignResponse, CSVImportPreview, CSVImportResult, LeadBase
)
from app.services.lead_service import (
    parse_csv_content, preview_csv_import, validate_lead_data
)

router = APIRouter()

@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign_in: CampaignCreate, db: Session = Depends(get_db)):
    campaign = Campaign(
        name=campaign_in.name,
        description=campaign_in.description,
        status="ACTIVE"
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign

@router.get("", response_model=List[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    results = []
    for c in campaigns:
        total_leads = db.query(Lead).filter(Lead.campaign_id == c.id).count()
        validated_leads = db.query(Lead).filter(Lead.campaign_id == c.id, Lead.validation_status == "VALID").count()
        high_priority = db.query(Lead).join(LeadQualification).filter(
            Lead.campaign_id == c.id, LeadQualification.priority == "HIGH"
        ).count()

        results.append(CampaignResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at,
            total_leads=total_leads,
            validated_leads=validated_leads,
            high_priority_leads=high_priority
        ))
    return results

@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    total_leads = db.query(Lead).filter(Lead.campaign_id == campaign.id).count()
    validated_leads = db.query(Lead).filter(Lead.campaign_id == campaign.id, Lead.validation_status == "VALID").count()
    high_priority = db.query(Lead).join(LeadQualification, isouter=True).filter(
        Lead.campaign_id == campaign.id, LeadQualification.priority == "HIGH"
    ).count()

    return CampaignResponse(
        id=campaign.id,
        name=campaign.name,
        description=campaign.description,
        status=campaign.status,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        total_leads=total_leads,
        validated_leads=validated_leads,
        high_priority_leads=high_priority
    )

@router.post("/{campaign_id}/leads/import-preview", response_model=CSVImportPreview)
async def preview_lead_import(
    campaign_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    content = await file.read()
    parsed_leads = parse_csv_content(content)
    preview = preview_csv_import(parsed_leads, db=db, campaign_id=campaign_id)
    return preview

@router.post("/{campaign_id}/leads/import", response_model=CSVImportResult)
async def import_leads(
    campaign_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    content = await file.read()
    parsed_leads = parse_csv_content(content)
    preview = preview_csv_import(parsed_leads, db=db, campaign_id=campaign_id)

    imported_count = 0
    invalid_count = 0
    duplicate_count = 0

    for item in preview["rows"]:
        status = item["status"]
        data = item["data"]
        errors = item["errors"]

        if status in ("VALID", "INCOMPLETE"):
            lead = Lead(
                campaign_id=campaign_id,
                name=data.get("name", "Unknown Name"),
                email=data.get("email", ""),
                company_name=data.get("company", "Unknown Company"),
                website=data.get("website"),
                job_title=data.get("job_title"),
                industry=data.get("industry"),
                notes=data.get("notes"),
                validation_status=status,
                validation_errors=errors,
                status="VALIDATED" if status == "VALID" else "NEW"
            )
            db.add(lead)
            imported_count += 1
        elif status == "DUPLICATE":
            duplicate_count += 1
        else:
            invalid_count += 1

    db.commit()
    return CSVImportResult(
        imported_count=imported_count,
        invalid_count=invalid_count,
        duplicate_count=duplicate_count,
        campaign_id=campaign_id
    )
