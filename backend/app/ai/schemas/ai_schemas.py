from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class LeadIntelligenceAI(BaseModel):
    company_name: str = Field(description="Normalized official company name")
    industry: str = Field(description="Primary business industry")
    company_size: str = Field(description="Estimated company size e.g. 50-100 employees or UNKNOWN")
    summary: str = Field(description="Concise 2-3 sentence company overview based on web research")
    recent_signals: List[str] = Field(default=[], description="List of verified recent business signals e.g. hiring, expanding")
    pain_points: List[str] = Field(default=[], description="Detected potential business pain points")
    opportunities: List[str] = Field(default=[], description="Identified sales or outreach opportunities")
    confidence: float = Field(default=0.8, description="Confidence score between 0.0 and 1.0")

class QualificationAI(BaseModel):
    score: int = Field(description="Overall Lead Score from 0 to 100")
    priority: str = Field(description="Priority classification: HIGH, MEDIUM, or LOW")
    fit_score: int = Field(description="Fit score from 0 to 100")
    intent_score: int = Field(description="Intent score from 0 to 100")
    timing_score: int = Field(description="Timing score from 0 to 100")
    reason: str = Field(description="Concise 1-2 sentence decision explanation")
    evidence: List[str] = Field(default=[], description="List of bulleted justifications supporting score")

class OutreachAI(BaseModel):
    subject: str = Field(description="Compelling personalized email subject line")
    body: str = Field(description="Concise 3-5 sentence evidence-backed outbound email body")
    personalization_points: List[str] = Field(default=[], description="List of specific research facts used for personalization")
    confidence: float = Field(default=0.85, description="Personalization confidence score between 0.0 and 1.0")

class ReplyClassificationAI(BaseModel):
    classification: str = Field(description="Category: INTERESTED, QUESTION, OBJECTION, NOT_INTERESTED, OUT_OF_OFFICE, UNSUBSCRIBE, UNKNOWN")
    intent: str = Field(default="unclear", description="intent: interested | not_interested | question | objection | meeting_request | unsubscribe | unclear")
    sentiment: str = Field(default="neutral", description="sentiment: positive | neutral | negative")
    urgency: str = Field(default="medium", description="urgency: high | medium | low")
    meeting_requested: bool = Field(default=False, description="True if prospect explicitly requested a call, meeting or demo")
    confidence: float = Field(default=0.9, description="Confidence score between 0.0 and 1.0")
    detected_intent: str = Field(description="Brief summary of prospect intent")
    recommended_action: str = Field(description="Action: BOOK_MEETING, ANSWER_QUESTION, SEND_INFORMATION, FOLLOW_UP, STOP_CONTACT, WAIT, MANUAL_REVIEW")
    reason: str = Field(description="Explanation of classification and recommendation")
    summary: str = Field(default="", description="Concise 1-sentence summary of reply content")
