import asyncio
import logging
import random
from typing import List, Dict, Any
from tqdm.asyncio import tqdm

from src.utils.normalizer import normalize_to_username
from src.scraper.instagrapi_scraper import InstagrapiScraper
from src.parser.profile_parser import parse_instagram_profile, get_failed_profile
from src.extractor.contact_extractor import extract_emails, extract_phones, categorize_links
from src.extractor.bio_extractor import extract_bio_details
from src.export.cache import ScrapeCache
from src.config.settings import settings

logger = logging.getLogger("instagram_scraper.bulk")

class BulkProcessor:
    def __init__(self):
        self.scraper = InstagrapiScraper()
        self.cache = ScrapeCache()
        self.semaphore = asyncio.Semaphore(settings.concurrency)
        
    async def process_single(self, raw_input: str, retries: int = settings.retries) -> Dict[str, Any]:
        username = normalize_to_username(raw_input)
        
        if self.cache.is_cached(username):
            logger.info(f"Skipping {username}, already cached as success.")
            # For a real system, we might want to return the cached data instead of None
            # But for simplicity, we return a cached indicator
            return {"username": username, "status": "cached"}
            
        async with self.semaphore:
            # Pacing to avoid getting banned
            delay = random.uniform(settings.min_delay, settings.max_delay)
            logger.info(f"Pacing delay: waiting {delay:.2f}s before scraping {username}")
            await asyncio.sleep(delay)
            
            for attempt in range(retries):
                try:
                    logger.info(f"Scraping {username} (Attempt {attempt + 1}/{retries})")
                    raw_data = await self.scraper.scrape_profile(username)
                    
                    # Parse and extract
                    bio_text = raw_data.get('biography', '')
                    external_url = raw_data.get('external_url', '')
                    
                    extracted_bio = extract_bio_details(bio_text)
                    
                    # Combine all text for contact extraction
                    all_text = f"{bio_text} {external_url}"
                    emails = extract_emails(all_text)
                    phones = extract_phones(all_text)
                    
                    # Links to categorize
                    links_to_check = []
                    if external_url:
                        links_to_check.append(external_url)
                        
                    # external_url_linkshimmed might also exist, but external_url is the original
                    categorized_links = categorize_links(links_to_check)
                    
                    structured_data = parse_instagram_profile(
                        raw_data, extracted_bio, categorized_links, emails, phones
                    )
                    
                    self.cache.mark_scraped(username, "success")
                    return structured_data
                    
                except Exception as e:
                    logger.warning(f"Failed to scrape {username} on attempt {attempt + 1}: {e}")
                    if attempt == retries - 1:
                        self.cache.mark_scraped(username, "failed")
                        return get_failed_profile(username, str(e))
                    await asyncio.sleep(2 ** attempt) # Exponential backoff

    async def process_bulk(self, inputs: List[str]) -> List[Dict[str, Any]]:
        await self.scraper.initialize()
        
        results = []
        try:
            tasks = [self.process_single(inp) for inp in inputs]
            for f in tqdm.as_completed(tasks, total=len(inputs), desc="Processing Profiles"):
                res = await f
                if res:
                    results.append(res)
        finally:
            await self.scraper.close()
            
        return results
