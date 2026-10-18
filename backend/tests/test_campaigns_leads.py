import sys
import os
import io
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def test_campaign_creation_and_csv_import():
    # 1. Create Campaign
    create_res = client.post("/api/v1/campaigns", json={
        "name": "Test Hackathon Campaign",
        "description": "Testing campaign flow"
    })
    assert create_res.status_code == 201
    campaign_data = create_res.json()
    campaign_id = campaign_data["id"]
    assert campaign_data["name"] == "Test Hackathon Campaign"

    # 2. Upload CSV preview
    sample_csv = b"name,email,company,website\nAarav Mehta,aarav@technovalabs.com,TechNova Labs,https://technovalabs.com\nBad Lead,not-an-email,Bad Co,https://bad.com\n"
    files = {"file": ("test.csv", io.BytesIO(sample_csv), "text/csv")}
    
    preview_res = client.post(f"/api/v1/campaigns/{campaign_id}/leads/import-preview", files=files)
    assert preview_res.status_code == 200
    preview_data = preview_res.json()
    assert preview_data["total_rows"] == 2
    assert preview_data["valid_count"] == 1
    assert preview_data["invalid_count"] == 1

    # 3. Import leads
    files_import = {"file": ("test.csv", io.BytesIO(sample_csv), "text/csv")}
    import_res = client.post(f"/api/v1/campaigns/{campaign_id}/leads/import", files=files_import)
    assert import_res.status_code == 200
    import_data = import_res.json()
    assert import_data["imported_count"] == 1

    # 4. List leads
    leads_res = client.get(f"/api/v1/leads?campaign_id={campaign_id}")
    assert leads_res.status_code == 200
    leads = leads_res.json()
    assert len(leads) == 1
    assert leads[0]["email"] == "aarav@technovalabs.com"
