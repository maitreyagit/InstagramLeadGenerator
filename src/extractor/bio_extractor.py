import re
from typing import Dict, Any

HASHTAG_REGEX = re.compile(r'#\w+')
MENTION_REGEX = re.compile(r'@\w+')
CTA_KEYWORDS = ['book now', 'click here', 'link in bio', 'dm us', 'contact us', 'book below']

def extract_bio_details(bio_text: str) -> Dict[str, Any]:
    if not bio_text:
        return {
            "bio": "",
            "hashtags": [],
            "mentions": [],
            "cta_present": False,
            "services": [], # Typically needs NLP or a predefined list, keeping empty for now unless we match keywords
            "location": ""  # Location is better extracted from Instagram's location fields, but can be NLPed from bio
        }
        
    hashtags = HASHTAG_REGEX.findall(bio_text)
    mentions = MENTION_REGEX.findall(bio_text)
    
    bio_lower = bio_text.lower()
    cta_present = any(cta in bio_lower for cta in CTA_KEYWORDS)
    
    return {
        "bio": bio_text,
        "hashtags": hashtags,
        "mentions": mentions,
        "cta_present": cta_present,
        "services": [], 
        "location": "" 
    }
