import re
from typing import List, Dict, Any

EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_REGEX = re.compile(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')

BOOKING_DOMAINS = [
    "calendly.com", "fresha.com", "treatwell.com", "vagaro.com", 
    "booksy.com", "squareup.com", "linktr.ee", "beacons.ai", "wa.me", "maps.app.goo.gl"
]

def extract_emails(text: str) -> List[str]:
    if not text:
        return []
    return list(set(EMAIL_REGEX.findall(text)))

def extract_phones(text: str) -> List[str]:
    if not text:
        return []
    # This is a basic regex, could return false positives. 
    # Usually we'd pass this through phonenumbers lib to validate.
    matches = PHONE_REGEX.findall(text)
    # Filter out obvious non-phones (like simple numbers)
    return list(set([m for m in matches if len(re.sub(r'\D', '', m)) >= 7]))

def categorize_links(links: List[str]) -> Dict[str, Any]:
    categorized = {
        "whatsapp": "",
        "booking_links": [],
        "linktree_or_similar": [],
        "social_media": [],
        "google_maps": "",
        "other_websites": []
    }
    
    for link in links:
        link_lower = link.lower()
        if "wa.me" in link_lower or "whatsapp.com" in link_lower:
            categorized["whatsapp"] = link
        elif any(b in link_lower for b in ["linktr.ee", "beacons.ai"]):
            categorized["linktree_or_similar"].append(link)
        elif any(b in link_lower for b in ["calendly.com", "fresha.com", "treatwell.com", "vagaro.com", "booksy.com", "squareup.com"]):
            categorized["booking_links"].append(link)
        elif "maps.app.goo.gl" in link_lower or "google.com/maps" in link_lower:
            categorized["google_maps"] = link
        elif any(s in link_lower for s in ["facebook.com", "tiktok.com", "youtube.com", "twitter.com"]):
            categorized["social_media"].append(link)
        else:
            categorized["other_websites"].append(link)
            
    return categorized
