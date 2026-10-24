import re
import emoji
import phonenumbers

def clean_phone_number(phone_str: str, default_region: str = "US") -> str:
    """
    Attempts to parse and format a phone number to E.164 international format.
    Returns the original string if parsing fails.
    """
    if not phone_str:
        return ""
    try:
        parsed = phonenumbers.parse(phone_str, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass
    return phone_str.strip()

def clean_whitespace(text: str) -> str:
    """
    Removes extra whitespace and newlines from a string.
    """
    if not text:
        return ""
    # Replace multiple newlines or spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_emojis(text: str) -> str:
    """
    Removes emojis from text.
    """
    if not text:
        return ""
    return emoji.replace_emoji(text, replace="")

def clean_url(url: str) -> str:
    """
    Basic cleanup of URLs to remove query parameters that might be tracking.
    """
    if not url:
        return ""
    url = url.strip()
    # E.g., remove utm_source, etc. simple approach: just split by ? if we don't care about query params
    # But some URLs need query params (like youtube). So we'll just return stripped for now.
    return url
