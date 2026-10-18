import re
import csv
import io
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.models import Lead, Campaign, Company

HEADER_MAPPINGS = {
    "full_name": "name",
    "lead_name": "name",
    "contact_name": "name",
    "email_address": "email",
    "work_email": "email",
    "company_name": "company",
    "organization": "company",
    "company_website": "website",
    "url": "website",
    "domain": "website",
    "job title": "job_title",
    "title": "job_title",
    "role": "job_title",
    "sector": "industry",
}

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
URL_REGEX = re.compile(r"^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$")

def normalize_header(header: str) -> str:
    cleaned = header.strip().lower().replace(" ", "_")
    return HEADER_MAPPINGS.get(cleaned, cleaned)

def validate_email_syntax(email: str) -> bool:
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_url_syntax(url: str) -> bool:
    if not url:
        return True # Optional field
    return bool(URL_REGEX.match(url.strip()))

def validate_lead_data(data: Dict[str, Any], existing_emails: set = None) -> Tuple[str, List[str]]:
    """
    Validates a lead row dictionary.
    Returns (status, errors_list)
    Statuses: VALID, INVALID, DUPLICATE, INCOMPLETE
    """
    errors = []
    
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    company = (data.get("company") or "").strip()
    website = (data.get("website") or "").strip()

    if not email:
        errors.append("Missing required field: email")
    elif not validate_email_syntax(email):
        errors.append(f"Invalid email format: '{email}'")

    if not name:
        errors.append("Missing field: name")

    if not company:
        errors.append("Missing field: company")

    if website and not validate_url_syntax(website):
        errors.append(f"Invalid website URL format: '{website}'")

    # Determine status
    if existing_emails and email and email.lower() in existing_emails:
        return "DUPLICATE", ["Duplicate email found in campaign or batch"]

    if "Missing required field: email" in errors or "Invalid email format" in str(errors):
        return "INVALID", errors
    
    if errors:
        return "INCOMPLETE", errors

    return "VALID", []

def parse_csv_content(content_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parses raw CSV bytes, normalizes headers, returns list of lead dicts.
    """
    text_data = content_bytes.decode("utf-8-sig", errors="ignore")
    reader = csv.reader(io.StringIO(text_data))
    
    rows = list(reader)
    if not rows:
        return []

    raw_headers = rows[0]
    normalized_headers = [normalize_header(h) for h in raw_headers]

    parsed_leads = []
    for row in rows[1:]:
        if not any(row): # Skip empty lines
            continue
        lead_dict = {}
        for idx, val in enumerate(row):
            if idx < len(normalized_headers):
                lead_dict[normalized_headers[idx]] = val.strip() if val else ""
        parsed_leads.append(lead_dict)

    return parsed_leads

def preview_csv_import(parsed_leads: List[Dict[str, Any]], db: Session = None, campaign_id: str = None) -> Dict[str, Any]:
    existing_emails = set()
    if db and campaign_id:
        existing_in_db = db.query(Lead.email).filter(Lead.campaign_id == campaign_id).all()
        existing_emails = {e[0].lower() for e in existing_in_db}

    seen_in_batch = set()
    rows_preview = []
    valid_count = 0
    invalid_count = 0
    duplicate_count = 0

    for idx, lead_dict in enumerate(parsed_leads):
        email = (lead_dict.get("email") or "").strip().lower()
        
        # Check duplicate against batch
        is_batch_duplicate = email in seen_in_batch if email else False
        if email:
            seen_in_batch.add(email)

        combined_existing = existing_emails.union({"seen_batch": email} if is_batch_duplicate else set())
        
        status, errors = validate_lead_data(lead_dict, existing_emails=existing_emails if not is_batch_duplicate else None)
        if is_batch_duplicate and status != "INVALID":
            status = "DUPLICATE"
            errors = ["Duplicate email in uploaded CSV"]

        if status == "VALID":
            valid_count += 1
        elif status == "DUPLICATE":
            duplicate_count += 1
        else:
            invalid_count += 1

        rows_preview.append({
            "row_index": idx + 1,
            "data": lead_dict,
            "status": status,
            "errors": errors
        })

    return {
        "total_rows": len(parsed_leads),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "duplicate_count": duplicate_count,
        "rows": rows_preview
    }
