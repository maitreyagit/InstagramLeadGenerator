import pytest
from src.utils.normalizer import normalize_to_username
from src.extractor.contact_extractor import extract_emails, extract_phones

def test_normalize_to_username():
    assert normalize_to_username("https://www.instagram.com/nike/") == "nike"
    assert normalize_to_username("https://instagram.com/nike") == "nike"
    assert normalize_to_username("@nike") == "nike"
    assert normalize_to_username("nike") == "nike"

def test_extract_emails():
    text = "Contact us at support@nike.com or hello@nike.com"
    emails = extract_emails(text)
    assert len(emails) == 2
    assert "support@nike.com" in emails
    assert "hello@nike.com" in emails

def test_extract_phones():
    text = "Call us at +1-800-555-0199 or 555-1234"
    phones = extract_phones(text)
    assert len(phones) >= 1
