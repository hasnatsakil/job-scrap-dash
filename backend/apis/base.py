from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseJobAPI:
    """
    Abstract base class for Job API providers.
    """
    source_name = "unknown"

    def __init__(self):
        self.diagnostics = {
            "jobs_found": 0,
            "start_time": 0,
            "end_time": 0,
            "errors": []
        }

    async def fetch_jobs(self, keyword: str, location: str = "US", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch jobs from the API matching the keyword.
        Must return a list of dictionaries that match the internal Job Model.
        """
        raise NotImplementedError("Subclasses must implement fetch_jobs()")

    def _record_error(self, e: Exception):
        logger.error(f"[{self.source_name}] Error: {e}")
        self.diagnostics["errors"].append(str(e))
