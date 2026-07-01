import asyncio
import httpx
from typing import List, Dict, Any
from backend.apis.base import BaseJobAPI, logger
from backend.config import env_settings
from backend.services.normalizer import DataNormalizer

class AdzunaAPI(BaseJobAPI):
    source_name = "adzuna"

    async def fetch_jobs(self, keyword: str, location: str = "US", limit: int = 50) -> List[Dict[str, Any]]:
        self.diagnostics["start_time"] = asyncio.get_event_loop().time()
        jobs = []

        if not env_settings.adzuna_app_id or not env_settings.adzuna_app_key:
            logger.warning("[adzuna] API credentials missing, skipping.")
            return jobs

        url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
        params = {
            "app_id": env_settings.adzuna_app_id,
            "app_key": env_settings.adzuna_app_key,
            "results_per_page": limit,
            "what": keyword,
            "where": location
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()

            results = data.get("results", [])
            for res in results:
                company = res.get("company", {}).get("display_name", "Unknown")
                location = ",".join(res.get("location", {}).get("area", []))
                title = res.get("title", "")
                
                # Use clean_html to sanitize
                desc = DataNormalizer.clean_html(res.get("description", ""))

                job = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "source": self.source_name,
                    "work_type": "Unknown",
                    "employment_type": "Unknown",
                    "description": desc,
                    "job_url": res.get("redirect_url", ""),
                    "scraped_at": None,
                    "raw_html": None # Ensure this is cleared
                }
                jobs.append(job)

            self.diagnostics["jobs_found"] += len(jobs)
        except Exception as e:
            self._record_error(e)
        finally:
            self.diagnostics["end_time"] = asyncio.get_event_loop().time()

        logger.info(f"[{self.source_name}] Found {len(jobs)} jobs for '{keyword}' in '{location}'")
        return jobs
