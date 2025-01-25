# scraper.py
import requests
from bs4 import BeautifulSoup
import re
import time
from cachetools import TTLCache
from typing import Optional
import logging
from dataclasses import dataclass
from unidecode import unidecode

logger = logging.getLogger(__name__)

@dataclass
class TownInfo:
    """Town information including score and postal code"""
    name: str
    cog_code: str
    postal_code: str
    score: float

class ScraperConfig:
    """Configuration for the web scraper"""
    BASE_URL = "https://www.ville-ideale.fr"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    CACHE_TTL = 3600  # 1 hour
    RATE_LIMIT = 1  # seconds between requests

class TownScraper:
    """Handles scraping of town information"""
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=ScraperConfig.CACHE_TTL)
        self.last_request_time = 0

    def clean_town_name(self, town_name: str) -> str:
        """Clean town name to match URL format"""
        cleaned = unidecode(town_name.lower())
        cleaned = re.sub(r'[^a-z0-9]', '_', cleaned)
        cleaned = re.sub(r'_+', '_', cleaned)
        cleaned = cleaned.strip('_')
        return cleaned

    def parse_french_score(self, score_text: str) -> float:
        """Parse French formatted score"""
        try:
            score_match = re.search(r'(\d+,\d+)', score_text)
            if not score_match:
                raise ValueError(f"Invalid score format: {score_text}")
            return float(score_match.group(1).replace(',', '.'))
        except Exception as e:
            logger.error(f"Error parsing score '{score_text}': {str(e)}")
            raise

    def parse_postal_code(self, header_text: str) -> str:
        """Extract postal code from header text"""
        try:
            postal_match = re.search(r'(\d{5})', header_text)
            if not postal_match:
                raise ValueError(f"No postal code found in: {header_text}")
            return postal_match.group(1)
        except Exception as e:
            logger.error(f"Error parsing postal code from '{header_text}': {str(e)}")
            raise

    def _respect_rate_limit(self):
        """Ensure we respect the rate limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < ScraperConfig.RATE_LIMIT:
            time.sleep(ScraperConfig.RATE_LIMIT - elapsed)
        self.last_request_time = time.time()

    async def get_town_info(self, town_name: str, cog_code: str) -> Optional[TownInfo]:
        """Get information for a specific town"""
        cache_key = f"{town_name}_{cog_code}"

        # Check cache
        if cache_key in self.cache:
            logger.info(f"Returning cached data for {town_name}")
            return self.cache[cache_key]

        try:
            # Respect rate limiting
            self._respect_rate_limit()

            # Clean town name and construct URL
            cleaned_name = self.clean_town_name(town_name)
            url = f"{ScraperConfig.BASE_URL}/{cleaned_name}_{cog_code}"
            logger.info(f"Fetching data from: {url}")

            # Make request
            response = requests.get(url, headers=ScraperConfig.HEADERS, timeout=10)
            response.raise_for_status()

            # Parse response
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract data
            score_elem = soup.find('p', id='ng')
            header_elem = soup.find('h1')

            if not score_elem or not header_elem:
                logger.error(f"Missing elements on page. Score elem: {bool(score_elem)}, Header elem: {bool(header_elem)}")
                return None

            # Parse data
            score = self.parse_french_score(score_elem.text.strip())
            postal_code = self.parse_postal_code(header_elem.text.strip())

            # Create result
            result = TownInfo(
                name=town_name,
                cog_code=cog_code,
                postal_code=postal_code,
                score=score
            )

            # Cache result
            self.cache[cache_key] = result
            logger.info(f"Successfully fetched data for {town_name}")
            return result

        except Exception as e:
            logger.error(f"Error fetching town info for {town_name}: {str(e)}", exc_info=True)
            return None