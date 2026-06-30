from typing import List, Dict, Any
from playwright.async_api import BrowserContext, async_playwright
from bs4 import BeautifulSoup
import asyncio
import logging
from backend.scrapers.base import BaseScraper, JobResult
from backend.config import config_manager
from backend.services.captcha_detector import captcha_detector, CaptchaDetectedException

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    source_name = "LinkedIn"

    async def scrape(self, context: BrowserContext, keyword: str) -> List[Dict[str, Any]]:
        self.diagnostics["start_time"] = asyncio.get_event_loop().time()
        jobs: List[Dict[str, Any]] = []

        config = config_manager.get_config()

        try:
            logger.info("Using public unauthenticated LinkedIn scraping.")
            page = await context.new_page()
            url = f"https://www.linkedin.com/jobs/search?keywords={keyword}"
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(config.delay_between_requests)

            content = await page.content()
            
            if captcha_detector.detect_html(content):
                raise CaptchaDetectedException(self.source_name)
                
            jobs = self._parse_jobs(content, config.max_jobs_per_keyword)
            await page.close()

        except Exception as e:
            if "Timeout" in str(e):
                self.diagnostics["rate_limited"] = True
            self._record_error(e)
        finally:
            self.diagnostics["end_time"] = asyncio.get_event_loop().time()

        return jobs

    def _parse_jobs(self, html_content: str, max_jobs: int) -> List[Dict[str, Any]]:
        jobs = []
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.select(".job-search-card") or soup.select(".jobs-search-results__list-item")

        for card in job_cards[:max_jobs]:
            title_elem = card.select_one(".base-search-card__title") or card.select_one(".job-card-list__title")
            company_elem = card.select_one(".base-search-card__subtitle") or card.select_one(".job-card-container__company-name")
            location_elem = card.select_one(".job-search-card__location") or card.select_one(".job-card-container__metadata-item")
            url_elem = card.select_one(".base-card__full-link") or card.select_one(".job-card-container__link")

            if not title_elem or not url_elem:
                continue

            job = JobResult(
                title=title_elem.text.strip(),
                company=company_elem.text.strip() if company_elem else "Unknown",
                location=location_elem.text.strip() if location_elem else "Unknown",
                job_url=url_elem.get("href", "").split("?")[0]
            )
            job.source = self.source_name
            jobs.append(job.to_dict())
            self.diagnostics["jobs_found"] += 1

        return jobs
