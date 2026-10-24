import sqlite3
import os
import logging
from typing import Optional

logger = logging.getLogger("instagram_scraper.cache")

class ScrapeCache:
    def __init__(self, db_path: str = "scraper_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scraped_profiles (
                        username TEXT PRIMARY KEY,
                        status TEXT,
                        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize cache DB: {e}")

    def is_cached(self, username: str) -> bool:
        """Check if a profile was successfully scraped recently."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT status FROM scraped_profiles WHERE username = ?', (username,))
                row = cursor.fetchone()
                if row and row[0] == 'success':
                    return True
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
        return False

    def mark_scraped(self, username: str, status: str = "success"):
        """Mark a profile as scraped."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO scraped_profiles (username, status, scraped_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (username, status))
                conn.commit()
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")
