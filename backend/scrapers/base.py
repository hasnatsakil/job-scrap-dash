import logging
from typing import List, Dict, Any
from datetime import datetime
from playwright.async_api import BrowserContext

logger = logging.getLogger(__name__)

class JobResult:
    def __init__(self, title: str, company: str, location: str, job_url: str):
        self.title, self.company, self.location, self.job_url = title, company, location, job_url
        self.work_type, self.employment_type, self.salary, self.experience, self.source, self.description, self.posted_date = "", "", "", "", "", "", ""
        self.scraped_date = datetime.now().isoformat()
    def to_dict(self) -> Dict[str, Any]: return self.__dict__

class BaseScraper:
    source_name: str = "Base"
    def __init__(self):
        self.diagnostics = {"jobs_found": 0, "jobs_accepted": 0, "jobs_rejected": 0, "errors": 0, "retry_count": 0, "rate_limited": False, "start_time": None, "end_time": None}
    async def scrape(self, context: BrowserContext, keyword: str) -> List[Dict[str, Any]]: raise NotImplementedError
    def _record_error(self, error: Exception):
        logger.error(f"Scraper {self.source_name} error: {error}")
        self.diagnostics["errors"] += 1
