import argparse
import asyncio
import os
import sys
import pandas as pd

from src.scraper.bulk_processor import BulkProcessor
from src.export.exporter import Exporter
from src.config.settings import settings
import src.utils.logger as log_setup

logger = log_setup.logger

def read_inputs(target: str) -> list:
    inputs = []
    if os.path.isfile(target):
        if target.lower().endswith('.xlsx'):
            try:
                df = pd.read_excel(target, header=None)
                # Assuming leads are in the first column
                inputs = df[0].dropna().astype(str).str.strip().tolist()
            except Exception as e:
                logger.error(f"Error reading Excel file: {e}")
        elif target.lower().endswith('.csv'):
            try:
                df = pd.read_csv(target, header=None)
                inputs = df[0].dropna().astype(str).str.strip().tolist()
            except Exception as e:
                logger.error(f"Error reading CSV file: {e}")
        else:
            with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.strip():
                        inputs.append(line.strip())
    else:
        # Single username or URL
        inputs.append(target)
    return inputs

async def run_cli(target: str):
    logger.info("Starting Scraper CLI")
    inputs = read_inputs(target)
    logger.info(f"Loaded {len(inputs)} targets.")
    
    processor = BulkProcessor()
    results = await processor.process_bulk(inputs)
    
    # Filter out cached items that weren't fully returned (if returning just status)
    data_to_export = [r for r in results if r.get('status') != 'cached']
    
    if data_to_export:
        exporter = Exporter(settings.output_folder)
        filename = "scraper_results"
        exporter.export(data_to_export, filename, settings.export_format)
    else:
        logger.info("No new data to export.")

async def perform_auth_flow():
    from src.scraper.instagrapi_scraper import InstagrapiScraper
    print("=========================================")
    print("Instagram Private API Login via Session Cookie")
    print("This method bypasses IP blocks safely.")
    print("=========================================")
    print("How to get your sessionid:")
    print("1. Log into instagram.com on Chrome/Edge.")
    print("2. Right-click anywhere -> Inspect -> Application tab.")
    print("3. Expand Cookies -> https://www.instagram.com.")
    print("4. Find the cookie named 'sessionid' and copy its Value.")
    print("=========================================")
    sessionid = input("Paste your sessionid here: ").strip()
    
    scraper = InstagrapiScraper()
    await scraper.perform_login_with_session(sessionid)

def main():
    parser = argparse.ArgumentParser(description="Instagram Profile Scraper & Data Extractor")
    parser.add_argument("target", nargs='?', help="Instagram username, URL, or path to a CSV/TXT file with usernames/URLs")
    parser.add_argument("--login", action="store_true", help="Launch a visible browser to log in and save authentication state")
    args = parser.parse_args()
    
    # Windows specific fix for asyncio and Playwright
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    if args.login:
        asyncio.run(perform_auth_flow())
    elif args.target:
        asyncio.run(run_cli(args.target))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
