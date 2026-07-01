import asyncio
import logging
import urllib.parse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import List, Dict, Any
from backend.apis.base import BaseJobAPI

logger = logging.getLogger(__name__)

class GoogleScraperAPI(BaseJobAPI):
    """
    A unified fallback scraper that uses Google Search with site: operators
    to find jobs from platforms like LinkedIn and Glassdoor without requiring
    platform-specific API keys or logins.
    """
    
    def __init__(self, platform: str):
        self.platform = platform # e.g., "linkedin" or "glassdoor"
        
    async def fetch_jobs(self, keyword: str, location: str, limit: int = 15) -> List[Dict[str, Any]]:
        query = f'site:{self.platform}.com/jobs "{keyword}" "{location}"'
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        
        logger.info(f"Google Scraper hitting: {search_url}")
        
        jobs = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                # Wait briefly for results to render
                try:
                    await page.wait_for_selector("div.g", timeout=5000)
                except Exception:
                    logger.warning(f"No results or timeout waiting for div.g on Google for {self.platform}")
                    
                content = await page.content()
                await browser.close()
                
                soup = BeautifulSoup(content, "html.parser")
                results = soup.select("div.g")
                
                for res in results[:limit]:
                    title_elem = res.select_one("h3")
                    link_elem = res.select_one("a")
                    snippet_elem = res.select_one("div.VwiC3b")
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get("href", "")
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        # Attempt to extract company name from title or snippet if possible
                        # "Software Engineer - Google - LinkedIn" -> Company: Google
                        parts = title.split(" - ")
                        company = "Unknown"
                        clean_title = title
                        
                        if len(parts) >= 3:
                            company = parts[1].strip()
                            clean_title = parts[0].strip()
                        elif len(parts) >= 2:
                            clean_title = parts[0].strip()
                            # if it ends with " - LinkedIn", it's just platform
                            if "linkedin" not in parts[1].lower() and "glassdoor" not in parts[1].lower():
                                company = parts[1].strip()
                                
                        jobs.append({
                            "title": clean_title,
                            "company": company,
                            "location": location,
                            "job_url": url,
                            "description": snippet, # Pass snippet as description for AI to evaluate
                            "salary": "Not provided",
                            "source": self.platform
                        })
                        
        except Exception as e:
            logger.error(f"Error in GoogleScraper for {self.platform}: {e}")
            
        return jobs

# Factories for the registry
def LinkedInScraper():
    return GoogleScraperAPI("linkedin")

def GlassdoorScraper():
    return GoogleScraperAPI("glassdoor")
