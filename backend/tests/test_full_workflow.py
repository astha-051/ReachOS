import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def test_full_reachos_ai_workflow():
    # 1. Create Campaign
    c_res = client.post("/api/v1/campaigns", json={
        "name": "Enterprise AI Outreach Campaign",
        "description": "Testing full end-to-end AI workflow"
    })
    assert c_res.status_code == 201
    campaign_id = c_res.json()["id"]

    # 2. Add Lead
    l_res = client.post("/api/v1/leads", json={
        "campaign_id": campaign_id,
        "name": "Aarav Mehta",
        "email": "aarav@technovalabs.com",
        "company_name": "TechNova Labs",
        "website": "https://technovalabs.com",
        "job_title": "VP of Growth & Sales",
        "industry": "B2B SaaS"
    })
    assert l_res.status_code == 201
    lead_id = l_res.json()["id"]

    # 3. Trigger Research
    r_res = client.post(f"/api/v1/leads/{lead_id}/research")
    assert r_res.status_code == 200
    research = r_res.json()
    assert research["status"] == "COMPLETED"
    assert len(research["recent_signals"]) > 0

    # 4. Trigger Qualification
    q_res = client.post(f"/api/v1/leads/{lead_id}/qualify")
    assert q_res.status_code == 200
    qual = q_res.json()
    assert qual["priority"] in ("HIGH", "MEDIUM", "LOW")
    assert qual["score"] >= 0

    # 5. Generate Outreach Draft
    o_res = client.post(f"/api/v1/leads/{lead_id}/outreach")
    assert o_res.status_code == 200
    draft = o_res.json()
    draft_id = draft["id"]
    assert draft["status"] == "PENDING_APPROVAL"
    assert len(draft["subject"]) > 0

    # 6. Approve Draft (Human in the Loop)
    app_res = client.post(f"/api/v1/outreach/{draft_id}/approve", json={
        "action": "APPROVE"
    })
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "APPROVED"

    # 7. Send Email
    s_res = client.post(f"/api/v1/outreach/{draft_id}/send")
    assert s_res.status_code == 200
    send_data = s_res.json()
    assert send_data["status"] == "success"

    # 8. Analyze Reply
    rep_res = client.post(f"/api/v1/leads/{lead_id}/reply/analyze", json={
        "reply_body": "Hi, I saw your email and would love to schedule a demo to discuss pricing for our SDR team."
    })
    assert rep_res.status_code == 200
    reply_data = rep_res.json()
    assert reply_data["classification"] == "INTERESTED"
    assert reply_data["recommended_action"] == "BOOK_MEETING"

    # 9. Verify Dashboard Analytics Stats
    stats_res = client.get("/api/v1/dashboard/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_leads"] >= 1
    assert stats["emails_sent"] >= 1
    assert stats["replies_received"] >= 1
