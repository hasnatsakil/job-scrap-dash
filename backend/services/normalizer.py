import re
from typing import Dict, Any

class DataNormalizer:
    @staticmethod
    def clean_html(raw_html: str) -> str:
        if not raw_html: return ""
        return ' '.join(re.sub('<.*?>', ' ', raw_html).split())

    @staticmethod
    def normalize_location(location: str) -> str:
        if not location: return "Unknown"
        loc = location.lower().strip()
        if "remote" in loc or "anywhere" in loc: return "Remote"
        return location.strip()

    @staticmethod
    def normalize_work_type(work_type: str, location: str) -> str:
        if not work_type:
            if location and "Remote" in location: return "Remote"
            return "Unknown"
        wt = work_type.lower()
        if "remote" in wt: return "Remote"
        if "hybrid" in wt: return "Hybrid"
        if "on-site" in wt or "onsite" in wt or "in-office" in wt: return "On-site"
        return work_type.strip().title()

    @staticmethod
    def normalize_employment_type(emp_type: str) -> str:
        if not emp_type: return "Full-time"
        et = emp_type.lower()
        if "full" in et and "time" in et: return "Full-time"
        if "part" in et and "time" in et: return "Part-time"
        if "contract" in et: return "Contract"
        if "intern" in et: return "Internship"
        return emp_type.strip().title()

    @classmethod
    def normalize_job(cls, job: Dict[str, Any]) -> Dict[str, Any]:
        job["description"] = cls.clean_html(job.get("description", ""))
        loc = cls.normalize_location(job.get("location", ""))
        job["location"] = loc
        job["work_type"] = cls.normalize_work_type(job.get("work_type", ""), loc)
        job["employment_type"] = cls.normalize_employment_type(job.get("employment_type", ""))
        return job
