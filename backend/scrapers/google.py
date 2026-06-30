from typing import List, Dict, Any
from urllib.parse import quote_plus
from playwright.async_api import BrowserContext
from bs4 import BeautifulSoup
import asyncio
import logging
from backend.scrapers.base import BaseScraper, JobResult
from backend.config import config_manager
from backend.services.captcha_detector import captcha_detector, CaptchaDetectedException

logger = logging.getLogger(__name__)


class GoogleScraper(BaseScraper):
    """
    Searches Google using a site: filter to find job postings
    on specific platforms (Lever, Greenhouse, Ashby).
    """
    site_filter: str = ""  # e.g. "site:jobs.lever.co"

    async def scrape(self, context: BrowserContext, keyword: str) -> List[Dict[str, Any]]:
        self.diagnostics["start_time"] = asyncio.get_event_loop().time()
        jobs: List[Dict[str, Any]] = []
        config = config_manager.get_config()
        page = await context.new_page()

        # Set a realistic user-agent to reduce bot detection
        await page.set_extra_http_headers({
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        })

        try:
            query = quote_plus(f'{self.site_filter} "{keyword}"')
            url = f"https://www.google.com/search?q={query}&num=30&hl=en"

            for page_num in range(config.max_pages_per_source):
                logger.info(f"[{self.source_name}] Google search page {page_num + 1} for '{keyword}'")

                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(1.5)  # Brief pause to appear human

                content = await page.content()

                # Detect CAPTCHA / bot challenge
                if captcha_detector.detect_html(content) or "detected unusual traffic" in content.lower():
                    raise CaptchaDetectedException(self.source_name)

                soup = BeautifulSoup(content, "html.parser")

                # Google result containers
                result_divs = soup.select("div.g") or soup.select("div[data-sokoban-container]")

                if not result_divs:
                    logger.warning(f"[{self.source_name}] No results found on page {page_num + 1}. Google may have changed its structure.")
                    break

                for div in result_divs:
                    # Extract title and URL
                    a_tag = div.select_one("a[href]")
                    h3_tag = div.select_one("h3")
                    snippet_tag = div.select_one("div[data-sncf='1']") or div.select_one(".VwiC3b") or div.select_one("span.aCOpRe")

                    if not a_tag or not h3_tag:
                        continue

                    job_url = a_tag.get("href", "")

                    # Filter out non-job URLs (Google ads, trackers, etc.)
                    if not job_url.startswith("http") or "google.com" in job_url:
                        continue

                    # Only keep URLs from the target site
                    site_domain = self.site_filter.replace("site:", "")
                    if site_domain not in job_url:
                        continue

                    title = h3_tag.get_text(strip=True)
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    job = JobResult(
                        title=title,
                        company="Unknown",
                        location="",
                        job_url=job_url,
                    )
                    job.description = snippet
                    job.source = self.source_name
                    jobs.append(job.to_dict())
                    self.diagnostics["jobs_found"] += 1

                    if len(jobs) >= config.max_jobs_per_keyword:
                        break

                if len(jobs) >= config.max_jobs_per_keyword:
                    break

                # Navigate to the next Google page
                next_link = soup.select_one("a#pnnext") or soup.select_one("a[aria-label='Next page']")
                if next_link and next_link.get("href"):
                    url = f"https://www.google.com{next_link['href']}"
                    await asyncio.sleep(config.delay_between_requests)
                else:
                    break

        except CaptchaDetectedException:
            raise
        except Exception as e:
            self._record_error(e)
        finally:
            await page.close()
            self.diagnostics["end_time"] = asyncio.get_event_loop().time()

        logger.info(f"[{self.source_name}] Found {len(jobs)} jobs for '{keyword}'")
        return jobs


class LeverScraper(GoogleScraper):
    source_name = "lever"
    site_filter = "site:jobs.lever.co"


class GreenhouseScraper(GoogleScraper):
    source_name = "greenhouse"
    site_filter = "site:boards.greenhouse.io"


class AshbyScraper(GoogleScraper):
    source_name = "ashby"
    site_filter = "site:jobs.ashbyhq.com"
