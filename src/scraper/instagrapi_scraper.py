import logging
import os
import random
import time
from typing import Dict, Any

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from .base import BaseScraper
from .proxy_manager import ProxyManager
from src.config.settings import settings

logger = logging.getLogger("instagram_scraper.instagrapi")

class InstagrapiScraper(BaseScraper):
    def __init__(self):
        self.client = Client()
        self.proxy_manager = ProxyManager(settings.proxy_list_file)
        self.auth_file = "auth_state.json"
        
        # Configure proxy if available
        proxy = self.proxy_manager.get_proxy_server_format()
        if proxy:
            # instagrapi expects proxy in URL format: http://username:password@ip:port
            if "http://" not in proxy and "socks5://" not in proxy:
                proxy = f"http://{proxy}"
            self.client.set_proxy(proxy)
            logger.info(f"Configured instagrapi with proxy: {proxy}")

    async def initialize(self):
        """Load session if exists."""
        if os.path.exists(self.auth_file):
            try:
                self.client.load_settings(self.auth_file)
                logger.info(f"Loaded session from {self.auth_file}")
            except Exception as e:
                logger.error(f"Failed to load auth settings: {e}")
        else:
            logger.warning("No auth_state.json found. You must login first using --login.")

    async def perform_login_with_session(self, sessionid: str):
        """Login via sessionid cookie - bypasses IP-based login blocks."""
        try:
            logger.info("Attempting session cookie login...")
            
            # instagrapi can set a session by directly injecting cookies
            # We need the username too - we can fetch it from the API after setting the session
            self.client.set_settings({
                "cookies": {"sessionid": sessionid},
            })
            
            # Verify session works by fetching our own account info
            account = self.client.account_info()
            username = account.username
            
            # Now dump the full working settings
            self.client.dump_settings(self.auth_file)
            logger.info(f"Session login successful as @{username}! Saved to {self.auth_file}.")
            print(f"\n[✓] Login successful! Authenticated as @{username}.")
            print(f"[✓] Session saved to {self.auth_file}. You won't need to login again.")
            return True

        except Exception as e:
            logger.error(f"Session login failed: {e}")
            print(f"\n[!] Session login failed. Error: {e}")
            print("[!] Make sure your sessionid cookie is correct and not expired.")
            print("[!] Try logging out and back into Instagram on Chrome and copy the new sessionid.")
            return False

    async def perform_login(self, username, password):
        """Interactive login for CLI (kept as fallback)."""
        try:
            logger.info(f"Attempting login for {username}...")
            time.sleep(random.uniform(2, 4))
            result = self.client.login(username, password)
            if result:
                self.client.dump_settings(self.auth_file)
                logger.info(f"Login successful! Session saved to {self.auth_file}")
                return True
            return False
        except ChallengeRequired as e:
            logger.error(f"Challenge required! You may need to verify your account via email/SMS. {e}")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            print(f"\n[!] Login failed. Error: {e}")
            print("[!] If you are sure your password is correct, Instagram may be blocking your IP.")
            print("[!] Try logging in via your phone on the same WiFi to clear the block, or use a Proxy.")
            return False

    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        """Scrape profile using Instagram Private Mobile API."""
        try:
            logger.info(f"Fetching data for @{username} via mobile API...")
            user = self.client.user_info_by_username(username)
            data = user.model_dump() if hasattr(user, 'model_dump') else user.dict()
            
            # Warn about private accounts — we can still get metadata but not contact info
            if data.get('is_private'):
                logger.warning(f"@{username} is a private account. Contact info may not be available.")

            # Build address string from structured location data
            address_json = data.get('address_street', '')
            city = data.get('city_name', '')
            zip_code = data.get('zip', '')
            address_parts = [p for p in [address_json, city, zip_code] if p]
            full_address = ', '.join(address_parts)

            extracted_data = {
                "username":                     data.get("username", username),
                "full_name":                    data.get("full_name", ""),
                "biography":                    data.get("biography", ""),
                "external_url":                 str(data.get("external_url", "") or ""),
                "category_name":                data.get("category_name", ""),
                "business_email":               data.get("public_email", ""),
                "business_phone_number":        data.get("contact_phone_number", ""),
                "business_address_json":        full_address,
                "is_verified":                  data.get("is_verified", False),
                "is_private":                   data.get("is_private", False),
                "is_business_account":          data.get("is_business", False),
                "highlight_reel_count":         data.get("highlight_reel_count", 0),
                "edge_followed_by":             {"count": data.get("follower_count", 0)},
                "edge_follow":                  {"count": data.get("following_count", 0)},
                "edge_owner_to_timeline_media": {"count": data.get("media_count", 0)},
                "profile_pic_url_hd":           str(data.get("profile_pic_url_hd", "") or ""),
            }
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error scraping @{username}: {str(e)}")
            raise e

    async def close(self):
        """No browser to close."""
        pass
