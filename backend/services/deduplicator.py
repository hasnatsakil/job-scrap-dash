from typing import List, Dict, Any, Set

class Deduplicator:
    def __init__(self, existing_jobs: List[Dict[str, Any]]):
        self.existing_urls: Set[str] = set()
        self.existing_signatures: Set[str] = set()
        for job in existing_jobs:
            url = job.get("job_url")
            if url: self.existing_urls.add(url.strip())
            company = job.get("company", "")
            title = job.get("title", "")
            if company and title:
                self.existing_signatures.add(f"{company.lower().strip()}::{title.lower().strip()}")

    def is_duplicate(self, job: Dict[str, Any]) -> bool:
        url = job.get("job_url", "").strip()
        if url and url in self.existing_urls: return True
        company = job.get("company", "").strip().lower()
        title = job.get("title", "").strip().lower()
        if company and title and f"{company}::{title}" in self.existing_signatures: return True
        return False
