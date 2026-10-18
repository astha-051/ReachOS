import urllib.request
import json
import io

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_endpoint(name, url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        if isinstance(data, dict):
            req.data = json.dumps(data).encode("utf-8")
            req.add_header("Content-Type", "application/json")
        else:
            req.data = data
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            print(f"[PASS] {name} ({method} {url}) -> HTTP {resp.status}")
            return body
    except urllib.error.HTTPError as e:
        print(f"[FAIL] {name} ({method} {url}) -> HTTP {e.code}: {e.read().decode()}")
        raise e

print("=== LIVE FASTAPI INTEGRATION VERIFICATION ===")

# 1. Health Check
health = test_endpoint("Health Check", f"{BASE_URL}/health")

# 2. Dashboard Stats
stats = test_endpoint("Dashboard Stats", f"{BASE_URL}/dashboard/stats")

# 3. Create Campaign
campaign = test_endpoint("Create Campaign", f"{BASE_URL}/campaigns", method="POST", data={
    "name": "Live Verification Campaign",
    "description": "Integration test campaign"
})
campaign_id = campaign["id"]

# 4. List Campaigns
campaigns = test_endpoint("List Campaigns", f"{BASE_URL}/campaigns")

# 5. Get Campaign Detail
campaign_detail = test_endpoint("Get Campaign Detail", f"{BASE_URL}/campaigns/{campaign_id}")

# 6. List Leads
leads = test_endpoint("List Leads", f"{BASE_URL}/leads")

# 7. Test CSV Import Preview & Import
boundary = '---------------------------974767299852498929531610575'
csv_content = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="sample.csv"\r\n'
    f'Content-Type: text/csv\r\n\r\n'
    f'Full Name,Email Address,Company Name,Website,Job Title\r\n'
    f'Alex Turner,alex@summitcloud.io,Summit Cloud,https://summitcloud.io,VP Sales\r\n'
    f'--{boundary}--\r\n'
).encode("utf-8")

headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}

csv_preview = test_endpoint("CSV Import Preview", f"{BASE_URL}/campaigns/{campaign_id}/leads/import-preview", method="POST", data=csv_content, headers=headers)
csv_import = test_endpoint("CSV Import", f"{BASE_URL}/campaigns/{campaign_id}/leads/import", method="POST", data=csv_content, headers=headers)

# 8. List Leads again
updated_leads = test_endpoint("List Leads After Import", f"{BASE_URL}/leads?campaign_id={campaign_id}")

print("\nALL LIVE ENDPOINT VERIFICATIONS PASSED SUCCESSFULLY!")
