import asyncio
import json
import logging
import os
from typing import Dict, Any

from playwright.async_api import async_playwright, Page, Browser, Playwright, expect
from playwright_stealth import Stealth
from .base import BaseScraper
from .proxy_manager import ProxyManager
from src.config.settings import settings

logger = logging.getLogger("instagram_scraper.playwright")

class PlaywrightScraper(BaseScraper):
    def __init__(self):
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.proxy_manager = ProxyManager(settings.proxy_list_file)
        self.auth_file = "auth_state.json"
        
    async def initialize(self, headless=True):
        self.playwright = await async_playwright().start()
        proxy = self.proxy_manager.get_proxy_server_format()
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            proxy=proxy if proxy else None
        )
        logger.info(f"Playwright initialized (headless={headless}).")

    async def perform_login(self):
        """Interactive login to save session."""
        if not self.browser:
            await self.initialize(headless=False)
            
        iphone = self.playwright.devices['iPhone 13']
        context = await self.browser.new_context(**iphone)
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        logger.info("=====================================================")
        logger.info("Please log in to Instagram in the browser window...")
        logger.info("You have 2 minutes to complete the login process.")
        logger.info("=====================================================")
        await page.goto("https://www.instagram.com/accounts/login/")
        
        # Wait for the user to log in and the homepage to load
        try:
            await page.wait_for_selector("svg[aria-label='Home'], svg[aria-label='New post']", timeout=120000)
            logger.info("Login successful! Saving authentication state...")
            await context.storage_state(path=self.auth_file)
            logger.info(f"Saved authentication state to {self.auth_file}")
        except Exception as e:
            logger.error("Login timed out or failed. Did not save state.")
            
        await context.close()

    async def _check_banned(self, page: Page) -> bool:
        """Check if the account is banned or suspended."""
        try:
            url = page.url
            if "login" in url:
                logger.error("Redirected to login page! Session is dead or account is logged out/banned.")
                return True
            if "challenge" in url or "suspended" in url:
                logger.error("Account challenged or suspended by Instagram.")
                return True
                
            title = await page.title()
            if "suspend" in title.lower() or "checkpoint" in title.lower():
                return True
                
            return False
        except Exception:
            return False

    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        if not self.browser:
            await self.initialize()
            
        context_args = {}
        if os.path.exists(self.auth_file):
            context_args["storage_state"] = self.auth_file
            iphone = self.playwright.devices['iPhone 13']
            context_args.update(iphone)
            logger.info("Using mobile emulation and authenticated session.")
        else:
            context_args["user_agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            
        context = await self.browser.new_context(**context_args)
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        extracted_data = {}
        
        async def handle_response(response):
            if "graphql/query" in response.url or "?__a=1" in response.url or "api/v1/users/web_profile_info" in response.url:
                try:
                    json_data = await response.json()
                    if 'data' in json_data and 'user' in json_data['data']:
                        extracted_data.update(json_data['data']['user'])
                except Exception:
                    pass

        page.on("response", handle_response)
        
        url = f"https://www.instagram.com/{username}/"
        logger.info(f"Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=settings.timeout)
            await page.wait_for_timeout(3000)
            
            if await self._check_banned(page):
                logger.error("ACCOUNT APPEARS TO BE BANNED OR SUSPENDED!")
                raise Exception("Account is banned.")
                
            # 1. Dismiss initial popups if any (e.g. "Not Now", "Use the App")
            try:
                not_now = page.locator("text='Not now', text='Not Now', text='Cancel'").first
                if await not_now.is_visible(timeout=1000):
                    await not_now.click()
                    await page.wait_for_timeout(1000)
            except Exception:
                pass
                
            # 2. Click "more" in bio
            try:
                more_btn = page.locator("span:has-text('more'), span:has-text('... more')").first
                if await more_btn.is_visible(timeout=1000):
                    await more_btn.click()
                    await page.wait_for_timeout(1000)
            except Exception:
                pass
                
            # 3. Click external link if present (to open modal)
            try:
                link_btn = page.locator("a[target='_blank'], span:has-text('link'), span:has-text('links')").first
                if await link_btn.is_visible(timeout=1000):
                    await link_btn.click()
                    await page.wait_for_timeout(1500)
            except Exception:
                pass
                
            # 4. Try to click the Contact button to reveal email/phone
            try:
                contact_button = page.locator("button:has-text('Contact'), a:has-text('Contact'), button:has-text('Email'), a:has-text('Email'), div[role='button']:has-text('Email'), div[role='button']:has-text('Contact'), text='Contact', text='Email', text='Contact info'").first
                if await contact_button.is_visible(timeout=1000):
                    logger.info("Found contact button! Clicking...")
                    await contact_button.click()
                    await page.wait_for_timeout(2000)
            except Exception as e:
                logger.debug("No contact button found or failed to click.")
                
            # Extract clean biography from DOM using JS to avoid button texts
            clean_bio = await page.evaluate('''() => {
                let spans = Array.from(document.querySelectorAll('span[dir="auto"], div[dir="auto"]'));
                let possibleBios = spans.map(s => s.innerText.trim()).filter(t => t.length > 20 && !t.includes('Followers') && !t.includes('Following') && !t.includes('See Instagram photos'));
                return possibleBios.length > 0 ? possibleBios[0] : "";
            }''')
            
            # Extract real hidden URLs from <a> tags to avoid truncation
            real_links = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a')).map(a => a.href).filter(h => h && h.startsWith('http') && (!h.includes('instagram.com/') || h.includes('l.instagram.com')));
            }''')
                
            # Grab the entire DOM text for regex extraction (phones/emails ONLY)
            body_text = await page.evaluate("document.body.innerText")
            extracted_data["_raw_dom_text"] = body_text

            if not extracted_data or "edge_followed_by" not in extracted_data:
                # Meta tags extraction
                meta_title = await page.title()
                desc = await page.get_attribute('meta[property="og:description"]', 'content')
                img = await page.get_attribute('meta[property="og:image"]', 'content')
                
                if "username" not in extracted_data:
                    extracted_data["username"] = username
                    extracted_data["full_name"] = meta_title.split('(@')[0].strip() if meta_title and '(@' in meta_title else username
                    extracted_data["profile_pic_url_hd"] = img if img else ""
                    extracted_data["biography"] = clean_bio
                
                if desc:
                    import re
                    followers_match = re.search(r'([\d\.,KMkm]+)\s+Followers', desc)
                    following_match = re.search(r'([\d\.,KMkm]+)\s+Following', desc)
                    posts_match = re.search(r'([\d\.,KMkm]+)\s+Posts', desc)
                    
                    if followers_match:
                        extracted_data['edge_followed_by'] = {'count': followers_match.group(1)}
                    if following_match:
                        extracted_data['edge_follow'] = {'count': following_match.group(1)}
                    if posts_match:
                        extracted_data['edge_owner_to_timeline_media'] = {'count': posts_match.group(1)}
                        
            # Use real links
            if real_links:
                import urllib.parse
                for link in real_links:
                    if 'l.instagram.com/?u=' in link:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
                        if 'u' in parsed:
                            extracted_data['external_url'] = parsed['u'][0]
                            break
                    else:
                        extracted_data['external_url'] = link
                        break
                    
        except Exception as e:
            logger.error(f"Error scraping {username}: {str(e)}")
            raise e
        finally:
            await context.close()
            
        if not extracted_data:
            raise Exception("Could not extract user data from page. Possible block or layout change.")
            
        return extracted_data

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Playwright closed.")
