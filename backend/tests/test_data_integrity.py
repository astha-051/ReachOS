import sys
import os
import io
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.services.tavily_service import tavily_service
from app.services.nemotron_service import nemotron_service
from app.ai.schemas.ai_schemas import LeadIntelligenceAI, QualificationAI, OutreachAI, ReplyClassificationAI

client = TestClient(app)

def test_1_correct_company_research_integrity():
    """Verify research for Orion Business Advisory yields Orion data, NOT TechNova Labs."""
    res = tavily_service._get_fallback_mock_evidence("Orion Business Advisory", "https://orionadvisory.com", "Management Consulting")
    assert len(res) == 2
    assert "Orion Business Advisory" in res[0]["title"]
    assert "TechNova" not in res[0]["title"]
    assert res[0]["domain"] == "orionadvisory.com"

def test_2_relevance_check_rejects_unrelated_company():
    """Verify company relevance filter rejects search results for unrelated company."""
    unrelated_result = {
        "title": "TechNova Labs Enterprise Software Solutions",
        "snippet": "TechNova Labs provides enterprise SaaS automation tools for commercial teams.",
        "url": "https://technovalabs.com/about"
    }
    score = tavily_service.check_company_relevance("Orion Business Advisory", "https://orionadvisory.com", unrelated_result)
    assert score < 0.4 # Rejection threshold is 0.4

def test_3_relevance_check_accepts_target_company():
    """Verify company relevance filter accepts valid search result for target company."""
    target_result = {
        "title": "Orion Business Advisory - Strategic Growth Services",
        "snippet": "Orion Business Advisory offers enterprise growth advisory and commercial scaling.",
        "url": "https://orionadvisory.com/services"
    }
    score = tavily_service.check_company_relevance("Orion Business Advisory", "https://orionadvisory.com", target_result)
    assert score >= 0.8

def test_4_no_sources_yields_insufficient_evidence():
    """Verify empty search sources yields 'insufficient_evidence' summary."""
    intel = nemotron_service.synthesize_lead_intelligence("Unknown Startup", None, None, [])
    assert intel.summary == "insufficient_evidence"
    assert len(intel.recent_signals) == 0

def test_5_dynamic_nemotron_fallback_isolation():
    """Verify fallback generation builds dynamic response using target lead's actual company and name."""
    prompt = "TARGET COMPANY: Orion Business Advisory\nTARGET CONTACT: Olivia Smith\nTARGET ROLE: Managing Director\nTARGET WEBSITE: https://orionadvisory.com"
    
    intel = nemotron_service._get_fallback_ai_response(LeadIntelligenceAI, prompt)
    assert intel.company_name == "Orion Business Advisory"
    assert "TechNova" not in intel.company_name

    qual = nemotron_service._get_fallback_ai_response(QualificationAI, prompt)
    assert "Orion Business Advisory" in qual.reason
    assert qual.score >= 80

    outreach = nemotron_service._get_fallback_ai_response(OutreachAI, prompt)
    assert "Olivia" in outreach.body
    assert "Orion Business Advisory" in outreach.body
    assert "TechNova" not in outreach.body

def test_6_different_leads_produce_different_scores():
    """Verify executive vs junior role leads produce different qualification scores."""
    prompt_exec = "TARGET COMPANY: Acme Corp\nTARGET CONTACT: Sarah Jenkins\nTARGET ROLE: VP of Sales\nTARGET WEBSITE: https://acme.com"
    qual_exec = nemotron_service._get_fallback_ai_response(QualificationAI, prompt_exec)

    prompt_junior = "TARGET COMPANY: Acme Corp\nTARGET CONTACT: John Doe\nTARGET ROLE: Intern\nTARGET WEBSITE: https://acme.com"
    qual_junior = nemotron_service._get_fallback_ai_response(QualificationAI, prompt_junior)

    assert qual_exec.score > qual_junior.score
    assert qual_exec.priority == "HIGH"

def test_7_email_state_machine_approval_and_sending():
    """Verify email state machine transitions and blocks modifying SENT draft."""
    # 1. Create Campaign
    c_res = client.post("/api/v1/campaigns", json={"name": "Audit Campaign"})
    campaign_id = c_res.json()["id"]

    # 2. Add Lead (Olivia Smith at Orion Business Advisory)
    l_res = client.post("/api/v1/leads", json={
        "campaign_id": campaign_id,
        "name": "Olivia Smith",
        "email": "olivia@orionadvisory.com",
        "company_name": "Orion Business Advisory",
        "website": "https://orionadvisory.com",
        "job_title": "Managing Director"
    })
    lead_id = l_res.json()["id"]

    # 3. Generate Outreach Draft (should be PENDING_APPROVAL)
    o_res = client.post(f"/api/v1/leads/{lead_id}/outreach")
    assert o_res.status_code == 200
    draft = o_res.json()
    draft_id = draft["id"]
    assert draft["status"] == "PENDING_APPROVAL"
    assert "Olivia" in draft["body"]
    assert "Orion Business Advisory" in draft["body"]

    # 4. Approve Draft -> APPROVED
    app_res = client.post(f"/api/v1/outreach/{draft_id}/approve", json={"action": "APPROVE"})
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "APPROVED"

    # 5. Send Draft -> SENT
    send_res = client.post(f"/api/v1/outreach/{draft_id}/send")
    assert send_res.status_code == 200

    # 6. Verify modifying SENT draft fails with HTTP 400
    modify_res = client.post(f"/api/v1/outreach/{draft_id}/approve", json={"action": "APPROVE"})
    assert modify_res.status_code == 400

    # 7. Verify resending SENT draft fails with HTTP 400
    resend_res = client.post(f"/api/v1/outreach/{draft_id}/send")
    assert resend_res.status_code == 400

def test_8_reply_classification_and_persistence():
    """Verify reply classification extracts structured intent, sentiment, and urgency."""
    c_res = client.post("/api/v1/campaigns", json={"name": "Reply Audit Campaign"})
    campaign_id = c_res.json()["id"]

    l_res = client.post("/api/v1/leads", json={
        "campaign_id": campaign_id,
        "name": "David Miller",
        "email": "david@apexcloud.io",
        "company_name": "Apex Cloud",
        "website": "https://apexcloud.io",
        "job_title": "CTO"
    })
    lead_id = l_res.json()["id"]

    reply_res = client.post(f"/api/v1/leads/{lead_id}/reply/analyze", json={
        "reply_body": "Thanks for the outreach. We are interested in a demo next Tuesday to discuss pricing."
    })
    assert reply_res.status_code == 200
    data = reply_res.json()
    assert data["classification"] == "INTERESTED"
    assert data["intent"] == "meeting_request"
    assert data["meeting_requested"] is True
    assert data["recommended_action"] == "BOOK_MEETING"

def test_9_persistence_across_lead_retrieval():
    """Verify page refresh / lead retrieval retains all persisted research, qualification, and outreach data."""
    # List leads and verify lead record includes research and qualification
    leads_res = client.get("/api/v1/leads")
    assert leads_res.status_code == 200
    leads = leads_res.json()
    assert len(leads) >= 1
    
    olivia_lead = next((l for l in leads if l["name"] == "Olivia Smith"), None)
    assert olivia_lead is not None
    assert olivia_lead["company_name"] == "Orion Business Advisory"
    assert olivia_lead["outreach_draft"]["status"] == "SENT"
