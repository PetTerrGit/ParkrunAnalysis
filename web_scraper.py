"""
Web Scraping Module
Fetches and parses parkrun results from webpages
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParkrunScraper:
    """Scrapes parkrun results from official parkrun websites"""
    
    # Headers to mimic browser request
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    def __init__(self, timeout: int = 10):
        """
        Initialize ParkrunScraper
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if request fails
        """
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def parse_results_table(self, soup: BeautifulSoup) -> Optional[List[Dict]]:
        """
        Parse results table from parkrun webpage
        
        This is a flexible parser that works with common parkrun page structures.
        Adjust selectors if parkrun changes their HTML structure.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of result dictionaries or None if parsing fails
        """
        results = []
            
        try:
    
            rows = soup.find_all('tr', class_='Results-table-row')

            if not rows:
                logger.warning("Could not find results table")
                return None

            for row in rows:
                # Use .get() to pull data directly from the attributes
                # This avoids navigating the messy <span> and <div> tags inside
                date_str = row.get('data-date')
                first_male = row.get('data-male')
                first_female = row.get('data-female')
                finishers = row.get('data-finishers')
                helpers = row.get('data-volunteers')
                event_number = row.get('data-parkrun')
                male_time = row.get('data-maletime')
                female_time = row.get('data-femaletime')

                date = self._parse_date(date_str)
                          
                
                
                if date and finishers:
                    results.append({
                        'event_number' : event_number,
                        'date': date,
                        'first_male': first_male if first_male else None,
                        'first_female': first_female if first_female else None,
                        'finishers': finishers,
                        'helpers': helpers,
                        'male_time' : male_time,
                        'female_time' : female_time,                 
                    })   
            
            if results:
                logger.info(f"Parsed {len(results)} results")
                return results
            else:
                logger.warning("No results found in table")
                return None
        
        except Exception as e:
            logger.error(f"Error parsing results table: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string in various common formats
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime object or None
        """
        formats = [
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%B %d, %Y',
            '%d %B %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def scrape_event(self, url: str, event_name: str = None) -> Optional[List[Dict]]:
        """
        Scrape a parkrun event results page
        
        Args:
            url: URL of the results page
            event_name: Name of the event (for logging)
            
        Returns:
            List of result dictionaries or None if scraping fails
        """
        display_name = event_name or urlparse(url).netloc
        logger.info(f"Scraping {display_name}...")
        
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        results = self.parse_results_table(soup)
        return results
    
    def scrape_multiple_events(self, urls: Dict[str, str]) -> Dict[str, Optional[List[Dict]]]:
        """
        Scrape multiple parkrun events
        
        Args:
            urls: Dictionary with event names as keys and URLs as values
            
        Returns:
            Dictionary with event names as keys and result lists as values
        """
        all_results = {}
        
        for event_name, url in urls.items():
            results = self.scrape_event(url, event_name)
            all_results[event_name] = results
        
        return all_results


class ParkrunURLBuilder:
    """Helper class to build parkrun URLs"""
    
    BASE_URL = "https://{country}.parkrun.com/{event_name}/results"
    
    @staticmethod
    def build_url(event_name: str, country: str = 'uk') -> str:
        """
        Build parkrun results URL
        
        Args:
            event_name: Name of the parkrun event (typically lowercase, dashes)
            country: Country code (default: uk)
            
        Returns:
            Full URL
        """
        return ParkrunURLBuilder.BASE_URL.format(
            country=country,
            event_name=event_name
        )


if __name__ == "__main__":
    # Example usage
    scraper = ParkrunScraper()
    
    # Example: Windsor parkrun (UK)
    # url = ParkrunURLBuilder.build_url('stadtparkgraz', 'at')
    url = "https://www.parkrun.co.at/stadtparkgraz/results/eventhistory/"
    results = scraper.scrape_event(url, 'Stadtpark Graz')
    
    if results:
        print(f"Found {len(results)} records")
        for r in results[:3]:
            print(r)
