import datetime
from typing import Dict, Any

# Social media domains that should never appear in the 'website' column.
# These eat up the website slot without being the business's actual website.
SOCIAL_MEDIA_DOMAINS = [
    "facebook.com", "fb.com", "fb.me",
    "instagram.com",
    "twitter.com", "x.com",
    "tiktok.com",
    "youtube.com", "youtu.be",
    "linkedin.com",
    "snapchat.com",
    "pinterest.com",
]

def _is_social_media_link(url: str) -> bool:
    """Returns True if the URL belongs to a known social media platform."""
    if not url:
        return False
    url_lower = url.lower()
    return any(domain in url_lower for domain in SOCIAL_MEDIA_DOMAINS)

def parse_instagram_profile(raw_data: Dict[str, Any], extracted_bio: Dict[str, Any], extracted_links: Dict[str, Any], extracted_emails: list, extracted_phones: list) -> Dict[str, Any]:
    """
    Parses raw instagram user object and combines with extracted data to match output spec.
    """
    # Defensive gets since Instagram JSON structure can vary
    username = raw_data.get('username', '')
    
    # Combine bio with extracted phone/email if requested
    base_bio = extracted_bio.get("bio", "")
    final_email = raw_data.get('business_email', '') or (extracted_emails[0] if extracted_emails else "")
    final_phone = raw_data.get('business_phone_number', '') or (extracted_phones[0] if extracted_phones else "")
    
    bio_parts = [base_bio]
    if final_phone:
        bio_parts.append(final_phone)
    if final_email:
        bio_parts.append(final_email)
        
    return {
        "username": username,
        "profile_url": f"https://www.instagram.com/{username}/" if username else "",
        "full_name": raw_data.get('full_name', ''),
        "bio": "\t".join(bio_parts),
        "category": raw_data.get('category_name', ''),
        "website": raw_data.get('external_url', '') if not _is_social_media_link(raw_data.get('external_url', '')) else "",
        "email": final_email,
        "phone": final_phone,
        "whatsapp": extracted_links.get("whatsapp", ""),
        "address": raw_data.get('business_address_json', ''), # Can be parsed further if exists
        "followers": raw_data.get('edge_followed_by', {}).get('count', ''),
        "following": raw_data.get('edge_follow', {}).get('count', ''),
        "posts": raw_data.get('edge_owner_to_timeline_media', {}).get('count', ''),
        "is_verified": raw_data.get('is_verified', False),
        "is_private": raw_data.get('is_private', False),
        "business_account": raw_data.get('is_business_account', False),
        "profile_picture_url": raw_data.get('profile_pic_url_hd', '') or raw_data.get('profile_pic_url', ''),
        "external_links": extracted_links.get("other_websites", []) + extracted_links.get("booking_links", []) + extracted_links.get("linktree_or_similar", []),
        "highlights_count": raw_data.get('highlight_reel_count', ''),
        "scraped_at": datetime.datetime.utcnow().isoformat(),
        "status": "success"
    }

def get_failed_profile(username_or_url: str, error_message: str) -> Dict[str, Any]:
    """
    Returns a structured dictionary for a failed profile.
    """
    from src.utils.normalizer import normalize_to_username
    username = normalize_to_username(username_or_url)
    return {
        "username": username,
        "profile_url": f"https://www.instagram.com/{username}/",
        "full_name": "",
        "bio": "",
        "category": "",
        "website": "",
        "email": "",
        "phone": "",
        "whatsapp": "",
        "address": "",
        "followers": "",
        "following": "",
        "posts": "",
        "is_verified": "",
        "is_private": "",
        "business_account": "",
        "profile_picture_url": "",
        "external_links": [],
        "highlights_count": "",
        "scraped_at": datetime.datetime.utcnow().isoformat(),
        "status": "failed",
        "error_message": error_message
    }
