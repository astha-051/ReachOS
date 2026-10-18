import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.lead_service import (
    normalize_header,
    validate_email_syntax,
    validate_url_syntax,
    validate_lead_data,
    parse_csv_content,
    preview_csv_import
)

def test_header_normalization():
    assert normalize_header("Full Name") == "name"
    assert normalize_header("Email Address") == "email"
    assert normalize_header("Company Name") == "company"
    assert normalize_header("Company Website") == "website"
    assert normalize_header("Job Title") == "job_title"

def test_email_validation():
    assert validate_email_syntax("aarav@technovalabs.com") is True
    assert validate_email_syntax("invalid-email") is False
    assert validate_email_syntax("") is False

def test_url_validation():
    assert validate_url_syntax("https://technovalabs.com") is True
    assert validate_url_syntax("http://apexcloud.io") is True
    assert validate_url_syntax("not-a-url") is False
    assert validate_url_syntax("") is True

def test_lead_data_validation():
    valid_lead = {
        "name": "Aarav Mehta",
        "email": "aarav@technovalabs.com",
        "company": "TechNova Labs",
        "website": "https://technovalabs.com"
    }
    status, errors = validate_lead_data(valid_lead)
    assert status == "VALID"
    assert len(errors) == 0

    invalid_lead = {
        "name": "Invalid Lead",
        "email": "not-an-email",
        "company": "Test Co"
    }
    status, errors = validate_lead_data(invalid_lead)
    assert status == "INVALID"
    assert len(errors) > 0

def test_csv_parser():
    csv_bytes = b"Full Name,Email Address,Company Name\nJohn Doe,john@example.com,Acme Inc\n"
    leads = parse_csv_content(csv_bytes)
    assert len(leads) == 1
    assert leads[0]["name"] == "John Doe"
    assert leads[0]["email"] == "john@example.com"
    assert leads[0]["company"] == "Acme Inc"
