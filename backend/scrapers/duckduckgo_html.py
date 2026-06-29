from typing import List, Dict, Any
from urllib.parse import quote_plus
from playwright.async_api import BrowserContext
from bs4 import BeautifulSoup
import asyncio, logging
from backend.scrapers.base import BaseScraper, JobResult
from backend.config import config_manager

logger = logging.getLogger(__name__)

class DuckDuckGoHTMLScraper(BaseScraper):
    site_query: str = ""
    async def scrape(self, context: BrowserContext, keyword: str) -> List[Dict[str, Any]]:
        self.diagnostics["start_time"] = asyncio.get_event_loop().time()
        jobs: List[Dict[str, Any]] = []
        page = await context.new_page()
        config = config_manager.get_config()
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(f'{self.site_query} \"{keyword}\"')}"
            for p in range(config.max_pages_per_source):
                await page.goto(url, wait_until="domcontentloaded")
                soup = BeautifulSoup(await page.content(), "html.parser")
                results = soup.select(".result__body")
                if not results: break
                for result in results:
                    title_elem, snippet_elem = result.select_one(".result__title .result__a"), result.select_one(".result__snippet")
                    if not title_elem: continue
                    job = JobResult(title=title_elem.text.strip(), company="Unknown", location="", job_url=title_elem.get("href", ""))
                    job.description = snippet_elem.text.strip() if snippet_elem else ""
                    job.source = self.source_name
                    jobs.append(job.to_dict())
                    self.diagnostics["jobs_found"] += 1
                    if len(jobs) >= config.max_jobs_per_keyword: break
                if len(jobs) >= config.max_jobs_per_keyword: break
                next_btn = soup.select_one(".nav-link")
                if next_btn and "Next" in next_btn.text:
                    url = f"https://html.duckduckgo.com{next_btn['href']}"
                    await asyncio.sleep(config.delay_between_requests)
                else: break
        except Exception as e: self._record_error(e)
        finally:
            await page.close()
            self.diagnostics["end_time"] = asyncio.get_event_loop().time()
        return jobs

class LeverScraper(DuckDuckGoHTMLScraper): source_name, site_query = "Lever", "site:jobs.lever.co"
class GreenhouseScraper(DuckDuckGoHTMLScraper): source_name, site_query = "Greenhouse", "site:boards.greenhouse.io"
class AshbyScraper(DuckDuckGoHTMLScraper): source_name, site_query = "Ashby", "site:jobs.ashbyhq.com"
