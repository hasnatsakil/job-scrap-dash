import asyncio
import httpx
from typing import List, Dict, Any
from backend.apis.base import BaseJobAPI, logger
from backend.config import env_settings
from backend.services.normalizer import DataNormalizer

class JoobleAPI(BaseJobAPI):
    source_name = "jooble"

    async def fetch_jobs(self, keyword: str, location: str = "US", limit: int = 50) -> List[Dict[str, Any]]:
        self.diagnostics["start_time"] = asyncio.get_event_loop().time()
        jobs = []

        if not env_settings.jooble_api_key:
            logger.warning("[jooble] API credentials missing, skipping.")
            return jobs

        url = f"https://jooble.org/api/{env_settings.jooble_api_key}"
        payload = {
            "keywords": keyword,
            "location": location,
            "page": 1,
            "resultonpage": limit
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()

            results = data.get("jobs", [])
            for res in results:
                company = res.get("company", "Unknown")
                location = res.get("location", "")
                title = res.get("title", "")
                desc = DataNormalizer.clean_html(res.get("snippet", ""))

                job = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "source": self.source_name,
                    "work_type": "Unknown",
                    "employment_type": "Unknown",
                    "description": desc,
                    "job_url": res.get("link", ""),
                    "scraped_at": None,
                    "raw_html": None
                }
                jobs.append(job)

            self.diagnostics["jobs_found"] += len(jobs)
        except Exception as e:
            self._record_error(e)
        finally:
            self.diagnostics["end_time"] = asyncio.get_event_loop().time()

        logger.info(f"[{self.source_name}] Found {len(jobs)} jobs for '{keyword}' in '{location}'")
        return jobs
