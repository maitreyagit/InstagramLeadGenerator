from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseScraper(ABC):
    
    @abstractmethod
    async def initialize(self):
        """Initialize browser/session"""
        pass

    @abstractmethod
    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        """Scrape profile data for a given username"""
        pass
        
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
