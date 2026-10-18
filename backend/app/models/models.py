import uuid
import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="ACTIVE") # ACTIVE, ARCHIVED, DRAFT
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="campaigns")
    leads = relationship("Lead", back_populates="campaign", cascade="all, delete-orphan")

class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, index=True, nullable=False)
    website = Column(String, nullable=True)
    domain = Column(String, index=True, nullable=True)
    industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    leads = relationship("Lead", back_populates="company_obj")
    research_reports = relationship("ResearchReport", back_populates="company", cascade="all, delete-orphan")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=generate_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=True)

    name = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    company_name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Lead state: NEW, VALIDATED, RESEARCH_PENDING, RESEARCHED, QUALIFIED, OUTREACH_DRAFTED, AWAITING_APPROVAL, APPROVED, SENT, REPLIED, ACTION_REQUIRED, CLOSED
    status = Column(String, default="NEW", index=True)
    
    # Validation
    validation_status = Column(String, default="UNVALIDATED") # VALID, INVALID, DUPLICATE, INCOMPLETE
    validation_errors = Column(JSON, default=list) # List of string error messages

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    campaign = relationship("Campaign", back_populates="leads")
    company_obj = relationship("Company", back_populates="leads")
    research_report = relationship("ResearchReport", back_populates="lead", uselist=False, cascade="all, delete-orphan")
    qualification = relationship("LeadQualification", back_populates="lead", uselist=False, cascade="all, delete-orphan")
    outreach_draft = relationship("OutreachDraft", back_populates="lead", uselist=False, cascade="all, delete-orphan")
    email_events = relationship("EmailEvent", back_populates="lead", cascade="all, delete-orphan")
    replies = relationship("Reply", back_populates="lead", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="lead", cascade="all, delete-orphan")

class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=True)

    summary = Column(Text, nullable=True)
    recent_signals = Column(JSON, default=list) # List of dicts or strings
    pain_points = Column(JSON, default=list)
    opportunities = Column(JSON, default=list)
    research_confidence = Column(Float, default=0.0)
    raw_research_reference = Column(Text, nullable=True)
    
    status = Column(String, default="COMPLETED") # NOT_STARTED, IN_PROGRESS, COMPLETED, FAILED

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="research_report")
    company = relationship("Company", back_populates="research_reports")
    sources = relationship("ResearchSource", back_populates="research_report", cascade="all, delete-orphan")

class ResearchSource(Base):
    __tablename__ = "research_sources"

    id = Column(String, primary_key=True, default=generate_uuid)
    research_report_id = Column(String, ForeignKey("research_reports.id"), nullable=False)

    title = Column(String, nullable=True)
    url = Column(String, nullable=False)
    domain = Column(String, nullable=True)
    snippet = Column(Text, nullable=True)
    source_type = Column(String, default="web")
    published_date = Column(String, nullable=True)
    relevance_score = Column(Float, default=1.0)
    retrieved_at = Column(DateTime, default=datetime.datetime.utcnow)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    research_report = relationship("ResearchReport", back_populates="sources")

class LeadQualification(Base):
    __tablename__ = "lead_qualifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)

    score = Column(Integer, default=0) # 0 to 100
    priority = Column(String, default="MEDIUM") # HIGH, MEDIUM, LOW
    fit_score = Column(Integer, default=0)
    intent_score = Column(Integer, default=0)
    timing_score = Column(Integer, default=0)
    evidence = Column(JSON, default=list) # List of evidence strings/dicts
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="qualification")

class OutreachDraft(Base):
    __tablename__ = "outreach_drafts"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)

    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    personalization_points = Column(JSON, default=list)
    grounding_evidence_ids = Column(JSON, default=list)
    model_used = Column(String, default="nvidia/nemotron-3-super-120b-a12b")
    confidence = Column(Float, default=0.0)
    
    # Status: DRAFT, GENERATED, PENDING_APPROVAL, APPROVED, SENDING, SENT, REJECTED, FAILED
    status = Column(String, default="DRAFT")

    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="outreach_draft")
    email_events = relationship("EmailEvent", back_populates="outreach_draft")

class EmailEvent(Base):
    __tablename__ = "email_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    outreach_draft_id = Column(String, ForeignKey("outreach_drafts.id"), nullable=True)

    provider = Column(String, default="mock") # mock, resend
    provider_message_id = Column(String, nullable=True)
    status = Column(String, default="SENT") # SENT, DELIVERED, FAILED
    
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)

    lead = relationship("Lead", back_populates="email_events")
    outreach_draft = relationship("OutreachDraft", back_populates="email_events")
    replies = relationship("Reply", back_populates="email_event")

class Reply(Base):
    __tablename__ = "replies"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    email_event_id = Column(String, ForeignKey("email_events.id"), nullable=True)

    body = Column(Text, nullable=False)
    # INTERESTED, QUESTION, OBJECTION, NOT_INTERESTED, OUT_OF_OFFICE, UNSUBSCRIBE, UNKNOWN
    classification = Column(String, default="UNKNOWN")
    intent = Column(String, nullable=True) # interested | not_interested | question | objection | meeting_request | unsubscribe | unclear
    sentiment = Column(String, nullable=True) # positive | neutral | negative
    urgency = Column(String, nullable=True) # high | medium | low
    meeting_requested = Column(Boolean, default=False)
    confidence = Column(Float, default=0.0)
    detected_intent = Column(String, nullable=True)
    # BOOK_MEETING, ANSWER_QUESTION, SEND_INFORMATION, FOLLOW_UP, STOP_CONTACT, WAIT, MANUAL_REVIEW
    recommended_action = Column(String, default="MANUAL_REVIEW")
    reason = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="replies")
    email_event = relationship("EmailEvent", back_populates="replies")

class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)

    scheduled_at = Column(DateTime, nullable=False)
    action = Column(String, nullable=False)
    status = Column(String, default="PENDING") # PENDING, COMPLETED, CANCELLED

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="follow_ups")

class AIJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)

    job_type = Column(String, nullable=False) # RESEARCH, QUALIFY, OUTREACH, REPLY_ANALYSIS
    status = Column(String, default="QUEUED") # QUEUED, RUNNING, COMPLETED, FAILED
    error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
