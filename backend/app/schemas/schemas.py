from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Health Check Schema ---
class HealthCheckServices(BaseModel):
    database: bool
    nebius_configured: bool
    tavily_configured: bool
    email_provider: str

class HealthCheckResponse(BaseModel):
    status: str
    version: str
    demo_mode: bool
    services: HealthCheckServices

# --- Campaign Schemas ---
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignResponse(CampaignBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    total_leads: Optional[int] = 0
    validated_leads: Optional[int] = 0
    high_priority_leads: Optional[int] = 0

# --- Lead Schemas ---
class LeadBase(BaseModel):
    name: str
    email: str
    company_name: str
    website: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    campaign_id: str

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    website: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class CSVLeadRow(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None

class CSVImportPreview(BaseModel):
    total_rows: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
    rows: List[Dict[str, Any]]

class CSVImportResult(BaseModel):
    imported_count: int
    invalid_count: int
    duplicate_count: int
    campaign_id: str

# --- Research Schemas ---
class ResearchSourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    title: Optional[str] = None
    url: str
    domain: Optional[str] = None
    snippet: Optional[str] = None
    source_type: Optional[str] = "web"
    published_date: Optional[str] = None
    relevance_score: Optional[float] = 1.0

class ResearchReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    company_id: Optional[str] = None
    summary: Optional[str] = None
    recent_signals: List[Any] = []
    pain_points: List[Any] = []
    opportunities: List[Any] = []
    research_confidence: float = 0.0
    status: str = "COMPLETED"
    sources: List[ResearchSourceSchema] = []
    created_at: datetime

# --- Qualification Schemas ---
class LeadQualificationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    score: int
    priority: str
    fit_score: int
    intent_score: int
    timing_score: int
    evidence: List[Any] = []
    reason: Optional[str] = None
    created_at: datetime

# --- Outreach Schemas ---
class OutreachDraftSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    subject: str
    body: str
    personalization_points: List[Any] = []
    grounding_evidence_ids: List[Any] = []
    model_used: Optional[str] = "nvidia/nemotron-3-super-120b-a12b"
    confidence: float = 0.0
    status: str # DRAFT, GENERATED, PENDING_APPROVAL, APPROVED, SENDING, SENT, REJECTED, FAILED
    created_at: datetime

class OutreachApprovalRequest(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    action: str # APPROVE, EDIT, REJECT

# --- Reply Schemas ---
class ReplySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    body: str
    classification: str
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    urgency: Optional[str] = None
    meeting_requested: Optional[bool] = False
    confidence: float
    detected_intent: Optional[str] = None
    recommended_action: str
    reason: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime

class ReplyAnalysisRequest(BaseModel):
    reply_body: str

# --- Full Lead Detail Response ---
class LeadDetailResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    company_id: Optional[str] = None
    status: str
    validation_status: str
    validation_errors: List[str] = []
    created_at: datetime
    updated_at: datetime
    
    research_report: Optional[ResearchReportSchema] = None
    qualification: Optional[LeadQualificationSchema] = None
    outreach_draft: Optional[OutreachDraftSchema] = None
    replies: List[ReplySchema] = []

# --- Dashboard Stats ---
class DashboardStatsResponse(BaseModel):
    total_campaigns: int
    total_leads: int
    validated_leads: int
    research_completed: int
    high_priority_leads: int
    medium_priority_leads: int
    low_priority_leads: int
    emails_approved: int
    emails_sent: int
    replies_received: int
    interested_replies: int

