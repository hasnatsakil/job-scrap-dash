import asyncio
import httpx
from typing import List, Dict, Any
from backend.apis.base import BaseJobAPI, logger
from backend.config import env_settings
from backend.services.normalizer import DataNormalizer

class MuseAPI(BaseJobAPI):
    source_name = "muse"

    async def fetch_jobs(self, keyword: str, location: str = "US", limit: int = 50) -> List[Dict[str, Any]]:
        self.diagnostics["start_time"] = asyncio.get_event_loop().time()
        jobs = []

        url = "https://www.themuse.com/api/public/jobs"
        params = {
            "category": keyword,
            "location": location,
            "page": 0,
        }
        
        if env_settings.muse_api_key:
            params["api_key"] = env_settings.muse_api_key

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()

            results = data.get("results", [])
            # If limit < len(results), trim it
            results = results[:limit]

            for res in results:
                company = res.get("company", {}).get("name", "Unknown")
                
                # Muse returns a list of locations
                locations = res.get("locations", [])
                location_str = ", ".join([loc.get("name", "") for loc in locations]) if locations else ""

                title = res.get("name", "")
                desc = DataNormalizer.clean_html(res.get("contents", ""))

                job = {
                    "title": title,
                    "company": company,
                    "location": location_str,
                    "source": self.source_name,
                    "work_type": "Unknown",
                    "employment_type": "Unknown",
                    "description": desc,
                    "job_url": res.get("refs", {}).get("landing_page", ""),
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
