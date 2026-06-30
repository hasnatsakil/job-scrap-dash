import asyncio
import logging
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from playwright.async_api import BrowserContext

logger = logging.getLogger(__name__)

class JobHydrator:
    def __init__(self, concurrency_limit: int = 3):
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    def _needs_hydration(self, job: Dict[str, Any]) -> bool:
        # Smart Mode: Hydrate if description is missing/short, or work_type is missing
        desc = job.get("description", "")
        if not desc or len(desc) < 150:
            return True
        if not job.get("work_type"):
            return True
        return False

    async def hydrate_job(self, context: BrowserContext, job: Dict[str, Any]) -> Dict[str, Any]:
        if not self._needs_hydration(job):
            return job

        job_url = job.get("job_url")
        if not job_url:
            return job

        logger.info(f"Hydrating job: {job.get('title')} - {job_url}")
        
        page = None
        try:
            # Limit concurrent requests
            async with self.semaphore:
                page = await context.new_page()
                # Use a reasonable timeout so one bad page doesn't hang the whole process
                await page.goto(job_url, wait_until="domcontentloaded", timeout=20000)
                
                # Small wait for dynamic content to render (especially for ATS platforms)
                await asyncio.sleep(2)

                content = await page.content()
                job["raw_html"] = content

        except Exception as e:
            logger.warning(f"Hydration failed for {job_url}: {e}. Returning original job.")
        finally:
            if page and not page.is_closed():
                await page.close()
                
        return job

    async def hydrate_batch(self, context: BrowserContext, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not jobs:
            return []
        
        logger.info(f"Starting hydration for {len(jobs)} jobs...")
        tasks = [self.hydrate_job(context, job) for job in jobs]
        
        # We use asyncio.gather, and if an individual task fails, we catch it inside hydrate_job
        # so it won't kill the gather.
        hydrated_jobs = await asyncio.gather(*tasks, return_exceptions=False)
        return list(hydrated_jobs)

job_hydrator = JobHydrator()
