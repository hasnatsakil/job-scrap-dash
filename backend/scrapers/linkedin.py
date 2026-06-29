from typing import List, Dict, Any
from playwright.async_api import BrowserContext, async_playwright
from bs4 import BeautifulSoup
import asyncio
import logging
from backend.scrapers.base import BaseScraper, JobResult
from backend.config import config_manager
from backend.services.connection_manager import connection_manager
from backend.services.session_storage import session_storage

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    source_name = "LinkedIn"

    async def scrape(self, context: BrowserContext, keyword: str) -> List[Dict[str, Any]]:
        self.diagnostics["start_time"] = asyncio.get_event_loop().time()
        jobs: List[Dict[str, Any]] = []

        config = config_manager.get_config()

        # Check Connection Manager to see if we have an authenticated session
        connector = connection_manager.get_connector("linkedin")
        use_auth = False

        if connector and connector.is_connected and not connector.is_expired:
            logger.info("Using ConnectionManager Authenticated LinkedIn session.")
            use_auth = True

        try:
            if use_auth:
                # We need to launch a new context with the stored state, so we ignore the incoming `context`
                state = session_storage.load("linkedin")
                if state:
                    state.pop("_meta", None) # remove our custom meta before passing to playwright

                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    auth_context = await browser.new_context(storage_state=state)
                    page = await auth_context.new_page()

                    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
                    await page.goto(url, wait_until="domcontentloaded")
                    await asyncio.sleep(config.delay_between_requests)

                    content = await page.content()
                    jobs = self._parse_jobs(content, config.max_jobs_per_keyword)

                    await browser.close()
            else:
                # Fallback to public X-Ray style search using the incoming unauthenticated context
                logger.info("Using public unauthenticated LinkedIn scraping.")
                page = await context.new_page()
                url = f"https://www.linkedin.com/jobs/search?keywords={keyword}"
                await page.goto(url, wait_until="domcontentloaded")
                await asyncio.sleep(config.delay_between_requests)

                content = await page.content()
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
