import re
from urllib.parse import urlparse

def normalize_to_username(input_str: str) -> str:
    """
    Normalizes an input string (either a URL or a username) to a plain username.
    """
    input_str = input_str.strip()
    
    # If it's a URL
    if input_str.startswith("http://") or input_str.startswith("https://") or "instagram.com" in input_str:
        # Ensure it has scheme for urlparse
        if not input_str.startswith("http"):
            input_str = "https://" + input_str
            
        parsed = urlparse(input_str)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        if path_parts:
            # Username is typically the first part of the path
            return path_parts[0]
            
    # If it's just a username, strip '@' if present
    if input_str.startswith("@"):
        return input_str[1:]
        
    return input_str

def build_profile_url(username: str) -> str:
    """
    Builds the standard instagram profile URL from a username.
    """
    return f"https://www.instagram.com/{username}/"
