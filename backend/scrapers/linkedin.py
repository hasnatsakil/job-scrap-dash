from typing import List, Dict, Any
from playwright.async_api import BrowserContext
from bs4 import BeautifulSoup
import asyncio, logging
from backend.scrapers.base import BaseScraper, JobResult
from backend.config import config_manager, env_settings

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    source_name = "LinkedIn"
    async def scrape(self, context: BrowserContext, keyword: str) -> List[Dict[str, Any]]:
        self.diagnostics["start_time"] = asyncio.get_event_loop().time()
        jobs: List[Dict[str, Any]] = []
        page = await context.new_page()
        config = config_manager.get_config()
        try:
            if env_settings.linkedin_li_at_cookie:
                await context.add_cookies([{"name": "li_at", "value": env_settings.linkedin_li_at_cookie, "domain": ".linkedin.com", "path": "/"}])
                url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
            else:
                url = f"https://www.linkedin.com/jobs/search?keywords={keyword}"
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(config.delay_between_requests)
            job_cards = (BeautifulSoup(await page.content(), "html.parser")).select(".job-search-card") or (BeautifulSoup(await page.content(), "html.parser")).select(".jobs-search-results__list-item")
            for card in job_cards[:config.max_jobs_per_keyword]:
                title_elem = card.select_one(".base-search-card__title") or card.select_one(".job-card-list__title")
                company_elem = card.select_one(".base-search-card__subtitle") or card.select_one(".job-card-container__company-name")
                location_elem = card.select_one(".job-search-card__location") or card.select_one(".job-card-container__metadata-item")
                url_elem = card.select_one(".base-card__full-link") or card.select_one(".job-card-container__link")
                if not title_elem or not url_elem: continue
                job = JobResult(title=title_elem.text.strip(), company=company_elem.text.strip() if company_elem else "Unknown", location=location_elem.text.strip() if location_elem else "Unknown", job_url=url_elem.get("href", "").split("?")[0])
                job.source = self.source_name
                jobs.append(job.to_dict())
                self.diagnostics["jobs_found"] += 1
        except Exception as e:
            if "Timeout" in str(e): self.diagnostics["rate_limited"] = True
            self._record_error(e)
        finally:
            await page.close()
            self.diagnostics["end_time"] = asyncio.get_event_loop().time()
        return jobs
